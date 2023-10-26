"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:33
@Desc: 
@Ver : 1.0.0
"""
from nonebot.message import run_preprocessor
from nonebot.matcher import Matcher
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment
import datetime
from Hiyori.Utils.Database import DB_User

Config = get_driver().config
计算周期 = 5


# 群组CD计时器，其中CD为群组的冷却总权重（五分钟），lastTime为群聊/个人上一次触发的时间，格式是"%Y-%m-%d %H:%M:%S"
class CD_Counter:
    def __init__(self, ID: int, Name: str, CD: int, lastTime: str):
        self.ID = ID
        self.Name = Name
        self.CD = CD
        self.lastTime = lastTime
        self.hasSendInfo = False


driver = get_driver()
# CD统计
GroupsCD: dict[int, CD_Counter] = dict()
UsersCD: dict[int, CD_Counter] = dict()


@run_preprocessor
async def 功能调用CD检查(matcher: Matcher, bot: Bot, event: Event):
    global Config
    # 对于已关机的群聊直接返回
    if hasattr(event, "group_id"):
        GroupID = event.group_id
        Status = DB_User.getGroup(GroupID).Status
        if Status == "off":
            return
    # 对于没有元数据的插件，不进行CD调用检查
    if not hasattr(matcher.plugin.metadata, "extra"):
        return
    Data = matcher.plugin.metadata.extra
    # 若插件不支持CD权重则不启用
    if "CD_Weight" not in Data.keys():
        return
    CD_Weight = Data["CD_Weight"]
    if "CD" in matcher.state:
        CD_Weight = matcher.state["CD"]
    Time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 个人CD审查
    if hasattr(event, "user_id"):
        QQ = event.user_id
        # 不审查owner用户
        if DB_User.isOwner(QQ) or (QQ in Config.superusers):
            return
        User = DB_User.getUser(QQ)
        Max_CD = User.CD * 计算周期
        # 检查是否在字典中，不存在则添加
        if QQ not in UsersCD:
            UsersCD[QQ] = CD_Counter(ID=QQ, Name=User.Name, CD=0, lastTime=Time)
        # 权重累积计算
        # 计算间隔
        timeBefore = datetime.datetime.strptime(UsersCD[QQ].lastTime, "%Y-%m-%d %H:%M:%S")
        timeNow = datetime.datetime.now()
        seconds = (timeNow - timeBefore).seconds
        logger.debug(f"个人触发CD累积：【{QQ}】 seconds:{seconds},CD{UsersCD[QQ].CD},Max_CD{User.CD * 计算周期}")
        if seconds >= 计算周期 * 60:
            # 对于第一次响应，无论权重大小，均会响应
            UsersCD[QQ].lastTime = Time
            UsersCD[QQ].CD = CD_Weight
            UsersCD[QQ].hasSendInfo = False
        elif Max_CD < CD_Weight + UsersCD[QQ].CD:
            if not UsersCD[QQ].hasSendInfo:
                # 提示信息仅发送一次
                message = MessageSegment.at(event.user_id) + "个人功能调用已超出权重上限，请稍后使用哦。"
                await matcher.send(message)
                UsersCD[QQ].hasSendInfo = True
            raise IgnoredException("个人功能调用超出权重上限")
        else:
            UsersCD[QQ].CD = UsersCD[QQ].CD + CD_Weight
    # 群CD审查
    if hasattr(event, "group_id"):
        GroupID = event.group_id
        Group = DB_User.getGroup(GroupID)
        Max_CD = Group.CD * 计算周期
        # 检查是否在字典中，不存在则添加
        if GroupID not in GroupsCD:
            GroupsCD[GroupID] = CD_Counter(ID=GroupID, Name=Group.GroupName, CD=0, lastTime=Time)
        # 权重累积计算
        # 计算间隔
        timeBefore = datetime.datetime.strptime(GroupsCD[GroupID].lastTime, "%Y-%m-%d %H:%M:%S")
        timeNow = datetime.datetime.now()
        seconds = (timeNow - timeBefore).seconds
        logger.debug(f"群组触发CD累积：【{GroupID}】 seconds:{seconds},CD{GroupsCD[GroupID].CD},Max_CD{Group.CD * 计算周期}")
        if seconds >= 计算周期 * 60:
            # 对于第一次响应，无论权重大小，均会响应
            GroupsCD[GroupID].lastTime = Time
            GroupsCD[GroupID].CD = CD_Weight
            GroupsCD[GroupID].hasSendInfo = False
        elif Max_CD < CD_Weight + GroupsCD[GroupID].CD:
            if not GroupsCD[GroupID].hasSendInfo:
                # 提示信息仅发送一次
                await matcher.send("群聊功能调用已超出权重上限，请稍后使用哦。")
                GroupsCD[GroupID].hasSendInfo = True
            raise IgnoredException("群聊功能调用超出权重上限")
        else:
            GroupsCD[GroupID].CD = GroupsCD[GroupID].CD + CD_Weight
