"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/29-20:44
@Desc: 工具函数包
@Ver : 1.0.0
"""
import os
from io import BytesIO

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


async def 文件模糊匹配(QQ: int, path: str, matcher: Matcher) -> str | None:
    """根据百度网盘文件路径进行模糊匹配，成功匹配返回对应路径，失败返回None"""
    # 若用户不存在
    if str(QQ) not in baidu.Api.Pan.userInfo.keys():
        return None
    if path.endswith("/"):
        path = path.rstrip("/")
    # 确定目录是否存在
    dirName = os.path.dirname(path)
    fileName = os.path.basename(path)
    infos = await baiduPan.listDir(path=dirName, QQ=QQ, matcher=matcher)
    if infos is None:
        return None
    else:
        # 逐个匹配
        for info in infos:
            # 匹配开头
            if info["server_filename"].startswith(fileName):
                return info["path"]
    return None


async def 文件夹模糊匹配(QQ: int, path: str, matcher: Matcher) -> str | None:
    """根据百度网盘文件路径进行模糊匹配，仅匹配文件夹路径。成功匹配返回对应文件夹路径，文件夹路径必以"/"结尾，失败返回None"""
    # 若用户不存在
    if str(QQ) not in baidu.Api.Pan.userInfo.keys():
        return None
    if path.endswith("/"):
        path = path.rstrip("/")
    # 确定目录是否存在
    dirName = os.path.dirname(path)
    fileName = os.path.basename(path)
    infos = await baiduPan.listDir(path=dirName, QQ=QQ, matcher=matcher)
    if infos is None:
        return None
    else:
        # 逐个匹配
        for info in infos:
            # 匹配开头，且文件类型为文件夹
            if info["server_filename"].startswith(fileName) and info["isdir"] == 1:
                path: str = info["path"]
                if not path.endswith("/"):
                    path += "/"
                    return path
    return None
