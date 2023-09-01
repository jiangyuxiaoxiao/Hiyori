"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/1-23:45
@Desc: 群文件备份插件，测试中
@Ver : 1.0.0
"""

import re

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
    con = re.sub(pattern=r"^并发备份测试", repl="", string=msg)
    con = int(con)
    await concurrentDownload.send(f"开始测试{con}")

    GroupID = event.group_id
    groupFolder = QQGroupFolder(group_id=GroupID, folder_id=None, folder_name=f"{GroupID}",
                                create_time=0, creator=0, creator_name="", total_file_count=0,
                                local_path="")

    await groupFolder.getGroupFolderInfo(getBot(GroupID))
    msg = await groupFolder.concurrentDownload(dirPath=f"Data/Debug/Debug_GroupFile", bot=bot, concurrentNum=con, ignoreTempFile=True)
    try:
        await concurrentDownload.send(msg)
    except Exception:
        await concurrentDownload.send("下载已完成，报错信息较多，请在log中自行查看")
