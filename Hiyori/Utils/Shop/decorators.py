"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/8-9:35
@Desc: 装饰器 用于定义物品的某些特性
@Ver : 1.0.0
"""
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import nonebot.adapters.onebot.v11 as onebotV11

from Hiyori.Utils.Database import DB_User, DB_Item
import Hiyori.Utils.Exception.Market as Market


# 独特物品，请在beforePurchase函数上装饰
def uniqueItem(beforePurchase):
    async def uniqueCheck(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
                          state: T_State = None):
        item = DB_Item.getUserItem(QQ, self.name)
        if item.Quantity != 0:
            # 多适配器判断
            if isinstance(event, onebotV11.Event):
                msg = onebotV11.MessageSegment.at(QQ) + f"唯一物品，不可重复购买。"
            else:
                msg = f"唯一物品，不可重复购买。"
            await matcher.send(msg)
            raise Market.UniqueItemException()
        return beforePurchase(self, QQ, Targets, Num, bot, event, matcher, state)
    return uniqueCheck


# 一次仅可使用一个的物品，请在beforeUse函数上装饰
def singleItem(beforeUse):
    async def singleCheck(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
                          state: T_State = None):
        """使用前触发函数"""
        # 物品注册时写明了需要使用对象，然而没有传入使用对象
        if self.hasTarget and len(Targets) == 0:
            # 多适配器判断
            if isinstance(event, onebotV11.Event):
                msg = onebotV11.MessageSegment.at(QQ) + f"需要指定使用对象"
            else:
                msg = f"需要指定使用对象"
            await matcher.send(msg)
        # 使用物品数量不为1
        if Num != 1:
            if isinstance(event, onebotV11.Event):
                msg = onebotV11.MessageSegment.at(QQ) + f"一次只能使用一个{self.name}哦"
            else:
                msg = f"一次只能使用一个{self.name}哦"
            await matcher.send(msg)
            raise Market.ItemNumNotCorrectException()
        # 使用的物品数量大于持有的物品数量
        item = DB_Item.getUserItem(QQ=QQ, ItemName=self.name)
        if item.Quantity < 1:
            # 多适配器判断
            if isinstance(event, onebotV11.Event):
                msg = onebotV11.MessageSegment.at(QQ) + f"你的{self.name}数量不够，需要1个{self.name}。"
            else:
                msg = f"你的{self.name}数量不够，需要1个{self.name}。"
            await matcher.send(msg)
            raise Market.ItemNotEnoughException(now=item.Quantity, need=1)
        return beforeUse(self, QQ, Targets, Num, bot, event, matcher, state)
    return singleCheck