"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/1-23:45
@Desc: 群文件备份插件，测试中
@Ver : 1.0.0
"""

import re
import argparse

from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot import on_regex
from nonebot.plugin import PluginMetadata

from Hiyori.Utils.Permissions import HIYORI_OWNER
from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.API.QQ.GroupFile import QQGroupFolder
from Hiyori.Plugins.Basic_plugins.MultiBot_Support import getBot

__plugin_meta__ = PluginMetadata(
    name="群文件备份",  # 用于在菜单显示 用于插件开关
    description="群文件备份，将群文件备份到指定目录下\n",
    usage="群文件备份 【可选参数】\n"
          "参数列表：\n"
          "-p=200 指定并发数\n"
          "-r=20 下载失败重试次数\n"
          "-w=5 下载失败重试等待间隔，单位为秒\n"
          "-c=2 连接失败等待间隔\n"
          "-t 当包含该参数时将下载临时文件\n"
          "-o 当包含该参数时，下载文件结构与群文件结构相同即：群号/群文件。默认为群号/人名/群文件",
    extra={"example": "",
           "Group": "Daily",
           "version": "1.0",
           "permission": "妃爱超级管理员",
           "Keep_On": True,
           "Type": "Normal_Plugin",
           }
)

concurrentDownload = on_regex(r"^群文件备份", permission=HIYORI_OWNER, priority=Priority.普通优先级)


@concurrentDownload.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = event.message.extract_plain_text()
    msg = re.sub(pattern=r"^群文件备份", repl="", string=msg).strip(" ").split(" ")
    if len(msg) == 1 and msg[0] == "":
        msg = []
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-p", type=int, default=200)
    argparser.add_argument("-r", "--retry", type=int, default=None)
    argparser.add_argument("-w", "--wait", type=float, default=None)
    argparser.add_argument("-c", "--ctimeout", type=float, default=None)
    argparser.add_argument("-d", "--dtimeout", type=float, default=None)
    argparser.add_argument("-t", "--tempfile", action="store_true")
    argparser.add_argument("-o", "--origin", action="store_true")
    args = argparser.parse_args(msg)
    concurrentNum = args.p
    attemptCount = args.retry
    waitAfterFail = args.wait
    connectTimeout = args.ctimeout
    downloadTimeout = args.dtimeout
    ignoreTempFile = not args.tempfile
    originMode = "Origin" if args.origin else "ByName"

    concurrentNumStr = f"设置并发数{concurrentNum}，"
    attemptCountStr = f"设置重试次数{attemptCount}，" if attemptCount else ""
    waitAfterFailStr = f"设置重试等待时间{waitAfterFail}s，" if waitAfterFail else ""
    connectTimeoutStr = f"设置连接超时{connectTimeout}s，" if connectTimeout else ""
    downloadTimeoutStr = f"设置下载超时{downloadTimeout}s，" if downloadTimeout else ""
    originModeStr = f"按群目录格式存储，" if args.origin else "按用户名/群目录格式存储，"
    ignoreTempFileStr = f"不下载临时文件" if ignoreTempFile else "下载临时文件"

    await concurrentDownload.send(f"群文件备份开始  {concurrentNumStr}{attemptCountStr}{waitAfterFailStr}{connectTimeoutStr}{downloadTimeoutStr}"
                                  f"{originModeStr}{ignoreTempFileStr}")

    GroupID = event.group_id
    groupFolder = QQGroupFolder(group_id=GroupID, folder_id=None, folder_name=f"{GroupID}",
                                create_time=0, creator=0, creator_name="", total_file_count=0,
                                local_path="")
    await groupFolder.updateInfoFromQQ(getBot(GroupID))
    msg = await groupFolder.SyncFromGroup(dirPath=f"Data/GroupFile_Backup", bot=bot, concurrentNum=concurrentNum,
                                          ignoreTempFile=ignoreTempFile, attemptCount=attemptCount, waitAfterFail=waitAfterFail,
                                          connectTimeout=connectTimeout, downloadTimeout=downloadTimeout, mode=originMode)
    try:
        await concurrentDownload.send(msg)
    except Exception:
        await concurrentDownload.send("下载已完成，报错信息较多，请在log中自行查看")
