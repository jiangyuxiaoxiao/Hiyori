"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/9-21:09
@Desc: 
@Ver : 1.0.0
"""
import os
import pathlib
from nonebot.adapters.onebot.v11 import MessageSegment


def RecordMessage(Path: str = None) -> MessageSegment:
    """
    将录音文件路径转换为录音Message

    :param Path: 录音路径，支持绝对路径与相对路径
    :return: MessageSegment
    """
    Path = os.path.abspath(Path)
    Path = pathlib.Path(Path).as_uri()
    return MessageSegment.record(Path)
