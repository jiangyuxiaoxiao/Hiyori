"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:45
@Desc: 商店功能封装
@Ver : 1.0.0
"""
from typing import Callable
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import nonebot.adapters.onebot.v11 as onebotV11
from Hiyori.Utils.Exception.Market import *
from Hiyori.Utils.Database import DB_User, DB_Item


# 商品
class Item:
    def __init__(self, name: str, description: str = "", price: float = 10000,
                 hasTarget: bool = False, need_attitude: int = 0, anonymous: bool = False,
                 Functions: dict[str, any] = None):

        self.name: str = name  # 商品名
        self.description: str = description  # 商品描述
        self.price: float = price  # 商品价格，注意价格的最小单位为0.01，小于0.01的值将被抹去
        self.hasTarget: bool = hasTarget  # 有作用对象
        self.need_attitude: int = need_attitude  # 购买有好感度需求
        self.anonymous: bool = anonymous  # 隐式商品
        self.Functions: dict[str, any] = Functions

    async def beforePurchase(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
                             state: T_State = None):
        """购买前触发函数"""
        user = DB_User.getUser(QQ)
        # 好感度检查
        if user.Attitude < self.need_attitude:
            # 多适配器判断
            if isinstance(event, onebotV11.Event):
                msg = onebotV11.MessageSegment.at(QQ) + f"你的好感度不够哦，需要{self.need_attitude}好感度，当前好感度{user.Attitude}。"
            else:
                msg = f"你的好感度不够哦，需要{self.need_attitude}好感度，当前好感度{user.Attitude}。"
            await matcher.send(msg)
            raise AttitudeNotEnoughException(user.Attitude, self.need_attitude)
        # 物品名检查

    async def purchase(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
                       state: T_State = None):
        """购买触发函数"""
        money = 折扣系数计算(QQ=QQ, ItemName=self.name) * Num * self.price
        if not DB_User.spendMoney(QQ=QQ, Money=money):
            user = DB_User.getUser(QQ)
            # 多适配器判断
            if isinstance(event, onebotV11.Event):
                msg = onebotV11.MessageSegment.at(QQ) + f"你的妃爱币不够哦，需要{money}妃爱币，当前持有{user.Money / 100}。"
            else:
                msg = f"你的妃爱币不够哦，需要{money}妃爱币，当前持有{user.Money / 100}"
            await matcher.send(msg)
            # 抛出异常
            raise MoneyNotEnoughException(own=user.Money / 100, need=money)
        else:
            user = DB_User.getUser(QQ)
            # 修改数量
            item = DB_Item.getUserItem(QQ=QQ, ItemName=self.name)
            item.Quantity += Num
            item.save()
            # 多适配器判断
            if isinstance(event, onebotV11.Event):
                msg = onebotV11.MessageSegment.at(QQ) + f"购买成功，花费{money}妃爱币，剩余{user.Money / 100}妃爱币。当前持有{self.name} {item.Quantity}个"
            else:
                msg = f"购买成功，花费{money}妃爱币，剩余{user.Money / 100}妃爱币。"
            await matcher.send(msg)

    async def afterPurchase(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
                            state: T_State = None):
        """购买后触发函数"""
        pass

    async def consume(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
                      state: T_State = None):
        """消耗物品执行函数"""
        item = DB_Item.getUserItem(QQ=QQ, ItemName=self.name)
        # 由于已经在beforeUse时检查了使用物品数量，此处不再检查，beforeUse被重写时需留心
        item.Quantity -= Num
        item.save()

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
            raise UsageNotCorrectException()
        # 最少使用一个
        if Num <= 0:
            # 多适配器判断
            if isinstance(event, onebotV11.Event):
                msg = onebotV11.MessageSegment.at(QQ) + f"至少需要使用一个{self.name}哦"
            else:
                msg = f"至少需要使用一个{self.name}哦"
            await matcher.send(msg)
            raise UsageNotCorrectException()
        # 使用的物品数量大于持有的物品数量
        item = DB_Item.getUserItem(QQ=QQ, ItemName=self.name)
        if item.Quantity < Num:
            # 多适配器判断
            if isinstance(event, onebotV11.Event):
                msg = onebotV11.MessageSegment.at(QQ) + f"你的物品数量不够，需要{Num}个物品，当前持有{item.Quantity}。"
            else:
                msg = f"你的{self.name}数量不够，需要{Num}个，当前持有{item.Quantity}。"
            await matcher.send(msg)
            raise ItemNotEnoughException(now=item.Quantity, need=Num)

    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        """使用触发函数"""
        msg = self.description
        await matcher.send(msg)

    async def afterUse(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
                       state: T_State = None):
        """使用后触发函数"""
        pass

    async def autoEffect(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None):
        """待定"""
        pass


# 商店
class Shop:
    def __init__(self, name: str, description: str = "", anonymous: bool = False):
        self.name = name  # 商店名
        self.description = description  # 商店描述
        self.items: dict[str, Item] = dict()
        self.anonymous = anonymous  # 隐式商店

    # 添加商品
    def addItem(self, item: Item):
        self.items[item.name] = item


# 总商店
class Shops:
    shops: dict[str, Shop] = dict()
    items: dict[str, Item] = dict()

    # 添加商店
    @staticmethod
    def addShop(shop: Shop):
        Shops.shops[shop.name] = shop
        # 将物品添加进总物品表中
        for shopItem in shop.items.values():
            Shops.items[shopItem.name] = shopItem


def 折扣系数计算(QQ: int, ItemName: str) -> float:
    # if ItemName in Shops.shops["群友"].items.keys() or ItemName in Shops.shops["妃爱"].items.keys():
    if ItemName in Shops.shops["妃爱商店"].items.keys() or ItemName in Shops.shops["群友商店"].items.keys():
        if DB_Item.hasItem(QQ=QQ, ItemName="白银会员卡"):
            return 0.9
        if DB_Item.hasItem(QQ=QQ, ItemName="萝了吗白银会员卡"):
            return 0.9
    return 1


def hasItem(QQ: int, ItemName: str) -> bool:
    item = DB_Item.getUserItem(QQ, ItemName)
    if item.Quantity == 0:
        return False
    return True
