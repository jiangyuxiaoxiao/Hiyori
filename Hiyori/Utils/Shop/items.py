"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/7-10:55
@Desc: 物品实现
@Ver : 1.0.0
"""
from nonebot.adapters import Bot, Event
import nonebot.adapters.onebot.v11 as onebotV11
from nonebot.typing import T_State
from nonebot.matcher import Matcher

from Hiyori.Utils.Database import DB_Item
import Hiyori.Utils.Exception.MarketException as MarketException

from . import Item


class UniqueItemException(MarketException):
    """唯一物品不可重复购买"""

    def __init__(self):
        self.ExceptInfo = f"唯一物品不可重复购买。"

    def __str__(self):
        return self.ExceptInfo


class UniqueItem(Item):
    # 唯一物品，不可重复购买
    def __init__(self, name: str, description: str = "", price: float = 10000, hasTarget: bool = False, need_attitude: int = 0, anonymous: bool = False,
                 Functions: dict[str, any] = None):
        super().__init__(name, description, price, hasTarget, need_attitude, anonymous, Functions)

    async def beforePurchase(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
                             state: T_State = None):
        item = DB_Item.getUserItem(QQ, self.name)
        if item.Quantity != 0:
            # 多适配器判断
            if isinstance(event, onebotV11.Event):
                msg = onebotV11.MessageSegment.at(QQ) + f"唯一物品，不可重复购买。"
            else:
                msg = f"唯一物品，不可重复购买。"
            await matcher.send(msg)
            raise UniqueItemException


class SingleItem(Item):
    # 一次只能使用一个的物品
    async def beforeUse(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
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
            raise MarketException.ItemNumNotCorrectException()
        # 使用的物品数量大于持有的物品数量
        item = DB_Item.getUserItem(QQ=QQ, ItemName=self.name)
        if item.Quantity < 1:
            # 多适配器判断
            if isinstance(event, onebotV11.Event):
                msg = onebotV11.MessageSegment.at(QQ) + f"你的{self.name}数量不够，需要1个{self.name}。"
            else:
                msg = f"你的{self.name}数量不够，需要1个{self.name}。"
            await matcher.send(msg)
            raise MarketException.ItemNotEnoughException(now=item.Quantity, need=1)


