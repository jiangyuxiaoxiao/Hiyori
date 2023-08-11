"""
@Author: Kasugano Sora
@Author-2: Zao
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/1-0:22
@LastDate: 2023/8/1-21:48
@Desc: 签到插件
@Ver : 1.0.0
"""
import datetime
import random

from nonebot.matcher import Matcher
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Bot
from nonebot import get_driver
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

from Hiyori.Utils.Database import DB_User, DB_Item
from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.API.QQ import GetQQGrouperName, GetQQStrangerName
from Hiyori.Utils.File import DirExist
from Hiyori.Utils.Message.Image import ImageMessage
from Hiyori.Utils.Spider.WebShot import Web2ImgBytes
from Hiyori.Utils.Matcher import logPluginExecuteTime
from .config import signInImages, Mode

__plugin_meta__ = PluginMetadata(
    name="签到",  # 用于在菜单显示 用于插件开关
    description="不要忘了每日签到哦！连续签到有额外加成~",  # 用于在菜单中描述
    usage="#签到 【每日签到】\n"
          "#查看 【查看当前好感与金币】",
    extra={"CD_Weight": 0,  # 调用插件CD权重 不填的话不会触发权重插件
           "Group": "Daily",
           "Keep_On": False,
           "Type": "Normal_Plugin",
           }
)

# 预定义数值-收入
# 连续签到时收益提高
年收入: int = 43484  # 2023年城镇人均收入
收入福利系数: float = 0.3  # 上浮系数
日收入: int = int(年收入 * (1 + 收入福利系数) / 365)
收入波动幅度: int = int(日收入 * 0.2)  # 波动幅度
连续签到_收入奖励系数: float = 0.05  # 连续签到奖励
连续签到_最大收入奖励系数: float = 1.5  # 连续签到奖励上限
# 预定义数值-好感度
# 连续签到时收益提高
月好感度: int = 400
日好感度: int = int(月好感度 / 30)
好感度波动幅度: int = int(日好感度 * 0.2)  # 波动幅度
连续签到_好感度奖励系数: float = 0.05  # 连续签到奖励
连续签到_最大好感度奖励系数: float = 1.5  # 连续签到奖励上限

signIn = on_regex(r"^#?签到$", priority=Priority.普通优先级, block=False)
check = on_regex(r"^#查看$", priority=Priority.普通优先级, block=False)

DirExist("./Data/SignIn")


@signIn.handle()
@logPluginExecuteTime
async def _(bot: Bot, event: MessageEvent):
    QQ = event.user_id
    User = DB_User.getUser(QQ)
    LastSignIn = str(User.SignInDate)
    Today = datetime.datetime.now()
    TodayStr = str(Today.year) + "-" + str(Today.month) + "-" + str(Today.day)
    ComboDay = 0
    # 未签到
    if LastSignIn == "":
        ComboDay = 0
    # 重复签到
    elif TodayStr == str(LastSignIn.split("@")[0]):
        if len(LastSignIn.split("@")) == 2:
            ComboDay = LastSignIn.split("@")[1]
            # Sora渲染
            if Mode.Sora:
                # 获取当前端口号
                conf = get_driver().config.dict()
                port = conf["port"]
                # 获取昵称
                if hasattr(event, "group_id"):
                    Name = await GetQQGrouperName(bot=bot, QQ=QQ, Group=event.group_id)
                else:
                    Name = await GetQQStrangerName(bot=bot, QQ=QQ)
                Ls = LastSignIn.split("@")[0]
                url = f"127.0.0.1:{port}/Sign/Sign.html?QQ={QQ}&&Name={Name}&&LastSignDate={Ls}" \
                      f"&&Gold={User.Money / 100}" \
                      f"&&Attitude={User.Attitude}&&HasSign=true&&SignCombo={ComboDay}"
                image = await Web2ImgBytes(url=url, width=1200)
                msg = MessageSegment.at(QQ) + MessageSegment.image(image)
                await signIn.send(msg)
            else:
                # Zao渲染
                ReImage = ImageMessage(f"./Data/SignIn/{QQ}.png")
                message = MessageSegment.at(event.user_id) + "你今天已经签到过了哦~" + ReImage
                await signIn.send(message)
        else:
            logger.error(f"签到记录出错，记录信息{LastSignIn}，QQ={event.user_id}")
        return
    else:
        # 获取连续签到天数
        if len(LastSignIn.split("@")) != 2:
            logger.error(f"签到记录出错，记录信息{LastSignIn}，QQ={event.user_id}")
            return
        ComboDay = LastSignIn.split("@")[1]
        if not ComboDay.isdigit():
            logger.error(f"签到记录出错，记录信息{LastSignIn}，QQ={event.user_id}")
            return
        # 判断签到是否连续
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        yesterdayStr = str(yesterday.year) + "-" + str(yesterday.month) + "-" + str(yesterday.day)
        if yesterdayStr == LastSignIn.split("@")[0]:
            ComboDay = int(ComboDay)
        else:
            # 提取物品数量
            亚托莉断签保护卡 = DB_Item.getUserItem(QQ=event.user_id, ItemName="亚托莉断签保护卡")
            芳乃断签保护卡 = DB_Item.getUserItem(QQ=event.user_id, ItemName="芳乃断签保护卡")
            穹妹断签保护卡 = DB_Item.getUserItem(QQ=event.user_id, ItemName="穹妹断签保护卡")
            # 判断断签卡
            "数据库日期存储格式示范 2023-6-11@2"
            LastSignInStr = LastSignIn.split("@")[0]
            LastSignInStrs = LastSignInStr.split("-")
            try:
                Year = int(LastSignInStrs[0])
                Month = int(LastSignInStrs[1])
                Day = int(LastSignInStrs[2])
                LastDay = datetime.date(Year, Month, Day)
            except Exception:
                LastDay = yesterday
            ComboDay = int(ComboDay)
            # 当断签不超过1天
            if yesterday - LastDay <= datetime.timedelta(days=1):
                if 亚托莉断签保护卡.Quantity >= 1:
                    亚托莉断签保护卡.Quantity -= 1
                    亚托莉断签保护卡.save()
                elif 芳乃断签保护卡.Quantity >= 1:
                    芳乃断签保护卡.Quantity -= 1
                    芳乃断签保护卡.save()
                elif 穹妹断签保护卡.Quantity >= 1:
                    穹妹断签保护卡.Quantity -= 1
                    穹妹断签保护卡.save()
                else:
                    ComboDay = 0
            # 当断签不超过5天
            elif yesterday - LastDay <= datetime.timedelta(days=5):
                if 芳乃断签保护卡.Quantity >= 1:
                    芳乃断签保护卡.Quantity -= 1
                    芳乃断签保护卡.save()
                elif 穹妹断签保护卡.Quantity >= 1:
                    穹妹断签保护卡.Quantity -= 1
                    穹妹断签保护卡.save()
                else:
                    ComboDay = 0
            # 断签超过5天
            else:
                if 穹妹断签保护卡.Quantity >= 1:
                    穹妹断签保护卡.Quantity -= 1
                    穹妹断签保护卡.save()
                else:
                    ComboDay = 0
    AddMoney = int(random.randint(日收入 - 收入波动幅度, 日收入 + 收入波动幅度) * (1 + 收入福利系数) * min(
        (1 + 连续签到_收入奖励系数 * ComboDay),
        1 + 连续签到_最大收入奖励系数))
    AddAttitude = int(random.randint(日好感度 - 好感度波动幅度, 日好感度 + 好感度波动幅度) * min(
        (1 + 连续签到_好感度奖励系数 * ComboDay),
        (1 + 连续签到_最大好感度奖励系数)
    ))
    ComboDay = ComboDay + 1
    User.Money = User.Money + AddMoney * 100
    User.Attitude = User.Attitude + AddAttitude
    User.SignInDate = TodayStr + "@" + str(ComboDay)
    DB_User.updateUser(User)

    # 图片渲染
    if Mode.Zao:
        # zaozi版HTML渲染
        # 获取当前端口号
        conf = get_driver().config.dict()
        port = conf["port"]
        Ls = User.SignInDate.split("@")[0]
        url = f"127.0.0.1:{port}/ZSign/index.html?QQ={QQ}&&LastSignDate={Ls}" \
              f"&&AddGold={AddMoney}&&AddAttitude={AddAttitude}&&Gold={User.Money / 100}" \
              f"&&Attitude={User.Attitude}&&SignCombo={ComboDay}"
        image = await Web2ImgBytes(url=url, Path=f"./Data/SignIn/{QQ}.png", width=1280)
        # with open(f"./Data/SignIn/{QQ}.png", "wb") as f:
        #    f.write(image)
        msg = MessageSegment.at(QQ) + MessageSegment.image(image)
        await signIn.send(msg)
    else:
        # Sora版HTML渲染
        # 获取当前端口号
        conf = get_driver().config.dict()
        port = conf["port"]
        # 获取昵称
        if hasattr(event, "group_id"):
            Name = await GetQQGrouperName(bot=bot, QQ=QQ, Group=event.group_id)
        else:
            Name = await GetQQStrangerName(bot=bot, QQ=QQ)
        # 处理最后签到日期
        Ls = User.SignInDate.split("@")[0]
        url = f"127.0.0.1:{port}/Sign/Sign.html?QQ={QQ}&&Name={Name}&&LastSignDate={Ls}" \
              f"&&AddGold={AddMoney}&&AddAttitude={AddAttitude}&&Gold={User.Money / 100}" \
              f"&&Attitude={User.Attitude}&&HasSign=false&&SignCombo={ComboDay}"
        """
        Url示例
        http://127.0.0.1:12400/Sign/Sign.html?QQ=168934818&Name=Sora
        &&LastSignDate=2023/08/31&&AddGold=120&&Gold=420
        &&AddAttitude=20&&HasSign=true&&SignCombo=75&&Attitude=100
        """
        image = await Web2ImgBytes(url=url, width=1200)
        msg = MessageSegment.at(QQ) + MessageSegment.image(image)
        await signIn.send(msg)


@check.handle()
@logPluginExecuteTime
async def check(matcher: Matcher, event: MessageEvent):
    QQ = event.user_id
    User = DB_User.getUser(QQ)
    LastSignIn = str(User.SignInDate)
    ComboDay = 0
    # 未签到
    if LastSignIn == "":
        ComboDay = 0
    else:
        ComboDay = LastSignIn.split("@")[1]
        if not ComboDay.isdigit():
            ComboDay = 0
        else:
            ComboDay = int(ComboDay)
    message = MessageSegment.at(event.user_id) + MessageSegment.text(f"你的存款为{User.Money / 100}妃爱币\n"
                                                                     f"妃爱对你的好感度为{User.Attitude}\n"
                                                                     f"已连续签到{ComboDay}天")
    await matcher.send(message)
    return
