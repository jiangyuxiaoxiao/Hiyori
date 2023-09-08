"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:48
@Desc: 商店功能汇总
@Ver : 1.0.0
"""
import re

from nonebot import on_regex
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, Bot
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from nonebot.log import logger

from Hiyori.Utils.Shop import Shops
from Hiyori.Plugins.Basic_plugins.nonebot_plugin_htmlrender import html_to_pic
from Hiyori.Utils.Message.At import GetAtQQs, clearAt
from Hiyori.Utils.Database import DB_Item
from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.Exception.Market import MarketException

from .api import info

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
        # 无法主动打开匿名商店
        if check_shop.anonymous:
            msg = MessageSegment.at(event.user_id) + "查询的商店名不存在哦"
            await checkShop.send(msg)
            return
        shopContent = Template
        if check_shop.name == "妃爱":
            name = "妃爱商店"
            shopContent = shopContent.replace("【商店名】", name)
        else:
            shopContent = shopContent.replace("【商店名】", check_shop.name + "商店")
        shopContent = shopContent.replace("【描述】", check_shop.description)
        itemContent = ""
        for item in check_shop.items.values():
            if item.anonymous:
                continue  # 不显示匿名商品
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
            if shop.anonymous:
                continue
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
async def _(matcher: Matcher, state: T_State, bot: Bot, event: MessageEvent):
    message = str(event.message)
    targets = GetAtQQs(message=message)  # 目标对象
    message = message.replace("#购买物品", "", 1).lstrip()
    message = message.replace("#购买商品", "", 1).lstrip()
    message = clearAt(message).strip()
    messages = message.split(" ")
    if len(messages) == 1:
        itemName = messages[0]
        itemNumber = "1"
    elif len(messages) >= 2:
        itemName = messages[0]
        itemNumber = messages[1]
    else:
        message = MessageSegment.at(event.user_id) + "请输入商品名哦"
        await buy.send(message)
        return
    # 逻辑检查——商品不存在
    if itemName not in Shops.items.keys():
        message = MessageSegment.at(event.user_id) + "要购买的商品不存在哦"
        await buy.send(message)
        return

    else:
        item = Shops.items[itemName]
        # 逻辑检查——商品数量合法
        if not itemNumber.isdigit():
            message = MessageSegment.at(event.user_id) + "物品数量不是正整数哦"
            await buy.send(message)
            return
        itemNumber = int(itemNumber)
        if itemNumber <= 0:
            message = MessageSegment.at(event.user_id) + "物品使用数量需大于0"
            await buy.send(message)
            return
        # 购买执行流程
        try:
            # 执行 购买前阶段
            await item.beforePurchase(QQ=event.user_id, Targets=targets, Num=itemNumber, bot=bot, event=event, matcher=matcher, state=state)
            # 执行 购买阶段
            await item.purchase(QQ=event.user_id, Targets=targets, Num=itemNumber, bot=bot, event=event, matcher=matcher, state=state)
            # 执行 购买后阶段
            await item.afterPurchase(QQ=event.user_id, Targets=targets, Num=itemNumber, bot=bot, event=event, matcher=matcher, state=state)
        except MarketException as e:
            # 打印异常
            logger.debug(str(e))


@use.handle()
async def _(matcher: Matcher, state: T_State, bot: Bot, event: MessageEvent):
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
    targets = GetAtQQs(message=message)  # 目标对象
    message = clearAt(message).strip()
    messages = message.split(" ")
    if len(messages) == 1:
        itemName = messages[0]
        itemNumber = "1"
    elif len(messages) >= 2:
        itemName = messages[0]
        itemNumber = messages[1]
    else:
        message = MessageSegment.at(event.user_id) + "请输入商品名哦"
        await buy.send(message)
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
            message = MessageSegment.at(event.user_id) + "物品数量不是正整数哦"
            await use.send(message)
            return
        itemNumber = int(itemNumber)
        if itemNumber <= 0:
            message = MessageSegment.at(event.user_id) + "物品使用数量需大于0"
            await use.send(message)
            return
        # 使用执行流程
        try:
            # 执行 使用前阶段
            await item.beforeUse(QQ=event.user_id, Targets=targets, Num=itemNumber, bot=bot, event=event, matcher=matcher, state=state)
            # 执行 使用阶段
            await item.use(QQ=event.user_id, Targets=targets, Num=itemNumber, bot=bot, event=event, matcher=matcher, state=state)
            # 执行 使用后阶段
            await item.afterUse(QQ=event.user_id, Targets=targets, Num=itemNumber, bot=bot, event=event, matcher=matcher, state=state)
        except MarketException as e:
            logger.debug(str(e))
