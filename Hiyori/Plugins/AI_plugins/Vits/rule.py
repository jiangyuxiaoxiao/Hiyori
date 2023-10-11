"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/09/28-15:31
@Desc: 语音触发检查
@Ver : 1.0.0
"""
import re

from nonebot.adapters.onebot.v11 import MessageEvent

import Hiyori.Utils.API.BertVits as BertVits
import Hiyori.Utils.API.Vits as Vits

bertMap = BertVits.getBV_Map()
vitsMap = Vits.getVits_Map()


async def vitsCheck(event: MessageEvent) -> bool:
    global bertMap, vitsMap
    msg = event.message.extract_plain_text()
    msg = re.match(pattern=r"#?.+说", string=msg)
    if msg is None:
        return False
    name = msg.group().split("说")[0].lstrip("#").rstrip()
    if name not in bertMap.keys() and name not in vitsMap.keys():
        return False
    return True
