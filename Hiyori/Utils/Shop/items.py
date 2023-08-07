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
from Hiyori.Utils.Exception.MarketException import MarketException

from . import Item


class UniqueItemException(MarketException):
    """唯一物品不可重复购买"""

    def __init__(self):
        self.ExceptInfo = f"唯一物品不可重复购买。"

    def __str__(self):
        return self.ExceptInfo


class 唯一物品(Item):
    def __init__(self, name: str, description: str = "", price: float = 10000, hasTarget: bool = False, need_attitude: int = 0, anonymous: bool = False,
                 Functions: dict[str, any] = None):
        super().__init__(name, description, price, hasTarget, need_attitude, anonymous, Functions)

    async def beforePurchase(self, QQ: int, Targets: list[int], Num: int, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        item = DB_Item.getUserItem(QQ, self.name)
        if item.Quantity != 0:
            # 多适配器判断
            if isinstance(event, onebotV11.Event):
                msg = onebotV11.MessageSegment.at(QQ) + f"唯一物品，不可重复购买。"
            else:
                msg = f"唯一物品，不可重复购买。"
            await matcher.send(msg)
            raise UniqueItemException
