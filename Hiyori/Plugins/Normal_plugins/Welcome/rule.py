"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/10-12:48
@Desc: 
@Ver : 1.0.0
"""
from nonebot.adapters.onebot.v11 import Event, GroupIncreaseNoticeEvent


async def isGroupIncreaseNoticeEvent(event: Event) -> bool:
    if isinstance(event, GroupIncreaseNoticeEvent):
        return True
    return False
