"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/1-0:02
@Desc: 现货市场
@Ver : 1.0.0
"""
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot import on_regex
from nonebot.plugin import PluginMetadata
from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.Spider.SpotPrice import *
from Hiyori.Utils.Permissions import HIYORI_OWNER
from Hiyori.Utils.Database import DB_User, DB_Spot
from Hiyori.Plugins.Basic_plugins.nonebot_plugin_htmlrender import md_to_pic, html_to_pic
import decimal
import datetime

__plugin_meta__ = PluginMetadata(
    name="现货市场",  # 用于在菜单显示 用于插件开关
    description="可以用妃爱币买卖现货市场的物品。测试中。",  # 用于在菜单中描述
    usage="#金价 或 #银价\n"
          "#查看现货市场 或 #现货市场\n"
          "#买入 黄金/白银 数量 【买入 单位为g】\n"
          "#卖出 黄金/白银 数量/全部 【卖出 单位为g】\n"
          "#查看现货仓库 或 现货仓库 【查看自己的现货仓库】\n"
          "#清空xxx交易历史 【清空对应品种现货交易历史，若xxx为全部则清空所有历史】",
    extra={"CD_Weight": 1,  # 调用插件CD权重 不填的话不会触发权重插件
           "Group": "Daily",
           "version": "1.0",
           "Keep_On": False,
           "Type": "Normal_Plugin",
           }
)

Gold = on_regex("^#金价$", priority=Priority.普通优先级)
Silver = on_regex("^#银价$", priority=Priority.普通优先级)
Palladium = on_regex("^#钯价$", priority=Priority.普通优先级)
Platinum = on_regex("^#铂价$", priority=Priority.普通优先级)
Market = on_regex("^#(查看)?现货市场$", priority=Priority.普通优先级)
Buy = on_regex("^#买入", priority=Priority.普通优先级)
Sell = on_regex("^#卖出", priority=Priority.普通优先级)
Check = on_regex("^#(查看)?现货仓库$", priority=Priority.普通优先级)
DeleteHistory = on_regex(r"^#清空.*交易历史$", priority=Priority.普通优先级)

SpotHtml = "./Data/Shop/Template/Spot.html"


@Gold.handle()
async def _(event: MessageEvent):
    info = await getGoldInfo()
    msg = MessageSegment.image(info["head_image"])
    msg = msg + MessageSegment.image(info["image"])
    await Gold.send(msg)


@Silver.handle()
async def _(event: MessageEvent):
    info = await getSilverInfo()
    msg = MessageSegment.image(info["head_image"])
    msg = msg + MessageSegment.image(info["image"])
    await Silver.send(msg)


@Market.handle()
async def _(event: MessageEvent):
    info = await getGoldInfo()
    msg = MessageSegment.image(info["head_image"])
    msg += MessageSegment.image(info["image"])
    info = await getSilverInfo()
    msg += MessageSegment.image(info["head_image"])
    msg += MessageSegment.image(info["image"])
    info = await getPlatinumInfo()
    msg += MessageSegment.image(info["head_image"])
    msg += MessageSegment.image(info["image"])
    info = await getPalladiumInfo()
    msg += MessageSegment.image(info["head_image"])
    msg += MessageSegment.image(info["image"])
    await Market.send(msg)


@Buy.handle()
async def _(event: MessageEvent):
    message = str(event.message)
    msg = MessageSegment.at(event.user_id)
    messages = message.split(" ")
    if len(messages) != 3:
        msg += "指令输入格式错误哦。"
        await Buy.send(msg)
        return
    SpotName = messages[1]
    if not messages[2].isdigit():
        msg += "指令输入格式错误哦。"
        await Buy.send(msg)
        return
    SpotNum = int(messages[2])
    if SpotNum <= 0:
        msg += "买入数量必须大于0哦。"
        await Buy.send(msg)
        return
    if SpotName not in ["黄金", "白银", "钯金", "铂金"]:
        msg += "想买入的现货不存在哦。"
        await Buy.send(msg)
        return

    Time = datetime.datetime.now()
    DayStr = f"{Time:%Y-%m-%d %H:%M:%S} "
    match SpotName:
        case "黄金":
            info = await getGoldInfo()
        case "白银":
            info = await getSilverInfo()
        case "铂金":
            info = await getPlatinumInfo()
        case "钯金":
            info = await getPalladiumInfo()
        case _:
            msg += "想买的现货不存在哦。"
            await Buy.send(msg)
            return

    if not info["OK"]:
        msg += "获取价格出错，交易失败。"
        await Buy.send(msg)
        return
    price = float(info["price"])
    if not DB_User.spendMoney(event.user_id, price * SpotNum):
        msg += "当前妃爱币不足，交易失败。"
        await Buy.send(msg)
        return
    Spot = DB_Spot.getUserSpot(event.user_id, SpotName)
    Spot.Quantity += SpotNum
    Spot.History += DayStr + f"【买入】{SpotName}{SpotNum}克。 买入价{price}妃爱币/克\n"
    Spot.save()
    user = DB_User.getUser(QQ=event.user_id)
    money = int(user.Money/100)
    msg += f"交易成功，本次交易以{price}妃爱币/克的价格购入{SpotName}{SpotNum}克。当前余额{money}妃爱币。\n\n"
    msg += f"交易历史记录如下（使用指令#清空{SpotName}交易历史删除历史记录）：\n"
    historys = Spot.History.split("\n")
    md = f"##{SpotName}交易历史记录   \n" \
         "---   \n"
    for history in historys:
        if history != "":
            md += f"+ {history}   \n"
    image = await md_to_pic(md=md, width=800)
    msg += MessageSegment.image(image)
    await Buy.send(msg)


@Sell.handle()
async def _(event: MessageEvent):
    message = str(event.message)
    msg = MessageSegment.at(event.user_id)
    messages = message.split(" ")
    if len(messages) != 3:
        msg += "指令输入格式错误哦。"
        await Sell.send(msg)
        return
    SpotName = messages[1]
    Spot = DB_Spot.getUserSpot(event.user_id, SpotName)
    if messages[2] == "全部":
        SpotNum = Spot.Quantity
    elif not messages[2].isdigit():
        msg += "指令输入格式错误哦。"
        await Sell.send(msg)
        return
    else:
        SpotNum = int(messages[2])
    if SpotNum <= 0:
        msg += "卖出数量必须大于0哦。"
        await Sell.send(msg)
        return
    if SpotName not in ["黄金", "白银", "钯金", "铂金"]:
        msg += "想卖出的现货不存在哦。"
        await Sell.send(msg)
        return

    Time = datetime.datetime.now()
    DayStr = f"{Time:%Y-%m-%d %H:%M:%S} "
    match SpotName:
        case "黄金":
            info = await getGoldInfo()
        case "白银":
            info = await getSilverInfo()
        case "铂金":
            info = await getPlatinumInfo()
        case "钯金":
            info = await getPalladiumInfo()
        case _:
            msg += "想卖出的现货不存在哦。"
            await Sell.send(msg)
            return

    if not info["OK"]:
        msg += "获取价格出错，交易失败。"
        await Sell.send(msg)
        return
    price = float(info["price"])
    if Spot.Quantity < SpotNum:
        msg += "你的现货不足。"
        await Sell.send(msg)
        return
    else:
        Spot.Quantity -= SpotNum
        Spot.History += DayStr + f"【卖出】{SpotName}{SpotNum}克。 卖出价{price}妃爱币/克\n"
        Spot.save()
        DB_User.spendMoney(event.user_id, -price * SpotNum)
        user = DB_User.getUser(QQ=event.user_id)
        money = int(user.Money / 100)
        msg += f"交易成功，本次交易以{price}妃爱币/克的价格卖出{SpotName}{SpotNum}克。当前余额{money}妃爱币。\n\n"
        msg += f"交易历史记录如下（使用指令#清空{SpotName}交易历史删除历史记录）：\n"
        historys = Spot.History.split("\n")
        md = f"##{SpotName}交易历史记录   \n" \
             "---   \n"
        for history in historys:
            if history != "":
                md += f"+ {history}   \n"
        image = await md_to_pic(md=md, width=800)
        msg += MessageSegment.image(image)
        await Buy.send(msg)


@Check.handle()
async def _(event: MessageEvent):
    with open(SpotHtml, "r", encoding="utf-8") as file:
        html = file.read()
    infos = DB_Spot.getUserSpotALL(QQ=event.user_id)
    content = ""
    for info in infos:
        history = info.History.replace("\n", "<br>")
        content += f"<tr>" \
                   f"<td>{info.SpotName}</td>" \
                   f"<td>{info.Quantity}克</td>" \
                   f"<td>{history}</td>" \
                   f"</tr><tr></tr>"
    html = html.replace("spots", content)
    image = await html_to_pic(html=html, type="png", viewport={"width": 2160, "height": 10})
    msg = MessageSegment.image(image)
    await Check.send(msg)


@DeleteHistory.handle()
async def _(event: MessageEvent):
    message = str(event.message)
    message = message.replace("#清空", "")
    message = message.replace("交易历史", "").strip()
    msg = MessageSegment.at(event.user_id)
    if message == "全部":
        Spots = DB_Spot.getUserSpotALL(QQ=event.user_id)
        for spot in Spots:
            spot.History = ""
            spot.save()
        msg += "交易历史已全部清空"
        await DeleteHistory.send(msg)
        return
    else:
        if message not in ["黄金", "白银", "铂金", "钯金"]:
            msg += "现货名不存在哦"
            await DeleteHistory.send(msg)
            return
        Spot = DB_Spot.getUserSpot(QQ=event.user_id, SpotName=message)
        Spot.History = ""
        Spot.save()
        msg += f"{message}交易历史已清空。"
        await DeleteHistory.send(msg)
        return
