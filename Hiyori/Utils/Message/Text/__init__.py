"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/8/7-13:55
@Desc: 
@Ver : 1.0.0
"""
from typing import Union
from nonebot.adapters.onebot.v11 import Message

try:
    import ujson as json
except ModuleNotFoundError:
    import json


def get_message_text(data: Union[str, Message]) -> str:
    """
    说明:
        获取消息中 纯文本 的信息
    参数:
        :param data: event.json()
    """
    result = ""
    if isinstance(data, str):
        event = json.loads(data)
        if data and (message := event.get("message")):
            if isinstance(message, str):
                return message.strip()
            for msg in message:
                if msg["type"] == "text":
                    result += msg["data"]["text"].strip() + " "
        return result.strip()
    else:
        for seg in data["text"]:
            result += seg.data["text"] + " "
    return result.strip()