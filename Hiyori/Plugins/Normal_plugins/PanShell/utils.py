"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/29-20:44
@Desc: 工具函数包
@Ver : 1.0.0
"""
import os
from io import BytesIO
import warnings

from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment

from Hiyori.Utils.Message.Image.pil_utils import text2image
from Hiyori.Utils.API.Baidu import baidu
import Hiyori.Utils.API.Baidu.Pan as baiduPan


def printFileInfo(infos: list[dict], msgBefore: str = "", msgAfter: str = "") -> MessageSegment:
    """打印文件信息，并转换为图片"""
    msg = msgBefore
    for info in infos:
        # 容量信息
        size = info["size"]
        size = printSizeInfo(size)
        if info["isdir"] == 1:
            msg += info["server_filename"] + "/ " + "\n"
        else:
            msg += info["server_filename"] + "  " + size + "\n"
    if msg == "":
        return MessageSegment.text("当前文件夹为空")
    else:
        msg = msg + msgAfter
        image = text2image(text=msg)
        msg = BytesIO()
        image.save(msg, format="png")
        return MessageSegment.image(msg)


def printSizeInfo(size: int) -> str:
    """
    打印文件大小信息，根据具体的值选择合适的单位。

    :param size 文件大小，单位为字节。
    """
    if size < 1024:
        size = str(size) + "B"
    elif size < 1024 ** 2:
        size = str(round(size / 1024, 3)) + "KB"
    elif size < 1024 ** 3:
        size = str(round(size / (1024 ** 2), 3)) + "MB"
    elif size < 1024 ** 4:
        size = str(round(size / (1024 ** 3), 3)) + "GB"
    else:
        size = str(round(size / (1024 ** 4), 3)) + "TB"
    return str(size)



