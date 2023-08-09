"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/8/7-12:10
@Desc: 
@Ver : 1.0.0
"""
from typing import List

from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageEvent
from nonebot.rule import to_me

from .config import TEXT_FILTER
from Hiyori.Utils.Message.Image import get_message_img
from Hiyori.Utils.Message.Text import get_message_text
from Hiyori.Utils.Database import DB_User

from .data_source import get_chat_result, hello, no_result

ai = on_message(rule=to_me(), priority=998)


@ai.handle()
async def _(bot: Bot, event: MessageEvent):
    User = DB_User.getUser(QQ=event.user_id)
    nickname = User.NickName
    msg = get_message_text(event.json())
    img = get_message_img(event.json())
    if "CQ:xml" in str(event.get_message()):
        return
    # 打招呼
    if (not msg and not img) or msg in [
        "你好啊",
        "你好",
        "在吗",
        "在不在",
        "您好",
        "您好啊",
        "你好",
        "在",
    ]:
        await ai.finish(hello())
    img = img[0] if img else ""
    if not nickname:
        if isinstance(event, GroupMessageEvent):
            nickname = event.sender.card or event.sender.nickname
        else:
            nickname = event.sender.nickname
    result = await get_chat_result(msg, img, event.user_id, nickname)
    print(
        f"USER {event.user_id} GROUP {event.group_id if isinstance(event, GroupMessageEvent) else ''} "
        f"问题：{msg} ---- 回答：{result}"
    )
    if result:
        result = str(result)
        for t in TEXT_FILTER:
            result = result.replace(t, "*")
        await ai.finish(Message(result))
    else:
        await ai.finish(no_result())
