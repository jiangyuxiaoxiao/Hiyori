"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/10-12:52
@Desc: 
@Ver : 1.0.0
"""
from nonebot.adapters.onebot.v11 import GroupRecallNoticeEvent, Event


async def isGroupRecallNoticeEvent(event: Event) -> bool:
    if isinstance(event, GroupRecallNoticeEvent):
        return True
    return False
