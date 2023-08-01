"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/8/1-21:15
@Desc: 妃爱回复
@Ver : 1.0.0
"""

from nonebot.plugin import on_command
from Hiyori.Utils.Priority import Priority
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Bot
import random
import pathlib
import os

reply = on_command("妃爱", block=True, priority=Priority.普通优先级)


@reply.handle()
async def _():
    message = "我在~"
    image = f"./Data/Reply/images/hiy{random.randint(1, 3)}.jpg"
    ImagePath = os.path.abspath(image)
    ImagePath = pathlib.Path(ImagePath).as_uri()
    msg = message + MessageSegment.image(ImagePath)
    await reply.send(msg)
