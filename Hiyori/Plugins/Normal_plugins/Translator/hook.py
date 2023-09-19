"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/8-8:41
@Desc: 
@Ver : 1.0.0
"""

from nonebot.adapters.onebot.v11 import Bot, MessageSegment
from Hiyori.Utils.API.Baidu.OpenTranslate import Translate

from .config import translatorConfig


@Bot.on_calling_api
async def cantonese(bot: Bot, api: str, data: dict[str, any]):
    # 必须是发送消息的事件
    if api not in ["send_msg", "send_group_msg", "send_private_msg"]:
        return
    messages: list[MessageSegment] = data["message"]
    if "user_id" in data:
        QQ = data["user_id"]
    else:
        return
    if str(QQ) in translatorConfig.config:
        if translatorConfig.config[str(QQ)] == "":
            return
        outMsg = None
        for msg in messages:
            if hasattr(msg, "type"):
                if msg.type == "text":
                    text: str = msg.data["text"]
                    texts = text.split("\n")
                    outTexts = []
                    for t in texts:
                        if t != "":
                            out = await Translate(Sentence=t, to_Language=translatorConfig.config[str(QQ)])
                            if out is not None:
                                outTexts.append(out)
                        else:
                            if outTexts:
                                outTexts[-1] += "\n"
                            else:
                                outTexts.append("\n")
                    if outTexts:
                        text = "\n".join(outTexts) if len(outTexts) > 1 else outTexts[0]
                        outMsg += MessageSegment.text(text)
                else:
                    if not outMsg:
                        outMsg = msg
                    else:
                        outMsg += msg
            else:
                return
        data["message"] = outMsg
