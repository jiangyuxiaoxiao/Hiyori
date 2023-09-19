"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:43
@Desc: 妃爱商店物品功能实现
@Ver : 1.0.0
"""
import random

from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import MessageSegment

from Hiyori.Utils.Shop.items import UniqueItem
from Hiyori.Utils.Shop import Item
from Hiyori.Utils.Database import DB_Item


class 白银会员卡(UniqueItem):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        await matcher.send("持有该会员卡在以下商店享受九折优惠：\n"
                           "1.群友商店\n"
                           "2.妃爱小卖部")


class 神秘模块抽奖券(Item):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        # 奖池 pool
        pool: list[str] = ["文言文翻译模块", "广东话翻译模块", "英语翻译模块", "韩语翻译模块", "德语翻译模块", "日语翻译模块", "法语翻译模块", "俄语翻译模块",
                           "中文翻译模块"]
        result: dict[str, int] = {}
        for i in range(Num):
            getItem = random.choice(pool)
            if getItem not in result.keys():
                result[getItem] = 1
            else:
                result[getItem] += 1
        resultMsg = MessageSegment.at(QQ) + "当前抽奖结果：\n"
        for itemName, itemNum in result.items():
            item = DB_Item.getUserItem(QQ, itemName)
            item.Quantity += itemNum
            item.save()
            resultMsg += f"{itemName}：{itemNum}个\n"
        item = DB_Item.getUserItem(QQ, "神秘模块抽奖券")
        item.Quantity -= Num
        item.save()
        await matcher.send(resultMsg)
