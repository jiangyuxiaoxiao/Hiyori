"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:43
@Desc: 妃爱商店物品功能实现
@Ver : 1.0.0
"""
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from Hiyori.Utils.Shop.items import UniqueItem


class 白银会员卡(UniqueItem):
    async def use(self, QQ: int, Targets: list[int], Num: int, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        await matcher.send("持有该会员卡在以下商店享受九折优惠：\n"
                           "1.群友商店\n"
                           "2.妃爱小卖部")
