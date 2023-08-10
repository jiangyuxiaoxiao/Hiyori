"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/10-12:40
@Desc: 
@Ver : 1.0.0
"""
from nonebot.adapters.onebot.v11 import PokeNotifyEvent, Event


async def isPokeEvent(event: Event) -> bool:
    if isinstance(event, PokeNotifyEvent):
        return True
    return False

