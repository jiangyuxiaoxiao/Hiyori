"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/7-19:26
@Desc: 
@Ver : 1.0.0
"""
import numpy
from datetime import datetime, timedelta
import time

from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import nonebot.adapters.onebot.v11 as onebotV11

from Hiyori.Utils.Database import DB_User, DB_slave, DB_Item
from Hiyori.Utils.Shop.items import UniqueItem, SingleItem
from Hiyori.Utils.Shop import Item
from Hiyori.Utils.Shop.decorators import singleItem
from Hiyori.Utils.API.QQ import GetQQGrouperName
from Hiyori.Utils.Exception.Market import *

from .Utils import SlaveUtils


async def GroupEventCheck(matcher: Matcher, event: Event):
    if not isinstance(event, onebotV11.GroupMessageEvent):
        msg = f"请于群聊中使用该物品"
        await matcher.send(msg)
        raise TypeErrorException()


class 重开模拟器(SingleItem):
    """仅适用于OnebotV11"""

    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        await GroupEventCheck(matcher, event)  # 仅于群聊事件中可用
        await self.consume(QQ=QQ, Num=1)  # 消耗物品
        # 获取属性
        GroupID = event.group_id
        slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
        SlaveUtils.获取现代世界观属性(slave)
        ExtraInfo = SlaveUtils.GetExtraInfo(slave)
        # 随机生成属性
        attributes = numpy.random.normal(loc=100, size=3, scale=20)
        for index in range(0, 3):
            if attributes[index] < 0:
                attributes[index] = 0
            if attributes[index] > 200:
                attributes[index] = 200
        ExtraInfo["现代世界观_通常属性"] = {
            "颜值": int(attributes[0]),
            "智力": int(attributes[1]),
            "体质": int(attributes[2]),
            "version": 2.0
        }
        SlaveUtils.SaveExtraInfo(slave, ExtraInfo)
        msg = onebotV11.MessageSegment.at(QQ) + f"重开成功，当前基础属性为 颜值{int(attributes[0])} 智力{int(attributes[1])} 体质{int(attributes[2])}。"
        await matcher.send(msg)


class 世界线演算装置(SingleItem):
    """仅适用于OnebotV11"""

    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        await GroupEventCheck(matcher, event)  # 仅于群聊事件中可用

        start = time.time_ns()
        item = DB_Item.getUserItem(QQ=QQ, ItemName="重开模拟器")
        if item.Quantity < 1:
            msg = onebotV11.MessageSegment.at(QQ) + "你没有重开模拟器，无法进行演算。"
            await matcher.send(msg)
            raise ItemNotEnoughException(now=0, need=1)

        # 若不存在属性则进行生成
        slave = DB_slave.getUser(QQ=QQ, GroupID=event.group_id)
        SlaveUtils.获取现代世界观属性(slave)
        ExtraInfo = SlaveUtils.GetExtraInfo(slave)
        # 消耗所有重开模拟器取最大值进行生成
        number = item.Quantity
        item.Quantity = 0
        item.save()
        # 消耗一个演算装置
        await self.consume(QQ=QQ, Num=1)
        # 计算
        颜值 = ExtraInfo["现代世界观_通常属性"]["颜值"]
        智力 = ExtraInfo["现代世界观_通常属性"]["智力"]
        体质 = ExtraInfo["现代世界观_通常属性"]["体质"]
        attributes = numpy.random.normal(loc=100, size=(number, 3), scale=20)
        Max = numpy.max(attributes, axis=0)
        颜值 = int(max(颜值, Max[0]))
        智力 = int(max(智力, Max[1]))
        体质 = int(max(体质, Max[2]))
        ExtraInfo["现代世界观_通常属性"]["颜值"] = 颜值
        ExtraInfo["现代世界观_通常属性"]["智力"] = 智力
        ExtraInfo["现代世界观_通常属性"]["体质"] = 体质
        end = time.time_ns()
        t = end - start
        if t > 1000000000:
            timeStr = f"用时{round(t / 1000000000, 3)}s"
        elif t > 1000000:
            timeStr = f"用时{round(t / 1000000, 3)}ms"
        else:
            timeStr = f"用时{round(t / 1000, 3)}us"
        SlaveUtils.SaveExtraInfo(slave, ExtraInfo)
        msg = onebotV11.MessageSegment.at(QQ) + f"世界线演算成功，{timeStr}，消耗重开模拟器{number}个。当前基础属性为 颜值{颜值} 智力{智力} 体质{体质}。"
        await matcher.send(msg)


class 猫娘变身器(SingleItem):
    """仅适用于OnebotV11"""

    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        await GroupEventCheck(matcher, event)  # 仅于群聊事件中可用
        GroupID = event.group_id

        # 修改属性
        slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
        ExtraInfo = SlaveUtils.GetExtraInfo(slave)
        name = await GetQQGrouperName(bot=bot, QQ=QQ, Group=GroupID)
        # 添加标签
        if "现代世界观_人物标签" not in ExtraInfo.keys():
            ExtraInfo["现代世界观_人物标签"] = ["猫娘"]
        else:
            if "猫娘" in ExtraInfo["现代世界观_人物标签"]:
                msg = f"{name}已经是猫娘了哦。"
                await matcher.send(msg)
                raise UsageNotCorrectException()
            ExtraInfo["现代世界观_人物标签"].append("猫娘")

        # 添加buff
        if "现代世界观_BUFF" not in ExtraInfo.keys():
            ExtraInfo["现代世界观_BUFF"] = {
                "颜值": 30,
                "智力": 0,
                "体质": -15,
                "version": 3.2
            }
        else:
            ExtraInfo["现代世界观_BUFF"]["颜值"] = int(ExtraInfo["现代世界观_BUFF"]["颜值"] + 30)
            ExtraInfo["现代世界观_BUFF"]["体质"] = int(ExtraInfo["现代世界观_BUFF"]["体质"] - 15)
        SlaveUtils.SaveExtraInfo(slave, ExtraInfo)

        # 添加技能
        SkillInfo = SlaveUtils.GetSkillInfo(slave=slave)
        if "给我变" not in SkillInfo:
            SkillInfo.append("给我变")
        SlaveUtils.SaveSkillInfo(slave=slave, SkillInfoList=SkillInfo)

        # 使用物品
        await self.consume(QQ=QQ, Num=1)
        msg = f"一道光闪过，【{name}】变成了一只的猫娘，【{name}】看起来更可爱更娇弱了。"
        await matcher.send(msg)


class 白丝连裤袜(SingleItem):
    """仅适用于OnebotV11"""

    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        await GroupEventCheck(matcher, event)  # 仅于群聊事件中可用
        GroupID = event.group_id
        slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
        ExtraInfo = SlaveUtils.GetExtraInfo(slave)
        # 添加标签
        name = await GetQQGrouperName(bot=bot, QQ=QQ, Group=GroupID)
        if "现代世界观_人物标签" not in ExtraInfo.keys():
            ExtraInfo["现代世界观_人物标签"] = ["白丝jiojio"]
        else:
            if "白丝jiojio" in ExtraInfo["现代世界观_人物标签"]:
                msg = f"【{name}】已经穿上白丝了哦。"
                await matcher.send(msg)
                raise UsageNotCorrectException()
            ExtraInfo["现代世界观_人物标签"].append("白丝jiojio")

        # 添加buff
        if "现代世界观_BUFF" not in ExtraInfo.keys():
            ExtraInfo["现代世界观_BUFF"] = {
                "颜值": 20,
                "智力": 0,
                "体质": 0,
                "version": 3.2
            }
        else:
            ExtraInfo["现代世界观_BUFF"]["颜值"] = int(ExtraInfo["现代世界观_BUFF"]["颜值"] + 20)
        SlaveUtils.SaveExtraInfo(slave, ExtraInfo)

        # 使用物品
        await self.consume(QQ=QQ, Num=1)

        msg = f"【{name}】四处张望发现没人后，偷偷从包里摸出来一双白丝，轻轻展开，拉到膝盖处，再慢慢拉上大腿。" \
              f"细腻丝滑的袜子包裹摩擦着【{name}】的双腿，她的脸颊逐渐泛起一层淡淡的粉红色。。。"
        await matcher.send(msg)


class 灵魂宝石(UniqueItem):
    """仅适用于OnebotV11"""

    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        await GroupEventCheck(matcher, event)  # 仅于群聊事件中可用
        GroupID = event.group_id
        slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
        ExtraInfo = SlaveUtils.GetExtraInfo(slave)
        # 添加标签
        if "现代世界观_人物标签" not in ExtraInfo.keys():
            ExtraInfo["现代世界观_人物标签"] = ["魔法少女"]
        else:
            name = await GetQQGrouperName(bot=bot, QQ=QQ, Group=GroupID)
            if "魔法少女" in ExtraInfo["现代世界观_人物标签"]:
                msg = f"【{name}】已经是魔法少女了。"
                await matcher.send(msg)
                raise UsageNotCorrectException()

            ExtraInfo["现代世界观_人物标签"].append("魔法少女")

        # 添加buff
        if "现代世界观_BUFF" not in ExtraInfo.keys():
            ExtraInfo["现代世界观_BUFF"] = {
                "颜值": 0,
                "智力": 0,
                "体质": 40,
                "version": 3.2
            }
        else:
            ExtraInfo["现代世界观_BUFF"]["体质"] = int(ExtraInfo["现代世界观_BUFF"]["体质"] + 40)
        SlaveUtils.SaveExtraInfo(slave, ExtraInfo)

        # 添加技能
        SkillInfo = SlaveUtils.GetSkillInfo(slave=slave)
        if "魔女狩猎" not in SkillInfo:
            SkillInfo.append("魔女狩猎")
        SlaveUtils.SaveSkillInfo(slave=slave, SkillInfoList=SkillInfo)

        name = await GetQQGrouperName(bot=bot, QQ=QQ, Group=GroupID)
        msg = f"【{name}】与名为丘比的神秘生物签订了魔法契约获得了强大的力量。然而，奇迹与魔法并不是免费的，" \
              "祈求希望的同时也会散布同样分量的绝望。。。"
        await matcher.send(msg)


class 粉色项圈(Item):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):

        await GroupEventCheck(matcher, event)  # 仅于群聊事件中可用
        GroupID = event.group_id
        # 未制定对象则指向自己，否则指向老婆
        slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
        if len(Targets) != 0:
            slave = DB_slave.getUser(QQ=Targets[0], GroupID=GroupID)
            if SlaveUtils.结婚对象(slave) != QQ:
                msg = onebotV11.MessageSegment.at(QQ) + "不能对你或你老婆以外的人使用哦"
                await matcher.send(msg)
                raise UsageNotCorrectException()

        slaveInfo = SlaveUtils.GetExtraInfo(slave)
        Today = datetime.now()
        if "签约期" not in slaveInfo:
            DeadLine = Today + timedelta(days=Num)
        else:
            OldDeadLine = datetime.strptime(slaveInfo["签约期"], "%Y-%m-%d %H:%M:%S")
            DeadLine = max(OldDeadLine, Today) + timedelta(days=Num)
        slaveInfo["签约期"] = DeadLine.strftime("%Y-%m-%d %H:%M:%S")
        SlaveUtils.SaveExtraInfo(slave=slave, ExtraInfoDict=slaveInfo)
        await self.consume(QQ=QQ, Num=Num)
        timeStr = DeadLine.strftime("%Y年%m月%d日%H时 %M:%S")
        name = await GetQQGrouperName(bot=bot, QQ=QQ, Group=GroupID)
        if len(Targets) == 0:
            msg = f"{name}为自己带上了粉色项圈，直到" + timeStr + "前有效~"
        else:
            targetName = await GetQQGrouperName(bot=bot, QQ=Targets[0], Group=GroupID)
            msg = f"{name}为{targetName}带上了粉色项圈，直到" + timeStr + "前有效~"
        await matcher.send(msg)


def 项圈状态查询(QQ: int, GroupID: int) -> (bool, str):
    """
    查询用户当前是否被项圈束缚

    :param QQ: 用户QQ
    :param GroupID: 用户群组
    :return: 是否被束缚 True: 被束缚 （返回截止日期） False: 未被束缚
    """
    slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
    slaveInfo = SlaveUtils.GetExtraInfo(slave)
    if "签约期" not in slaveInfo:
        return False, ""
    else:
        Today = datetime.now()
        DeadLine = datetime.strptime(slaveInfo["签约期"], "%Y-%m-%d %H:%M:%S")
        if Today > DeadLine:
            return False, ""
        else:
            return True, DeadLine.strftime("%Y年%m月%d日%H时 %M:%S")


class 结婚戒指(UniqueItem):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        await GroupEventCheck(matcher, event)  # 仅于群聊事件中可用
        GroupID = event.group_id
        # 检查双方状态
        求婚者 = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
        求婚者状态 = SlaveUtils.GetExtraInfo(求婚者)
        被求婚者 = DB_slave.getUser(QQ=Targets[0], GroupID=GroupID)
        被求婚者状态 = SlaveUtils.GetExtraInfo(被求婚者)
        targetName = await GetQQGrouperName(bot=bot, QQ=Targets[0], Group=GroupID)
        name = await GetQQGrouperName(bot=bot, QQ=QQ, Group=GroupID)
        if "结婚状态" not in 求婚者状态.keys():
            求婚者状态["结婚状态"] = "未婚"
            SlaveUtils.SaveExtraInfo(求婚者, 求婚者状态)
        if "结婚状态" not in 被求婚者状态.keys():
            被求婚者状态["结婚状态"] = "未婚"
            SlaveUtils.SaveExtraInfo(被求婚者, 被求婚者状态)
        # 获取状态
        求婚者结婚状态: str = 求婚者状态["结婚状态"]
        被求婚者结婚状态: str = 被求婚者状态["结婚状态"]
        # 检查已婚
        if 求婚者结婚状态.startswith("已婚"):
            msg = "爬，你已经结过婚了"
            await matcher.send(msg)
            raise UsageNotCorrectException()
        if 被求婚者结婚状态.startswith("已婚"):
            msg = f"{targetName}已结婚了哦"
            await matcher.send(msg)
            raise UsageNotCorrectException()
        # 检查求婚
        if 被求婚者结婚状态.startswith("求婚"):
            求婚目标 = 被求婚者结婚状态.split(" ")[1]
            if 求婚目标 == str(QQ):
                # 双方互相指定，成功结婚
                # 保存结婚状态
                求婚者状态["结婚状态"] = f"已婚 {Targets[0]}"
                被求婚者状态["结婚状态"] = f"已婚 {QQ}"
                SlaveUtils.SaveExtraInfo(求婚者, 求婚者状态)
                SlaveUtils.SaveExtraInfo(被求婚者, 被求婚者状态)
                # 处理结婚动作
                # - 取消当前主人
                求婚者.Owner = 0
                被求婚者.Owner = 0
                求婚者.save()
                被求婚者.save()
                # 发送结婚结果
                msg = f"恭喜{name}与{targetName}结婚成功~"
                await matcher.send(msg)
                return
        求婚者状态["结婚状态"] = f"求婚 {Targets[0]}"
        SlaveUtils.SaveExtraInfo(求婚者, 求婚者状态)
        msg = f"求婚成功，请等待{targetName}的回应吧！"
        await matcher.send(msg)
        return
