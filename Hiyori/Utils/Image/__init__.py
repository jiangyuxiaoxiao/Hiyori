"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/8/1-21:40
@Desc: 
@Ver : 1.0.0
"""
from typing import List,Union
from nonebot.adapters.onebot.v11 import Message
import json
def get_message_img(data: Union[str, Message]) -> List[str]:
    """
    说明:
        获取消息中所有的 图片 的链接
    参数:
        :param data: event.json()
    """
    img_list = []
    if isinstance(data, str):
        event = json.loads(data)
        if data and (message := event.get("message")):
            for msg in message:
                if msg["type"] == "image":
                    img_list.append(msg["data"]["url"])
    else:
        for seg in data["image"]:
            img_list.append(seg.data["url"])
    return img_list