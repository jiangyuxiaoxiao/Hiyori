"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/09/19-14:56
@Desc: 妃爱圣经！
@Ver : 1.0.0
"""
import os
import json
import random
import re

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent

from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.Message.Record import RecordMessage
from Hiyori.Utils.File import DirExist

RecordsDict = dict()
# 初始化
DirExist("Config/Hiyo/script")
if os.path.isfile("Config/Hiyo/script/妃愛.txt"):
    with open(file="Config/Hiyo/script/妃愛.txt", mode="r", encoding="utf-8") as file:
        data = file.read()
    Records = json.loads(data)
else:
    Records = []
RecordsDict["Hiyori"] = Records
if os.path.isfile("Config/Hiyo/script/あすみ.txt"):
    with open(file="Config/Hiyo/script/あすみ.txt", mode="r", encoding="utf-8") as file:
        data = file.read()
    Records = json.loads(data)
else:
    Records = []
RecordsDict["Asumi"] = Records
if os.path.isfile("Config/Hiyo/script/華乃.txt"):
    with open(file="Config/Hiyo/script/華乃.txt", mode="r", encoding="utf-8") as file:
        data = file.read()
    Records = json.loads(data)
else:
    Records = []
RecordsDict["Kano"] = Records

hiyoBible = on_regex(r"^(妃爱|和泉妃爱|妃|锦|小天使|锦亚澄|华乃|常磐|常磐华乃)圣经$", priority=Priority.普通优先级, block=False)


@hiyoBible.handle()
async def _(event: MessageEvent):
    msg = event.message.extract_plain_text()
    match msg:
        case "妃爱圣经" | "和泉妃爱圣经" | "妃圣经":
            name = "Hiyori"
        case "锦圣经" | "小天使圣经" | "锦亚澄圣经":
            name = "Asumi"
        case _:
            name = "Kano"
    if not RecordsDict[name]:
        return
    else:
        count = 10
        while count > 0:
            voice = random.choice(RecordsDict[name])
            voiceFile = os.path.join(f"Data/Src/Sound/{name}", voice["vo"] + ".ogg")
            if os.path.isfile(voiceFile):
                text = " ".join(voice["texts"]).strip("「").strip("」")
                record = RecordMessage(voiceFile)
                await hiyoBible.send(text)
                await hiyoBible.send(record)
                return
            count -= 1
