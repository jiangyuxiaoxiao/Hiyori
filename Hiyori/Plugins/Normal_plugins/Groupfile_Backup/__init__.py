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

from Hiyori.Utils.Permissions import HIYORI_OWNER
from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.API.QQ.GroupFile import QQGroupFolder
from Hiyori.Utils.File import DirExist

from Hiyori.Plugins.Basic_plugins.MultiBot_Support import getBot

backup = on_regex(r"^#备份测试#$", permission=HIYORI_OWNER, priority=Priority.普通优先级)
concurrentDownload = on_regex(r"^并发备份测试", permission=HIYORI_OWNER, priority=Priority.普通优先级)


@backup.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    GroupID = event.group_id
    groupFolder = QQGroupFolder(group_id=GroupID, folder_id=None, folder_name="/",
                                create_time=0, creator=0, creator_name="", total_file_count=0,
                                local_path="")
    await groupFolder.getGroupFolderInfo(bot)
    DirExist("Data/Debug/Debug_GroupFile")
    with open("Data/Debug/Debug_GroupFile/config.json", mode="w", encoding="utf-8") as file:
        file.write(groupFolder.dumps())
    await backup.send("已写入信息")


@concurrentDownload.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = event.message.extract_plain_text()
    msg = re.sub(pattern=r"^并发备份测试", repl="", string=msg).strip(" ").split(" ")
    if len(msg) == 1 and msg[0] == "":
        msg = []
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-p", type=int, default=200)
    argparser.add_argument("-r", "--retry", type=int, default=None)
    argparser.add_argument("-w", "--wait", type=float, default=None)
    argparser.add_argument("-c", "--ctimeout", type=float, default=None)
    argparser.add_argument("-d", "--dtimeout", type=float, default=None)
    argparser.add_argument("-t", "--tempfile", action="store_true")
    args = argparser.parse_args(msg)
    concurrentNum = args.p
    attemptCount = args.retry
    waitAfterFail = args.wait
    connectTimeout = args.ctimeout
    downloadTimeout = args.dtimeout
    ignoreTempFile = not args.tempfile

    concurrentNumStr = f"设置并发数{concurrentNum}，"
    attemptCountStr = f"设置重试次数{attemptCount}，" if attemptCount else ""
    waitAfterFailStr = f"设置重试等待时间{waitAfterFail}，" if waitAfterFail else ""
    connectTimeoutStr = f"设置连接超时{connectTimeout}，" if connectTimeout else ""
    downloadTimeoutStr = f"设置下载超时{downloadTimeout}，" if downloadTimeout else ""
    ignoreTempFileStr = f"不下载临时文件" if ignoreTempFile else "下载临时文件"
    await concurrentDownload.send(f"开始测试  {concurrentNumStr}{attemptCountStr}{waitAfterFailStr}{connectTimeoutStr}{downloadTimeoutStr}{ignoreTempFileStr}")

    GroupID = event.group_id
    groupFolder = QQGroupFolder(group_id=GroupID, folder_id=None, folder_name=f"{GroupID}",
                                create_time=0, creator=0, creator_name="", total_file_count=0,
                                local_path="")
    await groupFolder.getGroupFolderInfo(getBot(GroupID))
    msg = await groupFolder.concurrentDownload(dirPath=f"Data/Debug/Debug_GroupFile", bot=bot, concurrentNum=concurrentNum,
                                               ignoreTempFile=ignoreTempFile, attemptCount=attemptCount, waitAfterFail=waitAfterFail,
                                               connectTimeout=connectTimeout, downloadTimeout=downloadTimeout)
    try:
        await concurrentDownload.send(msg)
    except Exception:
        await concurrentDownload.send("下载已完成，报错信息较多，请在log中自行查看")
