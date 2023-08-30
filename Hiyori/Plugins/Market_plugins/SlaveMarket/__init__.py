"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:50
@Desc: 群友市场插件
@Ver : 1.0.0
"""
import os.path
import datetime
import re

from nonebot import on_regex
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, Bot, MessageEvent
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata

from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.Database import DB_slave, DB_User
from Hiyori.Utils.Message.Forward_Message import Nodes
from Hiyori.Utils.API.QQ import GetQQGrouperName, GetQQStrangerName
from Hiyori.Plugins.Basic_plugins.nonebot_plugin_htmlrender import html_to_pic, md_to_pic
from Hiyori.Utils.Matcher import logPluginExecuteTime

from .config import SlaveConfig
from .skills import ExecuteSkill, Jobs
from .Utils import SlaveUtils, CartUtils
from .slaveShop import SlaveShopInit

__plugin_meta__ = PluginMetadata(
    name="群友市场",  # 用于在菜单显示 用于插件开关
    description="选购可爱的群友吧！",  # 用于在菜单中描述
    usage="查看群友市场帮助 【获取详细帮助信息】"
          "#查看群友市场\n 【查看当前群友市场】"
          "#购买群友@群友 或 #购买群友 QQ号\n"
          "#我的群友 【查看已拥有的群友以及自己】\n"
          "#一键打工 【派遣所有群友打工】\n"
          "#打工 【自己打工，每日限一次】\n"
          "#群友购物车 添加/删除群友 @群友/要删除的序号/QQ号 【购物车修改操作】\n"
          "#查看群友购物车"
          "#一键购买 【按购物车顺序对群友进行购买】\n",
    extra={"CD_Weight": 3,  # 调用插件CD权重 不填的话不会触发权重插件
           "Group": "Daily",
           "version": "1.0",
           "Keep_On": False,
           "Type": "Normal_Plugin",
           }
)

# 初始化相关
SlaveShopInit()

Help = on_regex("^#查看群友市场帮助$", priority=Priority.系统优先级, block=True)  # √
checkMarket = on_regex("(^#查看群友市场)|(^#查询群友市场)|(^#群友市场)", priority=Priority.普通优先级, block=False)  # √
buySlave = on_regex("^#购买群友", priority=Priority.普通优先级, block=True)
mySlave = on_regex("^#我的群友$", priority=Priority.普通优先级, block=False)  # √
Mission = on_regex("^#主人的任务", priority=Priority.普通优先级, block=True)  # √
AllWork = on_regex("^#一键打工$", priority=Priority.普通优先级, block=False)  # √
Work = on_regex("^#打工$", priority=Priority.普通优先级, block=False)  # √
AddCart = on_regex(r"^#群友购物车\s*添加群友", priority=Priority.普通优先级, block=True)
DeleteCart = on_regex(r"^#群友购物车\s*删除群友", priority=Priority.普通优先级, block=True)
CheckCart = on_regex(r"^#查看群友购物车$", priority=Priority.普通优先级, block=True)
BuyCart = on_regex("^#一键购买", priority=Priority.普通优先级, block=True)
Menu_HTML_Path = "./Data/SlaveMarket/Template/menu_百岁珊_1.html"
Menu_HTML_Path2 = "./Data/SlaveMarket/Template/menu_百岁珊_2.html"
Menu_HTML_Path3 = "./Data/SlaveMarket/Template/menu_百岁珊_3.html"
Menu_HTML_Path4 = "./Data/SlaveMarket/Template/购物车.html"


def removeUrl(s: str) -> str:
    s = re.sub(r"(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]", "", s)
    return s


@Help.handle()
async def _(event: MessageEvent):
    FileDir = os.path.dirname(os.path.abspath(__file__))
    menu = os.path.join(FileDir, "Menu", "menu_NormalUser.md")
    img = await md_to_pic(md_path=menu, width=1440)
    msg = MessageSegment.at(event.user_id) + MessageSegment.image(img)
    await Help.send(msg)


@checkMarket.handle()
@logPluginExecuteTime
async def _(matcher: Matcher, bot: Bot, event: GroupMessageEvent):
    message = str(event.message)
    message = re.sub(pattern=r"(^#查看群友市场)|(^#查询群友市场)|(^#群友市场)", repl="", string=message).strip()
    if message == "":
        mode = "价格降序"
    else:
        mode = message
    global Menu_HTML_Path
    with open(Menu_HTML_Path, "r", encoding="utf-8") as file:
        htmlStr = file.read()
    Slaves = DB_slave.getAllUsers(GroupID=event.group_id)
    # 规则排序
    match mode:
        case "价格降序":
            pass
        case "价格升序":
            Slaves = Slaves[::-1]
        case "颜值降序":
            Slaves = sorted(Slaves, key=lambda slave: SlaveUtils.获取现代世界观属性(slave)[0], reverse=True)
        case "颜值升序":
            Slaves = sorted(Slaves, key=lambda slave: SlaveUtils.获取现代世界观属性(slave)[0])
        case "智力降序":
            Slaves = sorted(Slaves, key=lambda slave: SlaveUtils.获取现代世界观属性(slave)[1], reverse=True)
        case "智力升序":
            Slaves = sorted(Slaves, key=lambda slave: SlaveUtils.获取现代世界观属性(slave)[1])
        case "体质降序":
            Slaves = sorted(Slaves, key=lambda slave: SlaveUtils.获取现代世界观属性(slave)[2], reverse=True)
        case "体质升序":
            Slaves = sorted(Slaves, key=lambda slave: SlaveUtils.获取现代世界观属性(slave)[2])
        case _:
            pass
    count = 0
    htmls = []
    content = ""
    CoupleMap = {}  # 用于记录已存在的Couple
    for Slave in Slaves:
        if Slave.Owner != 0:
            if count == 100:
                # 现在只显示前一百条
                # count = 0
                # htmls.append(htmlStr.replace("SlaveInfo", content))
                # content = ""
                break
            # 已在之前的结婚对象中显示则不再显示
            if Slave.QQ in CoupleMap.keys():
                continue
            Couple = SlaveUtils.结婚对象(Slave)
            try:
                SlaveName = await GetQQGrouperName(bot=bot, QQ=Slave.QQ, Group=event.group_id)
                OwnerName = await GetQQGrouperName(bot=bot, QQ=Slave.Owner, Group=event.group_id)
            except Exception:
                continue
            SlaveImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={Slave.QQ}&s=100"
            OwnerImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={Slave.Owner}&s=100"
            SlaveName = removeUrl(SlaveName)
            OwnerName = removeUrl(OwnerName)
            SlaveExtraInfo = SlaveUtils.PrintPersonInfo(slave=Slave)
            # 当存在结婚对象时的打印情况
            # 注意，此处会记录对象，并且不再打印第二次
            if Couple != 0:
                CoupleMap[Couple] = True
                try:
                    CoupleName = await GetQQGrouperName(bot=bot, QQ=Couple, Group=event.group_id)
                except Exception:
                    try:
                        CoupleName = await GetQQStrangerName(bot=bot, QQ=Couple)
                    except Exception:
                        CoupleName = ""
                CoupleImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={Couple}&s=100"
                CoupleName = removeUrl(CoupleName)
                CoupleSlave = DB_slave.getUser(QQ=Couple, GroupID=event.group_id)
                CoupleExtraInfo = SlaveUtils.PrintPersonInfo(slave=CoupleSlave)
                content = content + f"<tr><td>" \
                                    f"<img src={SlaveImageUrl} width=\"70px\"  height=\"70px\" alt=\"\">" \
                                    f"<img src={CoupleImageUrl} width=\"70px\" height=\"70px\" alt=\"\">" \
                                    f"<br>{SlaveName} & {CoupleName}</td>" \
                                    f"<td>{Slave.Price + CoupleSlave.Price}</td>" \
                                    f"<td><img src={OwnerImageUrl} alt=\"\"> <br> {OwnerName}</td>" \
                                    f"<td>{SlaveExtraInfo} <br> {CoupleExtraInfo}</td>" \
                                    f"<td>{Slave.QQ} <br> {Couple}</td>" \
                                    f"</tr><tr></tr>"
            # 不存在时的打印情况
            else:
                content = content + f"<tr><td><img src={SlaveImageUrl} alt=\"\"> <br> {SlaveName}</td>" \
                                    f"<td>{Slave.Price}</td>" \
                                    f"<td><img src={OwnerImageUrl} alt=\"\"> <br> {OwnerName}</td>" \
                                    f"<td>{SlaveExtraInfo}</td>" \
                                    f"<td>{Slave.QQ}</td>" \
                                    f"</tr><tr></tr>"
            count = count + 1
    htmls.append(htmlStr.replace("SlaveInfo", content))
    message = ""
    for html in htmls:
        pic = await html_to_pic(html=html, type="png", viewport={"width": 1440, "height": 2560})
        message = message + MessageSegment.image(pic)
    await matcher.send(message)


@buySlave.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    # 检查今日购买次数是否到达上限
    新主人_奴隶表数据 = DB_slave.getUser(QQ=event.user_id, GroupID=event.group_id)
    Today = datetime.datetime.now()
    TodayStr = str(Today.year) + "-" + str(Today.month) + "-" + str(Today.day)
    # 最后购买日期为本日
    if TodayStr == 新主人_奴隶表数据.LastPurchase:
        if 新主人_奴隶表数据.PurchaseTime >= SlaveConfig.MaxDailyPurchase:
            message = MessageSegment.at(user_id=event.user_id) + MessageSegment.text("你今天的购买次数已经到上限了哦~")
            await buySlave.send(message)
            return
    else:
        新主人_奴隶表数据.PurchaseTime = 0
    message = str(event.message)
    message = message.replace("#购买群友", "").strip()
    message = message.replace("[CQ:at,qq=", "")
    message = message.replace("]", "").strip()
    if message == "":
        奴隶QQ = event.self_id
    elif not message.isdigit():
        await buySlave.send("没有找到该群友>_<")
        return
    else:
        奴隶QQ = int(message)
    奴隶_奴隶表数据 = DB_slave.getUser(QQ=奴隶QQ, GroupID=event.group_id)
    # 检查是否可买 同时，若群友存在夫妻，则夫妻不可买的话群友亦不可买
    flag, result = SlaveUtils.项圈状态(QQ=奴隶QQ, GroupID=event.group_id)
    if flag:
        await buySlave.send(f"当前群友截止{result}前暂时不可购买哦")
        return
    奴隶老婆QQ = SlaveUtils.结婚对象(slave=奴隶_奴隶表数据)
    if 奴隶老婆QQ != 0:
        奴隶老婆_奴隶表数据 = DB_slave.getUser(QQ=奴隶老婆QQ, GroupID=event.group_id)
        flag, result = SlaveUtils.项圈状态(QQ=奴隶老婆QQ, GroupID=event.group_id)
        if flag:
            await buySlave.send(f"当前群友截止{result}前暂时不可购买哦")
            return
    # 检查逻辑——不能自己买自己
    if 奴隶QQ == event.user_id:
        await buySlave.send("不能自己购买自己哦~")
        return
    # 检查逻辑——不能买自己老婆
    if 奴隶QQ == SlaveUtils.结婚对象(slave=新主人_奴隶表数据):
        await buySlave.send("不能购买自己老婆哦~")
        return
    # 检查逻辑——不能购买已有奴隶
    if 奴隶_奴隶表数据.Owner == event.user_id:
        await buySlave.send("不能购买自己已有的群友哦~")
        return
    # 检查逻辑——奴隶为本群成员
    try:
        SlaveName = await GetQQGrouperName(bot=bot, QQ=奴隶QQ, Group=event.group_id)

        NewOwnerName = await GetQQGrouperName(bot=bot, QQ=event.user_id, Group=event.group_id)
    except Exception:
        await buySlave.send("只能购买群内的群友哦~")
        return
    # 检查逻辑——金币充足
    if 奴隶老婆QQ != 0:
        奴隶老婆_奴隶表数据 = DB_slave.getUser(QQ=奴隶老婆QQ, GroupID=event.group_id)
        if not DB_User.spendMoney(QQ=event.user_id, Money=奴隶_奴隶表数据.Price + 奴隶老婆_奴隶表数据.Price):
            await buySlave.send("你的妃爱币不够哦")
            return
    elif not DB_User.spendMoney(QQ=event.user_id, Money=奴隶_奴隶表数据.Price):
        await buySlave.send("你的妃爱币不够哦")
        return

    原主人QQ = 奴隶_奴隶表数据.Owner
    # 头像相关
    SlaveImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={奴隶QQ}&s=100"
    SlaveCoupleImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={奴隶老婆QQ}&s=100"
    OldOwnerImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={原主人QQ}&s=100"
    NewOwnerImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={event.user_id}&s=100"
    # html模板
    with open(Menu_HTML_Path3, "r", encoding="utf-8") as file:
        htmlStr = file.read()
    奴隶_用户表数据 = DB_User.getUser(QQ=奴隶_奴隶表数据.QQ)
    # 无主情况
    if 原主人QQ == 0:
        # 奴隶转让 新主人更新
        新主人_奴隶表数据.PurchaseTime = 新主人_奴隶表数据.PurchaseTime + 1
        新主人_奴隶表数据.LastPurchase = TodayStr
        新主人_奴隶表数据.save()
        新主人_用户表数据 = DB_User.getUser(event.user_id)
        # 奴隶获得金币 奴隶更新
        if 奴隶老婆QQ != 0:
            # 获取老婆用户表数据
            奴隶老婆_用户表数据 = DB_User.getUser(QQ=奴隶老婆QQ)
            奴隶老婆_奴隶表数据 = DB_slave.getUser(QQ=奴隶老婆QQ, GroupID=event.group_id)
            try:
                SlaveCoupleName = await GetQQGrouperName(bot=bot, QQ=奴隶老婆QQ, Group=event.group_id)
            except Exception:
                SlaveCoupleName = ""
            # 更新，两人收入叠加
            奴隶收入 = 奴隶_奴隶表数据.Price + 奴隶老婆_奴隶表数据.Price
            奴隶_用户表数据.Money = int(奴隶_用户表数据.Money + 奴隶收入 * 100)
            奴隶老婆_用户表数据.Money = int(奴隶老婆_用户表数据.Money + 奴隶收入 * 100)
            DB_User.updateUser(奴隶_用户表数据)
            DB_User.updateUser(奴隶老婆_用户表数据)
            # 奴隶转让 奴隶更新
            奴隶_奴隶表数据.Price += SlaveConfig.AddPrice
            奴隶老婆_奴隶表数据.Price += SlaveConfig.AddPrice
            奴隶_奴隶表数据.Owner = event.user_id
            奴隶老婆_奴隶表数据.Owner = event.user_id
            奴隶_奴隶表数据.save()
            奴隶老婆_奴隶表数据.save()
            content = f"<tr><td>" \
                      f"<img src={SlaveImageUrl} alt=\"\">" \
                      f"<img src={SlaveCoupleImageUrl} alt=\"\">" \
                      f"<br>{SlaveName} & {SlaveCoupleName}</td>" \
                      f"<td></td>" \
                      f"<td><img src={NewOwnerImageUrl} alt=\"\"> <br> {NewOwnerName}</td>" \
                      f"</tr><tr></tr>" \
                      f"<tr>" \
                      f"<td>收入{奴隶收入}&{奴隶收入}妃爱币</td>" \
                      f"<td></td>" \
                      f"<td>花费{奴隶_奴隶表数据.Price + 奴隶老婆_奴隶表数据.Price - SlaveConfig.AddPrice * 2}妃爱币</td>" \
                      f"</tr><tr></tr>" \
                      f"<tr>" \
                      f"<td>现持有{奴隶_用户表数据.Money / 100}&{奴隶老婆_用户表数据.Money / 100}妃爱币</td>" \
                      f"<td></td>" \
                      f"<td>现持有{新主人_用户表数据.Money / 100}妃爱币</td>" \
                      f"</tr><tr></tr>" \
                      f"<tr>" \
                      f"<td>身价{奴隶_奴隶表数据.Price - SlaveConfig.AddPrice} → {奴隶_奴隶表数据.Price}<br>" \
                      f"身价{奴隶老婆_奴隶表数据.Price - SlaveConfig.AddPrice} → {奴隶老婆_奴隶表数据.Price}" \
                      f"</td>" \
                      f"<td></td>" \
                      f"<td></td>" \
                      f"</tr>"
        else:
            奴隶收入 = 奴隶_奴隶表数据.Price
            奴隶_用户表数据.Money = int(奴隶_用户表数据.Money + 奴隶收入 * 100)
            DB_User.updateUser(奴隶_用户表数据)
            # 奴隶转让 奴隶更新
            奴隶_奴隶表数据.Price += SlaveConfig.AddPrice
            奴隶_奴隶表数据.Owner = event.user_id
            奴隶_奴隶表数据.save()
            content = f"<tr>" \
                      f"<td><img src={SlaveImageUrl} alt=\"\"> <br> {SlaveName}</td>" \
                      f"<td></td>" \
                      f"<td><img src={NewOwnerImageUrl} alt=\"\"> <br> {NewOwnerName}</td>" \
                      f"</tr><tr></tr>" \
                      f"<tr>" \
                      f"<td>收入{奴隶收入}妃爱币</td>" \
                      f"<td></td>" \
                      f"<td>花费{奴隶_奴隶表数据.Price - SlaveConfig.AddPrice}妃爱币</td>" \
                      f"</tr><tr></tr>" \
                      f"<tr>" \
                      f"<td>现持有{奴隶_用户表数据.Money / 100}妃爱币</td>" \
                      f"<td></td>" \
                      f"<td>现持有{新主人_用户表数据.Money / 100}妃爱币</td>" \
                      f"</tr><tr></tr>" \
                      f"<tr>" \
                      f"<td>身价{奴隶_奴隶表数据.Price - SlaveConfig.AddPrice} → {奴隶_奴隶表数据.Price}</td>" \
                      f"<td></td>" \
                      f"<td></td>" \
                      f"</tr>"
    # 有主情况
    else:
        if 奴隶老婆QQ != 0:
            # 获取老婆用户表数据
            奴隶老婆_用户表数据 = DB_User.getUser(QQ=奴隶老婆QQ)
            奴隶老婆_奴隶表数据 = DB_slave.getUser(QQ=奴隶老婆QQ, GroupID=event.group_id)

            # 原主人获得金币 原主人更新
            原主人_用户表数据 = DB_User.getUser(QQ=原主人QQ)
            原主人收入 = (奴隶_奴隶表数据.Price + 奴隶老婆_奴隶表数据.Price) * SlaveConfig.OwnerIncome
            原主人_用户表数据.Money = int(原主人_用户表数据.Money + 原主人收入 * 100)
            DB_User.updateUser(原主人_用户表数据)

            # 奴隶&奴隶老婆获得金币 奴隶更新
            奴隶收入 = min(奴隶_奴隶表数据.Price * SlaveConfig.SlaveIncome, SlaveConfig.MaxSlaveIncome)
            奴隶收入 += min(奴隶老婆_奴隶表数据.Price * SlaveConfig.SlaveIncome, SlaveConfig.MaxSlaveIncome)
            奴隶_用户表数据.Money = int(奴隶_用户表数据.Money + 奴隶收入 * 100)
            奴隶老婆_用户表数据.Money = int(奴隶老婆_用户表数据.Money + 奴隶收入 * 100)
            DB_User.updateUser(奴隶_用户表数据)
            DB_User.updateUser(奴隶老婆_用户表数据)

            # 奴隶&奴隶老婆转让 奴隶&奴隶老婆更新
            奴隶_奴隶表数据.Price += SlaveConfig.AddPrice
            奴隶老婆_奴隶表数据.Price += SlaveConfig.AddPrice
            奴隶_奴隶表数据.Owner = event.user_id
            奴隶老婆_奴隶表数据.Owner = event.user_id
            奴隶_奴隶表数据.save()
            奴隶老婆_奴隶表数据.save()

            # 奴隶转让 新主人更新
            新主人_奴隶表数据.PurchaseTime = 新主人_奴隶表数据.PurchaseTime + 1
            新主人_奴隶表数据.LastPurchase = TodayStr
            新主人_奴隶表数据.save()
            新主人_用户表数据 = DB_User.getUser(event.user_id)
            # 原主人&奴隶老婆数据获取
            try:
                OldOwnerName = await GetQQGrouperName(bot=bot, QQ=原主人QQ, Group=event.group_id)
                SlaveCoupleName = await GetQQGrouperName(bot=bot, QQ=奴隶老婆QQ, Group=event.group_id)
            except Exception:
                OldOwnerName = ""
                SlaveCoupleName = ""
            content = f"<tr><td>" \
                      f"<img src={SlaveImageUrl} alt=\"\">" \
                      f"<img src={SlaveCoupleImageUrl} alt=\"\">" \
                      f"<br>{SlaveName} & {SlaveCoupleName}</td>" \
                      f"<td><img src={OldOwnerImageUrl} alt=\"\"> <br> {OldOwnerName}</td>" \
                      f"<td><img src={NewOwnerImageUrl} alt=\"\"> <br> {NewOwnerName}</td>" \
                      f"</tr><tr></tr>" \
                      f"<tr>" \
                      f"<td>收入{奴隶收入}&{奴隶收入}妃爱币</td>" \
                      f"<td>收入{原主人收入}妃爱币</td>" \
                      f"<td>花费{奴隶_奴隶表数据.Price + 奴隶老婆_奴隶表数据.Price - SlaveConfig.AddPrice * 2}妃爱币</td>" \
                      f"</tr><tr></tr>" \
                      f"<tr>" \
                      f"<td>现持有{奴隶_用户表数据.Money / 100}&{奴隶老婆_用户表数据.Money / 100}妃爱币</td>" \
                      f"<td>现持有{原主人_用户表数据.Money / 100}妃爱币</td>" \
                      f"<td>现持有{新主人_用户表数据.Money / 100}妃爱币</td>" \
                      f"</tr><tr></tr>" \
                      f"<tr>" \
                      f"<td>身价{奴隶_奴隶表数据.Price - SlaveConfig.AddPrice} → {奴隶_奴隶表数据.Price}<br>" \
                      f"身价{奴隶老婆_奴隶表数据.Price - SlaveConfig.AddPrice} → {奴隶老婆_奴隶表数据.Price}</td>" \
                      f"<td></td>" \
                      f"<td></td>" \
                      f"</tr>"
        else:
            # 原主人获得金币 原主人更新
            原主人_用户表数据 = DB_User.getUser(QQ=原主人QQ)
            原主人收入 = 奴隶_奴隶表数据.Price * SlaveConfig.OwnerIncome
            原主人_用户表数据.Money = int(原主人_用户表数据.Money + 原主人收入 * 100)
            DB_User.updateUser(原主人_用户表数据)
            # 奴隶获得金币 奴隶更新
            奴隶收入 = min(奴隶_奴隶表数据.Price * SlaveConfig.SlaveIncome, SlaveConfig.MaxSlaveIncome)
            奴隶_用户表数据.Money = int(奴隶_用户表数据.Money + 奴隶收入 * 100)
            DB_User.updateUser(奴隶_用户表数据)
            # 奴隶转让 奴隶更新
            奴隶原价 = 奴隶_奴隶表数据.Price
            奴隶_奴隶表数据.Price = 奴隶原价 + SlaveConfig.AddPrice
            奴隶_奴隶表数据.Owner = event.user_id
            奴隶_奴隶表数据.save()
            # 奴隶转让 新主人更新
            新主人_奴隶表数据.PurchaseTime = 新主人_奴隶表数据.PurchaseTime + 1
            新主人_奴隶表数据.LastPurchase = TodayStr
            新主人_奴隶表数据.save()
            新主人_用户表数据 = DB_User.getUser(event.user_id)
            # 原主人数据获取
            try:
                OldOwnerName = await GetQQGrouperName(bot=bot, QQ=原主人QQ, Group=event.group_id)
            except Exception:
                OldOwnerName = ""

            content = f"<tr>" \
                      f"<td><img src={SlaveImageUrl} alt=\"\"> <br> {SlaveName}</td>" \
                      f"<td><img src={OldOwnerImageUrl} alt=\"\"> <br> {OldOwnerName}</td>" \
                      f"<td><img src={NewOwnerImageUrl} alt=\"\"> <br> {NewOwnerName}</td>" \
                      f"</tr><tr></tr>" \
                      f"<tr>" \
                      f"<td>收入{奴隶收入}妃爱币</td>" \
                      f"<td>收入{原主人收入}妃爱币</td>" \
                      f"<td>花费{奴隶_奴隶表数据.Price - SlaveConfig.AddPrice}妃爱币</td>" \
                      f"</tr><tr></tr>" \
                      f"<tr>" \
                      f"<td>现持有{奴隶_用户表数据.Money / 100}妃爱币</td>" \
                      f"<td>现持有{原主人_用户表数据.Money / 100}妃爱币</td>" \
                      f"<td>现持有{新主人_用户表数据.Money / 100}妃爱币</td>" \
                      f"</tr><tr></tr>" \
                      f"<tr>" \
                      f"<td>身价{奴隶_奴隶表数据.Price - SlaveConfig.AddPrice} → {奴隶_奴隶表数据.Price}</td>" \
                      f"<td></td>" \
                      f"<td></td>" \
                      f"</tr>"

    htmlStr = htmlStr.replace("Info", content)
    pic = await html_to_pic(html=htmlStr, type="png", viewport={"width": 1200, "height": 10})
    message = MessageSegment.image(pic)
    await buySlave.send(message)
    return


@mySlave.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    Owner = event.user_id
    GroupID = event.group_id
    Slaves = DB_slave.getSlaves(QQ=Owner, GroupID=GroupID)
    Self = [DB_slave.getUser(QQ=event.user_id, GroupID=GroupID)]
    message = MessageSegment.at(Owner)
    with open(Menu_HTML_Path2, "r", encoding="utf-8") as file:
        htmlStr = file.read()
    message = message + MessageSegment.text("你现在拥有的群友如下")
    count = 0
    htmls = []
    content = ""
    CoupleMap = {}  # 用于记录已存在的Couple
    Slaves = Self + Slaves
    for Slave in Slaves:
        if Slave.Owner != 0:
            # 已在之前显示
            if Slave.QQ in CoupleMap.keys():
                continue
            Couple = SlaveUtils.结婚对象(Slave)
            if count == 50:
                count = 0
                htmls.append(htmlStr.replace("SlaveInfo", content))
                content = ""
            try:
                SlaveName = await GetQQGrouperName(bot=bot, QQ=Slave.QQ, Group=event.group_id)
            except Exception:
                continue
            SlaveImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={Slave.QQ}&s=100"
            SlaveName = removeUrl(SlaveName)
            SlaveExtraInfo = SlaveUtils.PrintPersonInfo(slave=Slave)
            # 当存在结婚对象时的打印情况
            if Couple != 0:
                CoupleMap[Couple] = True
                try:
                    CoupleName = await GetQQGrouperName(bot=bot, QQ=Couple, Group=event.group_id)
                except Exception:
                    try:
                        CoupleName = await GetQQStrangerName(bot=bot, QQ=Couple)
                    except Exception:
                        CoupleName = ""
                CoupleImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={Couple}&s=100"
                CoupleName = removeUrl(CoupleName)
                CoupleSlave = DB_slave.getUser(QQ=Couple, GroupID=event.group_id)
                CoupleExtraInfo = SlaveUtils.PrintPersonInfo(slave=CoupleSlave)
                content = content + f"<tr><td>" \
                                    f"<img src={SlaveImageUrl} width=\"70px\"  height=\"70px\" alt=\"\">" \
                                    f"<img src={CoupleImageUrl} width=\"70px\" height=\"70px\" alt=\"\">" \
                                    f"<br> {SlaveName} & {CoupleName}</td>" \
                                    f"<td>{Slave.Price + CoupleSlave.Price}</td>" \
                                    f"<td>{SlaveExtraInfo} <br> {CoupleExtraInfo}</td>" \
                                    f"<td>{Slave.QQ} <br> {Couple}</td>" \
                                    f"</tr><tr></tr>"
            else:
                content = content + f"<tr><td><img src={SlaveImageUrl} alt=\"\"> <br> {SlaveName}</td>" \
                                    f"<td>{Slave.Price}</td>" \
                                    f"<td>{SlaveExtraInfo}</td>" \
                                    f"<td>{Slave.QQ}</td>" \
                                    f"</tr><tr></tr>"
            count = count + 1
    htmls.append(htmlStr.replace("SlaveInfo", content))
    for html in htmls:
        pic = await html_to_pic(html=html, type="png", viewport={"width": 1440, "height": 10})
        message = message + MessageSegment.image(pic)
    await mySlave.send(message)


@Mission.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    Owner = event.user_id
    message = str(event.message)
    message = message.replace("#主人的任务", "").strip()
    message = message.replace("[CQ:at,qq=", "").strip()
    message = message.replace("]", "")
    messages = message.split(" ")
    # 输入处理
    if len(messages) == 1:
        if event.is_tome():
            skillName = messages[0].strip()
            slaveQQ = event.self_id
        else:
            msg = MessageSegment.at(Owner) + MessageSegment.text("输入格式错误")
            await Mission.send(msg)
            return
    elif len(messages) == 2:
        if not messages[0].isdigit():
            msg = MessageSegment.at(Owner) + MessageSegment.text("输入格式错误")
            await Mission.send(msg)
            return
        else:
            slaveQQ = int(messages[0].strip())
            skillName = messages[1].strip()
    else:
        msg = MessageSegment.at(Owner) + MessageSegment.text("输入格式错误")
        await Mission.send(msg)
        return
    # 检查逻辑——奴隶为本群成员
    try:
        slaveName = await GetQQGrouperName(bot=bot, QQ=slaveQQ, Group=event.group_id)
    except Exception:
        await Mission.send("只能命令你的群友哦~")
        return
    # 检查主从关系
    slave = DB_slave.getUser(QQ=slaveQQ, GroupID=event.group_id)
    if int(slave.Owner) != event.user_id:
        await Mission.send("只能命令你的群友哦~")
        return
    # 获取姓名
    try:
        ownerName = await GetQQGrouperName(bot=bot, QQ=slave.Owner, Group=event.group_id)
    except Exception:
        ownerName = ""
    # 执行指令
    result = ExecuteSkill(slave=slave, skillName=skillName, slaveName=slaveName, ownerName=ownerName)
    msg = MessageSegment.at(event.user_id) + MessageSegment.text(result)
    await Mission.send(msg)
    return


@AllWork.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        ownerName = await GetQQGrouperName(bot=bot, QQ=event.user_id, Group=event.group_id)
    except Exception:
        ownerName = ""
    slaves = DB_slave.getSlaves(QQ=event.user_id, GroupID=event.group_id)
    message = ""
    for slave in slaves:
        # 检查逻辑——奴隶为本群成员
        try:
            slaveName = await GetQQGrouperName(bot=bot, QQ=slave.QQ, Group=event.group_id)
        except Exception:
            continue
        result = skills.派去打黑工(slave=slave, slaveName=slaveName, ownerName=ownerName)
        if "今天已经打过黑工了" not in result:
            message += result + "\n\n"
    if message != "":
        messages = message.split("\n")
        if len(messages) > 20:
            node = Nodes(qID=event.self_id, name="超可爱的妃爱酱", content="由于消息较长，结果通过转发展示哦。")
            node += Nodes(qID=event.self_id, name="超可爱的妃爱酱", content=message)
            await bot.call_api("send_group_forward_msg", **{"group_id": event.group_id, "messages": node.msg()})
            return
        message = MessageSegment.at(event.user_id) + "\n" + message.rstrip()
    else:
        message = MessageSegment.at(event.user_id) + "你还没有未打工的群友哦~"
    await AllWork.send(message)


@Work.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    state["JobsDict"] = {}
    msg = "要去哪打工呢？\n"
    slave = DB_slave.getUser(QQ=event.user_id, GroupID=event.group_id)
    for job in Jobs:
        if job.Enable(slave):
            state["JobsDict"][job.name] = job
            msg += f"{job.name}\n"
    msg = MessageSegment.at(event.user_id) + msg.rstrip()
    await Work.send(msg)


@Work.receive("")
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    message = str(event.message)
    if message not in state["JobsDict"].keys():
        msg = MessageSegment.at(event.user_id) + "要打的工不存在哦"
        await Work.send(msg)
        return
    Name = await GetQQGrouperName(bot=bot, QQ=event.user_id, Group=event.group_id)
    slave = DB_slave.getUser(QQ=event.user_id, GroupID=event.group_id)
    result = skills.自由打工(slave=slave, slaveName=Name, job=state["JobsDict"][message])
    msg = MessageSegment.at(event.user_id) + MessageSegment.text(result)
    await Work.send(msg)
    return


@AddCart.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    message = str(event.message)
    message = re.sub(pattern=r"#群友购物车\s*添加群友", repl="", string=message).strip()
    message = message.replace("[CQ:at,qq=", "").strip()
    message = message.replace("]", "").strip()
    if not message.isdigit() and (message != ""):
        msg = MessageSegment.at(event.user_id) + "输入格式错误"
        await AddCart.send(msg)
        return
    else:
        if message == "":
            QQ = event.self_id
        else:
            QQ = int(message)
        # 检查逻辑——奴隶为本群成员
        try:
            SlaveInfo = await bot.get_group_member_info(group_id=event.group_id, user_id=QQ)
        except Exception as e:
            msg = MessageSegment.at(event.user_id) + "添加的群友不在群内哦"
            await AddCart.send(msg)
            return
        # 检查逻辑——不能添加自己
        if QQ == event.user_id:
            msg = MessageSegment.at(event.user_id) + "不能添加自己哦"
            await AddCart.send(msg)
            return
        GroupID = int(event.group_id)
        info = CartUtils.ReadInfo()
        if str(GroupID) not in info.keys():
            info[str(GroupID)] = {str(event.user_id): [QQ]}
        else:
            if str(event.user_id) not in info[str(GroupID)]:
                info[str(GroupID)][str(event.user_id)] = [QQ]
            else:
                if QQ not in info[str(GroupID)][str(event.user_id)]:
                    info[str(GroupID)][str(event.user_id)].append(QQ)
        CartUtils.WriteInfo(info)
        with open(Menu_HTML_Path4, "r", encoding="utf-8") as file:
            htmlStr = file.read()
        count = 0
        content = ""
        for QQ in info[str(GroupID)][str(event.user_id)]:
            try:
                SlaveInfo = await bot.get_group_member_info(group_id=event.group_id, user_id=QQ,
                                                            no_cache=False)
                if SlaveInfo["card"] == "":
                    SlaveName = SlaveInfo["nickname"]
                else:
                    SlaveName = SlaveInfo["card"]
            except Exception:
                continue
            SlaveImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={QQ}&s=100"
            SlaveName = removeUrl(SlaveName)
            Slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
            SlaveExtraInfo = SlaveUtils.PrintPersonInfo(slave=Slave)
            content = content + f"<tr><td>{count}</td>" \
                                f"<td><img src={SlaveImageUrl} alt=\"\"> <br> {SlaveName}</td>" \
                                f"<td>{Slave.Price}</td>" \
                                f"<td>{SlaveExtraInfo}</td>" \
                                f"<td>{Slave.QQ}</td>" \
                                f"</tr><tr></tr>"
            count = count + 1
        html = htmlStr.replace("Info", content)
        pic = await html_to_pic(html=html, type="png", viewport={"width": 1440, "height": 10})
        msg = MessageSegment.at(event.user_id) + "添加成功！" + MessageSegment.image(pic)
        await AddCart.send(msg)


@DeleteCart.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    message = str(event.message)
    message = re.sub(pattern=r"^#群友购物车\s*删除群友", repl="", string=message).strip()
    message = message.replace("[CQ:at,qq=", "").strip()
    message = message.replace("]", "").strip()
    if message == "全部":
        GroupID = event.group_id
        QQ = event.user_id
        info = CartUtils.ReadInfo()
        if str(GroupID) not in info.keys():
            info[str(GroupID)] = {str(event.user_id): []}
        else:
            info[str(GroupID)][str(event.user_id)] = []
        CartUtils.WriteInfo(info)
        msg = MessageSegment.at(event.user_id) + "购物车已全部清空"
        await DeleteCart.send(msg)
        return

    if not message.isdigit() and (message != ""):
        msg = MessageSegment.at(event.user_id) + "输入格式错误"
        await DeleteCart.send(msg)
        return
    else:
        if message == "":
            slaveQQ = event.self_id
        else:
            slaveQQ = int(message)
        GroupID = event.group_id
        QQ = event.user_id
        emptyErr = MessageSegment.at(event.user_id) + "购物车中没有该群友哦"
        # 为QQ号而非序号
        if slaveQQ >= 10000:
            info = CartUtils.ReadInfo()
            if str(GroupID) not in info:
                await DeleteCart.send(emptyErr)
                return
            if str(QQ) not in info[str(GroupID)]:
                await DeleteCart.send(emptyErr)
                return
            if slaveQQ not in info[str(GroupID)][str(QQ)]:
                await DeleteCart.send(emptyErr)
                return
            info[str(GroupID)][str(QQ)].remove(QQ)
            CartUtils.WriteInfo(info)
        else:
            info = CartUtils.ReadInfo()
            if str(GroupID) not in info:
                await DeleteCart.send(emptyErr)
                return
            if str(QQ) not in info[str(GroupID)]:
                await DeleteCart.send(emptyErr)
                return
            if slaveQQ >= len(info[str(GroupID)][str(QQ)]):
                await DeleteCart.send(emptyErr)
                return
            info[str(GroupID)][str(QQ)].pop(slaveQQ)
            CartUtils.WriteInfo(info)

        with open(Menu_HTML_Path4, "r", encoding="utf-8") as file:
            htmlStr = file.read()
        count = 0
        content = ""
        for QQ in info[str(GroupID)][str(event.user_id)]:
            try:
                SlaveName = await GetQQGrouperName(bot=bot, QQ=QQ, Group=event.group_id)
            except Exception:
                continue
            SlaveImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={QQ}&s=100"
            SlaveName = removeUrl(SlaveName)
            Slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
            SlaveExtraInfo = SlaveUtils.PrintPersonInfo(slave=Slave)
            content = content + f"<tr><td>{count}</td>" \
                                f"<td><img src={SlaveImageUrl} alt=\"\"> <br> {SlaveName}</td>" \
                                f"<td>{Slave.Price}</td>" \
                                f"<td>{SlaveExtraInfo}</td>" \
                                f"<td>{Slave.QQ}</td>" \
                                f"</tr><tr></tr>"
            count = count + 1
        html = htmlStr.replace("Info", content)
        pic = await html_to_pic(html=html, type="png", viewport={"width": 1440, "height": 10})
        msg = MessageSegment.at(event.user_id) + "删除成功！" + MessageSegment.image(pic)
        await DeleteCart.send(msg)


@CheckCart.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    info = CartUtils.ReadInfo()
    GroupID = event.group_id
    if str(GroupID) not in info.keys():
        info[str(GroupID)] = {str(event.user_id): []}
        CartUtils.WriteInfo(info)
    elif str(event.user_id) not in info[str(GroupID)]:
        info[str(GroupID)][str(event.user_id)] = []
        CartUtils.WriteInfo(info)
    with open(Menu_HTML_Path4, "r", encoding="utf-8") as file:
        htmlStr = file.read()
    content = ""
    count = 0
    for QQ in info[str(GroupID)][str(event.user_id)]:
        try:
            SlaveName = await GetQQGrouperName(bot=bot, QQ=QQ, Group=event.group_id)
        except Exception:
            continue
        SlaveImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={QQ}&s=100"
        SlaveName = removeUrl(SlaveName)
        Slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
        SlaveExtraInfo = SlaveUtils.PrintPersonInfo(slave=Slave)
        content = content + f"<tr><td>{count}</td>" \
                            f"<td><img src={SlaveImageUrl} alt=\"\"> <br> {SlaveName}</td>" \
                            f"<td>{Slave.Price}</td>" \
                            f"<td>{SlaveExtraInfo}</td>" \
                            f"<td>{Slave.QQ}</td>" \
                            f"</tr><tr></tr>"
        count = count + 1
    html = htmlStr.replace("Info", content)
    pic = await html_to_pic(html=html, type="png", viewport={"width": 1440, "height": 10})
    msg = MessageSegment.at(event.user_id) + MessageSegment.image(pic)
    await DeleteCart.send(msg)


@BuyCart.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    info = CartUtils.ReadInfo()
    GroupID = event.group_id
    if str(GroupID) not in info.keys():
        info[str(GroupID)] = {str(event.user_id): []}
        CartUtils.WriteInfo(info)
    elif str(event.user_id) not in info[str(GroupID)]:
        info[str(GroupID)][str(event.user_id)] = []
        CartUtils.WriteInfo(info)

    # 检查今日购买次数是否到达上限
    新主人_奴隶表数据 = DB_slave.getUser(QQ=event.user_id, GroupID=event.group_id)
    Today = datetime.datetime.now()
    TodayStr = str(Today.year) + "-" + str(Today.month) + "-" + str(Today.day)
    # 最后购买日期为本日
    if TodayStr == 新主人_奴隶表数据.LastPurchase:
        if 新主人_奴隶表数据.PurchaseTime >= SlaveConfig.MaxDailyPurchase:
            message = MessageSegment.at(user_id=event.user_id) + MessageSegment.text(
                "你今天的购买次数已经到上限了哦~")
            await buySlave.send(message)
            return
    else:
        新主人_奴隶表数据.PurchaseTime = 0

    NewOwnerName = await GetQQGrouperName(bot=bot, QQ=event.user_id, Group=event.group_id)
    # html模板
    with open(Menu_HTML_Path3, "r", encoding="utf-8") as file:
        htmlStr = file.read()
    content = ""
    for 奴隶QQ in info[str(GroupID)][str(event.user_id)]:
        if 新主人_奴隶表数据.PurchaseTime >= SlaveConfig.MaxDailyPurchase:
            break
        奴隶_奴隶表数据 = DB_slave.getUser(QQ=奴隶QQ, GroupID=event.group_id)
        # 检查逻辑——项圈不在期限内 若老婆被捆则同样不能购买
        flag, result = SlaveUtils.项圈状态(QQ=奴隶QQ, GroupID=event.group_id)
        if flag:
            continue
        奴隶老婆QQ = SlaveUtils.结婚对象(slave=奴隶_奴隶表数据)
        if 奴隶老婆QQ != 0:
            flag, result = SlaveUtils.项圈状态(QQ=奴隶老婆QQ, GroupID=event.group_id)
            if flag:
                continue
        # 检查逻辑——不能自己买自己
        if 奴隶QQ == event.user_id:
            continue
        # 检查逻辑——不能买自己老婆
        if 奴隶QQ == SlaveUtils.结婚对象(slave=新主人_奴隶表数据):
            continue
        # 检查逻辑——不能购买已有奴隶
        if 奴隶_奴隶表数据.Owner == event.user_id:
            continue
        # 检查逻辑——奴隶为本群成员
        try:
            SlaveName = await GetQQGrouperName(bot=bot, QQ=奴隶QQ, Group=event.group_id)
        except Exception:
            continue
        # 检查逻辑——金币充足
        if not DB_User.spendMoney(QQ=event.user_id, Money=奴隶_奴隶表数据.Price):
            continue
        原主人QQ = 奴隶_奴隶表数据.Owner
        # 头像相关
        SlaveImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={奴隶QQ}&s=100"
        OldOwnerImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={原主人QQ}&s=100"
        NewOwnerImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={event.user_id}&s=100"
        SlaveCoupleImageUrl = f"http://q1.qlogo.cn/g?b=qq&nk={奴隶老婆QQ}&s=100"
        奴隶_用户表数据 = DB_User.getUser(QQ=奴隶_奴隶表数据.QQ)
        # 无主情况
        if 原主人QQ == 0:
            # 奴隶转让 新主人更新
            新主人_奴隶表数据.PurchaseTime = 新主人_奴隶表数据.PurchaseTime + 1
            新主人_奴隶表数据.LastPurchase = TodayStr
            新主人_奴隶表数据.save()
            新主人_用户表数据 = DB_User.getUser(event.user_id)
            # 奴隶获得金币 奴隶更新
            if 奴隶老婆QQ != 0:
                # 获取老婆用户表数据
                奴隶老婆_用户表数据 = DB_User.getUser(QQ=奴隶老婆QQ)
                奴隶老婆_奴隶表数据 = DB_slave.getUser(QQ=奴隶老婆QQ, GroupID=event.group_id)
                try:
                    SlaveCoupleName = await GetQQGrouperName(bot=bot, QQ=奴隶老婆QQ, Group=event.group_id)
                except Exception:
                    SlaveCoupleName = ""
                # 更新，两人收入叠加
                奴隶收入 = 奴隶_奴隶表数据.Price + 奴隶老婆_奴隶表数据.Price
                奴隶_用户表数据.Money = int(奴隶_用户表数据.Money + 奴隶收入 * 100)
                奴隶老婆_用户表数据.Money = int(奴隶老婆_用户表数据.Money + 奴隶收入 * 100)
                DB_User.updateUser(奴隶_用户表数据)
                DB_User.updateUser(奴隶老婆_用户表数据)
                # 奴隶转让 奴隶更新
                奴隶_奴隶表数据.Price += SlaveConfig.AddPrice
                奴隶老婆_奴隶表数据.Price += SlaveConfig.AddPrice
                奴隶_奴隶表数据.Owner = event.user_id
                奴隶老婆_奴隶表数据.Owner = event.user_id
                奴隶_奴隶表数据.save()
                奴隶老婆_奴隶表数据.save()
                content = f"<tr><td>" \
                          f"<img src={SlaveImageUrl} alt=\"\">" \
                          f"<img src={SlaveCoupleImageUrl} alt=\"\">" \
                          f"<br>{SlaveName} & {SlaveCoupleName}</td>" \
                          f"<td></td>" \
                          f"<td><img src={NewOwnerImageUrl} alt=\"\"> <br> {NewOwnerName}</td>" \
                          f"</tr><tr></tr>" \
                          f"<tr>" \
                          f"<td>收入{奴隶收入}&{奴隶收入}妃爱币</td>" \
                          f"<td></td>" \
                          f"<td>花费{奴隶_奴隶表数据.Price + 奴隶老婆_奴隶表数据.Price - SlaveConfig.AddPrice * 2}妃爱币</td>" \
                          f"</tr><tr></tr>" \
                          f"<tr>" \
                          f"<td>现持有{奴隶_用户表数据.Money / 100}&{奴隶老婆_用户表数据.Money / 100}妃爱币</td>" \
                          f"<td></td>" \
                          f"<td>现持有{新主人_用户表数据.Money / 100}妃爱币</td>" \
                          f"</tr><tr></tr>" \
                          f"<tr>" \
                          f"<td>身价{奴隶_奴隶表数据.Price - SlaveConfig.AddPrice} → {奴隶_奴隶表数据.Price}<br>" \
                          f"身价{奴隶老婆_奴隶表数据.Price - SlaveConfig.AddPrice} → {奴隶老婆_奴隶表数据.Price}" \
                          f"</td>" \
                          f"<td></td>" \
                          f"<td></td>" \
                          f"</tr>"
            else:
                奴隶收入 = 奴隶_奴隶表数据.Price
                奴隶_用户表数据.Money = int(奴隶_用户表数据.Money + 奴隶收入 * 100)
                DB_User.updateUser(奴隶_用户表数据)
                # 奴隶转让 奴隶更新
                奴隶_奴隶表数据.Price += SlaveConfig.AddPrice
                奴隶_奴隶表数据.Owner = event.user_id
                奴隶_奴隶表数据.save()
                content = f"<tr>" \
                          f"<td><img src={SlaveImageUrl} alt=\"\"> <br> {SlaveName}</td>" \
                          f"<td></td>" \
                          f"<td><img src={NewOwnerImageUrl} alt=\"\"> <br> {NewOwnerName}</td>" \
                          f"</tr><tr></tr>" \
                          f"<tr>" \
                          f"<td>收入{奴隶收入}妃爱币</td>" \
                          f"<td></td>" \
                          f"<td>花费{奴隶_奴隶表数据.Price - SlaveConfig.AddPrice}妃爱币</td>" \
                          f"</tr><tr></tr>" \
                          f"<tr>" \
                          f"<td>现持有{奴隶_用户表数据.Money / 100}妃爱币</td>" \
                          f"<td></td>" \
                          f"<td>现持有{新主人_用户表数据.Money / 100}妃爱币</td>" \
                          f"</tr><tr></tr>" \
                          f"<tr>" \
                          f"<td>身价{奴隶_奴隶表数据.Price - SlaveConfig.AddPrice} → {奴隶_奴隶表数据.Price}</td>" \
                          f"<td></td>" \
                          f"<td></td>" \
                          f"</tr>"
        # 有主情况
        else:
            if 奴隶老婆QQ != 0:
                # 获取老婆用户表数据
                奴隶老婆_用户表数据 = DB_User.getUser(QQ=奴隶老婆QQ)
                奴隶老婆_奴隶表数据 = DB_slave.getUser(QQ=奴隶老婆QQ, GroupID=event.group_id)

                # 原主人获得金币 原主人更新
                原主人_用户表数据 = DB_User.getUser(QQ=原主人QQ)
                原主人收入 = (奴隶_奴隶表数据.Price + 奴隶老婆_奴隶表数据.Price) * SlaveConfig.OwnerIncome
                原主人_用户表数据.Money = int(原主人_用户表数据.Money + 原主人收入 * 100)
                DB_User.updateUser(原主人_用户表数据)

                # 奴隶&奴隶老婆获得金币 奴隶更新
                奴隶收入 = min(奴隶_奴隶表数据.Price * SlaveConfig.SlaveIncome, SlaveConfig.MaxSlaveIncome)
                奴隶收入 += min(奴隶老婆_奴隶表数据.Price * SlaveConfig.SlaveIncome, SlaveConfig.MaxSlaveIncome)
                奴隶_用户表数据.Money = int(奴隶_用户表数据.Money + 奴隶收入 * 100)
                奴隶老婆_用户表数据.Money = int(奴隶老婆_用户表数据.Money + 奴隶收入 * 100)
                DB_User.updateUser(奴隶_用户表数据)
                DB_User.updateUser(奴隶老婆_用户表数据)

                # 奴隶&奴隶老婆转让 奴隶&奴隶老婆更新
                奴隶_奴隶表数据.Price += SlaveConfig.AddPrice
                奴隶老婆_奴隶表数据.Price += SlaveConfig.AddPrice
                奴隶_奴隶表数据.Owner = event.user_id
                奴隶老婆_奴隶表数据.Owner = event.user_id
                奴隶_奴隶表数据.save()
                奴隶老婆_奴隶表数据.save()

                # 奴隶转让 新主人更新
                新主人_奴隶表数据.PurchaseTime = 新主人_奴隶表数据.PurchaseTime + 1
                新主人_奴隶表数据.LastPurchase = TodayStr
                新主人_奴隶表数据.save()
                新主人_用户表数据 = DB_User.getUser(event.user_id)
                # 原主人&奴隶老婆数据获取
                try:
                    OldOwnerName = await GetQQGrouperName(bot=bot, QQ=原主人QQ, Group=event.group_id)
                    SlaveCoupleName = await GetQQGrouperName(bot=bot, QQ=奴隶老婆QQ, Group=event.group_id)
                except Exception:
                    OldOwnerName = ""
                    SlaveCoupleName = ""
                content = f"<tr><td>" \
                          f"<img src={SlaveImageUrl} alt=\"\">" \
                          f"<img src={SlaveCoupleImageUrl} alt=\"\">" \
                          f"<br>{SlaveName} & {SlaveCoupleName}</td>" \
                          f"<td><img src={OldOwnerImageUrl} alt=\"\"> <br> {OldOwnerName}</td>" \
                          f"<td><img src={NewOwnerImageUrl} alt=\"\"> <br> {NewOwnerName}</td>" \
                          f"</tr><tr></tr>" \
                          f"<tr>" \
                          f"<td>收入{奴隶收入}&{奴隶收入}妃爱币</td>" \
                          f"<td>收入{原主人收入}妃爱币</td>" \
                          f"<td>花费{奴隶_奴隶表数据.Price + 奴隶老婆_奴隶表数据.Price - SlaveConfig.AddPrice * 2}妃爱币</td>" \
                          f"</tr><tr></tr>" \
                          f"<tr>" \
                          f"<td>现持有{奴隶_用户表数据.Money / 100}&{奴隶老婆_用户表数据.Money / 100}妃爱币</td>" \
                          f"<td>现持有{原主人_用户表数据.Money / 100}妃爱币</td>" \
                          f"<td>现持有{新主人_用户表数据.Money / 100}妃爱币</td>" \
                          f"</tr><tr></tr>" \
                          f"<tr>" \
                          f"<td>身价{奴隶_奴隶表数据.Price - SlaveConfig.AddPrice} → {奴隶_奴隶表数据.Price}<br>" \
                          f"身价{奴隶老婆_奴隶表数据.Price - SlaveConfig.AddPrice} → {奴隶老婆_奴隶表数据.Price}</td>" \
                          f"<td></td>" \
                          f"<td></td>" \
                          f"</tr>"
            else:
                # 原主人获得金币 原主人更新
                原主人_用户表数据 = DB_User.getUser(QQ=原主人QQ)
                原主人收入 = 奴隶_奴隶表数据.Price * SlaveConfig.OwnerIncome
                原主人_用户表数据.Money = int(原主人_用户表数据.Money + 原主人收入 * 100)
                DB_User.updateUser(原主人_用户表数据)
                # 奴隶获得金币 奴隶更新
                奴隶收入 = min(奴隶_奴隶表数据.Price * SlaveConfig.SlaveIncome, SlaveConfig.MaxSlaveIncome)
                奴隶_用户表数据.Money = int(奴隶_用户表数据.Money + 奴隶收入 * 100)
                DB_User.updateUser(奴隶_用户表数据)
                # 奴隶转让 奴隶更新
                奴隶原价 = 奴隶_奴隶表数据.Price
                奴隶_奴隶表数据.Price = 奴隶原价 + SlaveConfig.AddPrice
                奴隶_奴隶表数据.Owner = event.user_id
                奴隶_奴隶表数据.save()
                # 奴隶转让 新主人更新
                新主人_奴隶表数据.PurchaseTime = 新主人_奴隶表数据.PurchaseTime + 1
                新主人_奴隶表数据.LastPurchase = TodayStr
                新主人_奴隶表数据.save()
                新主人_用户表数据 = DB_User.getUser(event.user_id)
                # 原主人数据获取
                try:
                    OldOwnerName = await GetQQGrouperName(bot=bot, QQ=原主人QQ, Group=event.group_id)
                except Exception:
                    OldOwnerName = ""

                content = f"<tr>" \
                          f"<td><img src={SlaveImageUrl} alt=\"\"> <br> {SlaveName}</td>" \
                          f"<td><img src={OldOwnerImageUrl} alt=\"\"> <br> {OldOwnerName}</td>" \
                          f"<td><img src={NewOwnerImageUrl} alt=\"\"> <br> {NewOwnerName}</td>" \
                          f"</tr><tr></tr>" \
                          f"<tr>" \
                          f"<td>收入{奴隶收入}妃爱币</td>" \
                          f"<td>收入{原主人收入}妃爱币</td>" \
                          f"<td>花费{奴隶_奴隶表数据.Price - SlaveConfig.AddPrice}妃爱币</td>" \
                          f"</tr><tr></tr>" \
                          f"<tr>" \
                          f"<td>现持有{奴隶_用户表数据.Money / 100}妃爱币</td>" \
                          f"<td>现持有{原主人_用户表数据.Money / 100}妃爱币</td>" \
                          f"<td>现持有{新主人_用户表数据.Money / 100}妃爱币</td>" \
                          f"</tr><tr></tr>" \
                          f"<tr>" \
                          f"<td>身价{奴隶_奴隶表数据.Price - SlaveConfig.AddPrice} → {奴隶_奴隶表数据.Price}</td>" \
                          f"<td></td>" \
                          f"<td></td>" \
                          f"</tr>"
    htmlStr = htmlStr.replace("Info", content)
    pic = await html_to_pic(html=htmlStr, type="png", viewport={"width": 1440, "height": 10})
    message = MessageSegment.at(event.user_id) + MessageSegment.image(pic)
    await BuyCart.send(message)
    return


"""
此后为提取的通用功能函数
"""
