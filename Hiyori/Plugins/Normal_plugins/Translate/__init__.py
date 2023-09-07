"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/6-17:26
@Desc: 翻译插件
@Ver : 1.0.0
"""
import re

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, Message, MessageSegment
from Hiyori.Utils.API.Baidu.OpenTranslate import Translate

speakCantonese = on_regex("^说粤语", block=False)


@speakCantonese.handle()
async def _(event: MessageEvent):
    msg = event.message.extract_plain_text()
    msg = re.sub(pattern="^说粤语", repl="", string=msg)
    msg = await Translate(Sentence=msg, to_Language="yue")
    await speakCantonese.send(msg)


@Bot.on_calling_api
async def cantonese(bot: Bot, api: str, data: dict[str, any]):
    # 必须是发送消息的事件
    if api not in ["send_msg", "send_group_msg", "send_private_msg"]:
        return
    messages: list[MessageSegment] = data["message"]
    outMsg = ""
    for msg in messages:
        if msg.type == "text":
            text: str = msg.data["text"]
            texts = text.split("\n")
            outTexts = []
            for t in texts:
                if t != "":
                    out = await Translate(Sentence=t, to_Language="yue")
                    if out is not None:
                        outTexts.append(out)
            if outTexts:
                text = "\n".join(outTexts) if len(outTexts) > 1 else outTexts[0]
                outMsg += MessageSegment.text(text)
        else:
            outMsg += msg
    data["message"] = outMsg
