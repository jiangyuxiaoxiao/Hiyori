"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/6-17:26
@Desc: 翻译插件
@Ver : 1.0.0
"""
import re

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent
from Hiyori.Utils.API.Baidu.OpenTranslate import Translate
from .hook import cantonese
from .shop import TranslateShopInit

speakCantonese = on_regex("^说粤语", block=False)

TranslateShopInit()


@speakCantonese.handle()
async def _(event: MessageEvent):
    msg = event.message.extract_plain_text()
    msg = re.sub(pattern="^说粤语", repl="", string=msg)
    msg = await Translate(Sentence=msg, to_Language="yue")
    await speakCantonese.send(msg)
