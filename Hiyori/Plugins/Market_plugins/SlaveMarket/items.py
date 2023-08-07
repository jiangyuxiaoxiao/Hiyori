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
from Hiyori.Utils.API.QQ import GetQQGrouperName
import Hiyori.Utils.Exception.MarketException as MarketException

from .Utils import SlaveUtils


def GroupEventCheck(matcher: Matcher, event: Event):
    if not isinstance(event, onebotV11.GroupMessageEvent):
        msg = f"请于群聊中使用该物品"
        await matcher.send(msg)
        raise MarketException.TypeErrorException()


class 重开模拟器(SingleItem):
    """仅适用于OnebotV11"""

    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        GroupEventCheck(matcher, event)  # 仅于群聊事件中可用
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
        msg = onebotV11.MessageSegment.at(QQ) + f"重开成功，当前基础属性为 颜值{int(attributes[0])} 智力{int(attributes[1])} 体质{int(attributes[2])}。"
        await matcher.send(msg)


class 世界线演算装置(SingleItem):
    """仅适用于OnebotV11"""

    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        GroupEventCheck(matcher, event)  # 仅于群聊事件中可用

        start = time.time_ns()
        item = DB_Item.getUserItem(QQ=QQ, ItemName="重开模拟器")
        if item.Quantity < 1:
            msg = onebotV11.MessageSegment.at(QQ) + "你没有重开模拟器，无法进行演算。"
            await matcher.send(msg)
            raise MarketException.ItemNotEnoughException(now=0, need=1)

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
        GroupEventCheck(matcher, event)  # 仅于群聊事件中可用
        GroupID = event.group_id

        # 修改属性
        slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
        ExtraInfo = SlaveUtils.GetExtraInfo(slave)
        # 添加标签
        if "现代世界观_人物标签" not in ExtraInfo.keys():
            ExtraInfo["现代世界观_人物标签"] = ["猫娘"]
        else:
            name = await GetQQGrouperName(bot=bot, QQ=QQ, Group=GroupID)
            if "猫娘" in ExtraInfo["现代世界观_人物标签"]:
                msg = f"{name}已经是猫娘了哦。"
                await matcher.send(msg)
                raise MarketException.UsageNotCorrectException()

            ExtraInfo["现代世界观_人物标签"].append("猫娘")
            # 使用物品
            await self.consume(QQ=QQ, Num=1)
            # 添加buff
            if "现代世界观_BUFF" not in ExtraInfo.keys():
                ExtraInfo["现代世界观_BUFF"] = {
                    "颜值": 2.0,
                    "智力": 1.0,
                    "体质": 0.7
                }
            else:
                ExtraInfo["现代世界观_BUFF"]["颜值"] *= 2.0
                ExtraInfo["现代世界观_BUFF"]["体质"] *= 0.7
            SlaveUtils.SaveExtraInfo(slave, ExtraInfo)
            # 添加技能
            SkillInfo = SlaveUtils.GetSkillInfo(slave=slave)
            if "给我变" not in SkillInfo:
                SkillInfo.append("给我变")
            SlaveUtils.SaveSkillInfo(slave=slave, SkillInfoList=SkillInfo)
            msg = f"一道光闪过，{name}变成了一只的猫娘，{name}看起来更可爱更娇弱了。"
            await matcher.send(msg)
