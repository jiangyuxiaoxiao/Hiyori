"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:48
@Desc: 商店功能汇总
@Ver : 1.0.0
"""
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, Bot
from nonebot.plugin import PluginMetadata
from Hiyori.Utils.Shop import Shops, Shop
from Hiyori.Utils.Shop.BasicFunction import 折扣系数计算
from Hiyori.Plugins.Basic_plugins.nonebot_plugin_htmlrender import html_to_pic
from Hiyori.Utils.Database import DB_Item, DB_User
from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.API.QQ import GetQQGrouperName, GetQQStrangerName
import re

__plugin_meta__ = PluginMetadata(
    name="商店",  # 用于在菜单显示 用于插件开关
    description="妃爱大商店！",  # 用于在菜单中描述
    usage="#我的背包/查看背包 【查看背包】\n"
          "#查看商店 【查看所有商店商品列表】\n"
          "#查看xxx商店 【查看xxx商店商品列表】\n"
          "#购买物品 商品名 商品数量 【购买对应商品】\n"
          "#使用物品 物品名 物品数量 【使用对应物品】\n"
          "#使用物品 物品名 物品数量 @使用对象【对指定对象使用对应物品】\n"
          "#查看 【查看当前妃爱币等信息】",
    extra={"CD_Weight": 1,  # 调用插件CD权重 不填的话不会触发权重插件
           "Group": "Daily",
           "version": "1.0",
           "Keep_On": False,
           "Type": "Normal_Plugin",
           }
)

myItems = on_regex("(^#我的背包$)|(^#查看背包$)", priority=Priority.普通优先级, block=False)
checkShop = on_regex(r"^#(查看)?[\s\S]*商店$", priority=Priority.普通优先级, block=False)
buy = on_regex(r"(^#购买物品)|(^#购买商品)", priority=Priority.普通优先级, block=False)
use = on_regex(r"(^#使用物品)|(^#使用商品)", priority=Priority.普通优先级, block=False)

BackPackHtml = "./Data/Shop/Template/BackPack.html"
ShopHtml = "./Data/Shop/Template/Shop.html"

Template = "<p style=\"text-align: center; font-size: 70px; line-height: 0\">【商店名】</p>" \
           "<p style=\"text-align: center; font-size: 35px; line-height: 35px\">【描述】</p>" \
           "<table style=\"word-break:break-all; table-layout: fixed;\">" \
           "<thead>" \
           "<tr>" \
           "<th width=\"20%\">物品</th>" \
           "<th width=\"15%\">好感度</th>" \
           "<th width=\"15%\">价格</th>" \
           "<th width=\"50%\">描述</th>" \
           "</tr>" \
           "</thead>" \
           "【商品栏】" \
           "</table>"


@myItems.handle()
async def _(event: MessageEvent):
    QQ = event.user_id
    items = DB_Item.getUserItemALL(QQ=QQ)
    with open(BackPackHtml, "r", encoding="utf-8") as file:
        html = file.read()
    content = ""
    for item in items:
        if str(item.Item) not in Shops.items.keys():
            description = ""
        else:
            description = Shops.items[str(item.Item)].description
        if item.Decimal == 0:
            quantity = int(item.Quantity)
        else:
            quantity = round(item.Quantity / (10 ** item.Decimal), item.Decimal)
        if quantity == 0:
            continue
        content += f"<tr>" \
                   f"<td>{item.Item}</td>" \
                   f"<td>{quantity}</td>" \
                   f"<td>{description}</td>" \
                   f"</tr><tr></tr>"
    html = html.replace("items", content)
    pic = await html_to_pic(html=html, type="png", viewport={"width": 1200, "height": 10})
    message = MessageSegment.image(pic)
    await myItems.send(message)


@checkShop.handle()
async def _(event: MessageEvent):
    message = str(event.message)
    message = re.sub(pattern=r"^#(查看)?", repl="", string=message)
    shopName = re.sub(pattern=r"商店$", repl="", string=message)
    with open(ShopHtml, "r", encoding="utf-8") as file:
        html = file.read()
    # 检查商店是否存在
    if shopName != "":
        if shopName not in Shops.shops.keys():
            msg = MessageSegment.at(event.user_id) + "查询的商店名不存在哦"
            await checkShop.send(msg)
            return
        check_shop = Shops.shops[shopName]
        shopContent = Template
        if check_shop.name == "妃爱":
            name = "妃爱商店"
            shopContent = shopContent.replace("【商店名】", name)
        else:
            shopContent = shopContent.replace("【商店名】", check_shop.name + "商店")
        shopContent = shopContent.replace("【描述】", check_shop.description)
        itemContent = ""
        for item in check_shop.items.values():
            itemContent += f"<tr>" \
                           f"<td>{item.name}</td>" \
                           f"<td>{item.need_attitude}</td>" \
                           f"<td>{item.price}</td>" \
                           f"<td>{item.description}</td>" \
                           f"</tr><tr></tr>"
        shopContent = shopContent.replace("【商品栏】", itemContent)
        htmlMsg = html.replace("【content】", shopContent)
        pic = await html_to_pic(html=htmlMsg, type="png", viewport={"width": 1200, "height": 10})
        message = MessageSegment.image(pic)
        await checkShop.send(message)
        return
    else:
        # 所有商店
        AllShopContent = ""
        for shop in Shops.shops.values():
            shopContent = Template
            shopContent = shopContent.replace("【商店名】", shop.name)
            shopContent = shopContent.replace("【描述】", shop.description)
            itemContent = ""
            for item in shop.items.values():
                itemContent += f"<tr>" \
                               f"<td>{item.name}</td>" \
                               f"<td>{item.need_attitude}</td>" \
                               f"<td>{item.price}</td>" \
                               f"<td>{item.description}</td>" \
                               f"</tr><tr></tr>"
            shopContent = shopContent.replace("【商品栏】", itemContent)
            AllShopContent += shopContent
        htmlMsg = html.replace("【content】", AllShopContent)
        # 打印
        pic = await html_to_pic(html=htmlMsg, type="png", viewport={"width": 1200, "height": 10})
        message = MessageSegment.image(pic)
        await checkShop.send(message)
        return


@buy.handle()
async def _(bot: Bot, event: MessageEvent):
    message = str(event.message)
    message = message.replace("#购买物品", "", 1).lstrip()
    message = message.replace("#购买商品", "", 1).lstrip()
    messages = message.split(" ")
    if len(messages) == 1:
        itemName = messages[0]
        itemNumber = "1"
    elif len(messages) == 2:
        itemName = messages[0]
        itemNumber = messages[1]
    else:
        message = MessageSegment.at(event.user_id) + "妃爱没懂你的意思，是不是输入格式错了？"
        await buy.send(message)
        return
    # 逻辑检查——商品不存在
    if itemName not in Shops.items.keys():
        message = MessageSegment.at(event.user_id) + "要购买的商品不存在哦"
        await buy.send(message)
        return

    else:
        折扣系数 = 折扣系数计算(QQ=event.user_id, ItemName=itemName)
        item = Shops.items[itemName]
        # 逻辑检查——商品数量合法
        if not itemNumber.isdigit():
            message = MessageSegment.at(event.user_id) + "妃爱没懂你的意思，是不是输入格式错了？"
            await buy.send(message)
            return
        itemNumber = int(itemNumber)
        if itemNumber <= 0:
            message = MessageSegment.at(event.user_id) + "妃爱没懂你的意思，是不是输入格式错了？"
            await buy.send(message)
            return
        # 逻辑检查——好感度不足
        User = DB_User.getUser(QQ=event.user_id)
        if User.Attitude < item.need_attitude:
            message = MessageSegment.at(event.user_id) + f"商品需要{item.need_attitude}好感度，你的好感度不足哟"
            await buy.send(message)
            return
        # 逻辑检查——余额不足
        if not DB_User.spendMoney(QQ=event.user_id, Money=itemNumber * item.price * 折扣系数):
            message = MessageSegment.at(event.user_id) + "你的妃爱币不够啦"
            await buy.send(message)
            return
        else:
            dbItem = DB_Item.getUserItem(QQ=event.user_id, ItemName=itemName)
            # 执行购买前触发函数
            if "购买前触发函数" in item.Functions.keys():
                if hasattr(event, "group_id"):
                    GroupID = event.group_id
                else:
                    GroupID = 0
                flag, result = item.Functions["购买前触发函数"](QQ=event.user_id, GroupID=GroupID, Quantity=itemNumber,
                                                                ItemName=itemName)
                if not flag:
                    await buy.send(result)
                    # 返还余额
                    DB_User.spendMoney(QQ=event.user_id, Money=-itemNumber * item.price)
                    return
            dbItem.Quantity += itemNumber
            dbItem.save()
            user = DB_User.getUser(QQ=event.user_id)
            message = MessageSegment.at(event.user_id)
            message += f"成功购买{itemNumber}个{item.name}，当前余额{int(user.Money / 100)}妃爱币。"
            await buy.send(message)
            # 执行购买后触发函数
            if "购买后触发函数" in item.Functions.keys():
                if hasattr(event, "group_id"):
                    GroupID = event.group_id
                else:
                    GroupID = 0
                flag, result = await item.Functions["购买后触发函数"](QQ=event.user_id, GroupID=GroupID,
                                                                      Quantity=itemNumber, bot=bot)
                if result != "":
                    await buy.send(result)
            return


@use.handle()
async def _(bot: Bot, event: MessageEvent):
    # 功能调试
    """
    if event.user_id != 654163754:
        await use.send("使用物品功能升级中")
        return
    """
    message = str(event.message)
    message = message.replace("#使用物品", "", 1).lstrip()
    message = message.replace("#使用商品", "", 1).lstrip()
    # 获取函数使用对象
    targetMessage = re.search(pattern=r"\[CQ:at,qq=[0-9]+\]", string=message)
    target = 0
    if targetMessage:
        targetMessage = targetMessage.group()
        target = re.search(pattern=r"[0-9]+", string=targetMessage).group()
        target = int(target)
        # 去除@信息
        message = re.sub(pattern=r"\[CQ:at,qq=[0-9]+\]", repl="", string=message).strip()
    messages = message.split(" ")
    if len(messages) == 1:
        itemName = messages[0]
        itemNumber = "1"
    elif len(messages) == 2:
        itemName = messages[0]
        itemNumber = messages[1]
    else:
        message = MessageSegment.at(event.user_id) + "妃爱没懂你的意思，是不是输入格式错了？"
        await use.send(message)
        return
    # 逻辑检查——物品不存在
    if itemName not in Shops.items.keys():
        message = MessageSegment.at(event.user_id) + "要使用的物品不存在。"
        await use.send(message)
        return

    else:
        item = Shops.items[itemName]
        # 逻辑检查——物品数量合法
        if not itemNumber.isdigit():
            message = MessageSegment.at(event.user_id) + "妃爱没懂你的意思，是不是输入格式错了？"
            await use.send(message)
            return
        itemNumber = int(itemNumber)
        if itemNumber <= 0:
            message = MessageSegment.at(event.user_id) + "妃爱没懂你的意思，是不是输入格式错了？"
            await use.send(message)
            return
        # 逻辑检查——背包物品数量不足 或 背包物品数量不合法
        DBitem = DB_Item.getUserItem(QQ=event.user_id, ItemName=itemName)
        if DBitem.Decimal != 0:
            # 不允许使用带小数点的物品
            message = MessageSegment.at(event.user_id) + "物品无法使用~"
            await use.send(message)
            return
        if DBitem.Quantity < itemNumber:
            message = MessageSegment.at(event.user_id) + f"你的{itemName}数量不足哦。"
            await use.send(message)
            return
        # 逻辑检查——物品存在可调用的函数
        if "使用时触发函数" not in item.Functions.keys():
            message = MessageSegment.at(event.user_id) + "物品无法使用~"
            await use.send(message)
            return
        # 逻辑检查——指定使用对象的物品必须可以指定对象
        if target != 0:
            if not item.hasTarget:
                message = MessageSegment.at(event.user_id) + "该物品无法指定他人使用~"
                await use.send(message)
                return
        # 参数检查——群聊Q号
        if hasattr(event, "group_id"):
            GroupID = event.group_id
        else:
            GroupID = 0
        flag, result = item.Functions["使用时触发函数"](
            QQ=event.user_id, GroupID=GroupID, Quantity=itemNumber, **{"target": target, "bot": bot})
        # 返回结果处理
        if result == "":
            return
        # 预定义参数处理
        if "{UserName}" in result:
            if hasattr(event, "group_id"):
                UserName = await GetQQGrouperName(bot=bot, QQ=event.user_id, Group=event.group_id)
            else:
                UserName = await GetQQStrangerName(bot=bot, QQ=event.user_id)
            result = result.replace("{UserName}", UserName)
        if "{TargetName}" in result:
            # 群聊中
            if hasattr(event, "group_id"):
                UserName = await GetQQGrouperName(bot=bot, QQ=target, Group=event.group_id)
            else:
                UserName = await GetQQStrangerName(bot=bot, QQ=target)
            result = result.replace("{TargetName}", UserName)
        await use.send(result)
        return
