"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/1-23:45
@Desc: 群文件备份插件，测试中
@Ver : 1.0.0
"""
import json
import re
import argparse
import os

from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment
from nonebot.matcher import Matcher
from nonebot.log import logger
from nonebot import on_regex
from nonebot.plugin import PluginMetadata

from Hiyori.Utils.Permissions import HIYORI_OWNER
from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.API.QQ.GroupFile import QQGroupFolder
from Hiyori.Plugins.Basic_plugins.MultiBot_Support import getBot
import Hiyori.Utils.API.Baidu.Pan as baiduPan

__plugin_meta__ = PluginMetadata(
    name="群文件同步备份",  # 用于在菜单显示 用于插件开关
    description="群文件备份，将群文件同步备份到指定目录下\n",
    usage="群文件同步 【可选参数】\n"
          "参数列表：\n"
          "-p=200 指定并发数\n"
          "-r=20 下载失败重试次数\n"
          "-w=5 下载失败重试等待间隔，单位为秒\n"
          "-c=2 连接失败等待间隔\n"
          "-t 当包含该参数时将下载临时文件\n"
          "-o 当包含该参数时，下载文件结构与群文件结构相同即：群号/群文件。默认为群号/人名/群文件\n"
          "-q 当包含该参数时，对话关闭，仅通过log来输出结果。",
    extra={"example": "",
           "Group": "Daily",
           "version": "1.0",
           "permission": "妃爱超级管理员",
           "Keep_On": True,
           "Type": "Normal_Plugin",
           }
)

concurrentSync = on_regex(r"^#?群文件同步", permission=HIYORI_OWNER, priority=Priority.普通优先级)
uploadSync = on_regex(r"^#?本地文件同步", permission=HIYORI_OWNER, priority=Priority.普通优先级)
panBackUp = on_regex(r"^#?群文件百度网盘备份", priority=Priority.普通优先级)


@concurrentSync.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = event.message.extract_plain_text()
    msg = re.sub(pattern=r"^#?群文件同步", repl="", string=msg).strip(" ").split(" ")
    if len(msg) == 1 and msg[0] == "":
        msg = []
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-p", type=int, default=200)
    argparser.add_argument("-r", "--retry", type=int, default=None)
    argparser.add_argument("-w", "--wait", type=float, default=None)
    argparser.add_argument("-c", "--ctimeout", type=float, default=None)
    argparser.add_argument("-d", "--dtimeout", type=float, default=None)
    argparser.add_argument("-t", "--tempfile", action="store_true")
    argparser.add_argument("-n", "--name", action="store_true")
    argparser.add_argument("-q", "--quiet", action="store_true")
    args = argparser.parse_args(msg)
    concurrentNum = args.p
    attemptCount = args.retry
    waitAfterFail = args.wait
    connectTimeout = args.ctimeout
    downloadTimeout = args.dtimeout
    ignoreTempFile = not args.tempfile
    quiet = args.quiet
    nameMode = "ByName" if args.name else "Origin"

    concurrentNumStr = f"设置并发数{concurrentNum}，"
    attemptCountStr = f"设置重试次数{attemptCount}，" if attemptCount else ""
    waitAfterFailStr = f"设置重试等待时间{waitAfterFail}s，" if waitAfterFail else ""
    connectTimeoutStr = f"设置连接超时{connectTimeout}s，" if connectTimeout else ""
    downloadTimeoutStr = f"设置下载超时{downloadTimeout}s，" if downloadTimeout else ""
    originModeStr = f"按群目录格式存储，" if not args.name else "按用户名/群目录格式存储，"
    ignoreTempFileStr = f"不下载临时文件" if ignoreTempFile else "下载临时文件"
    if not quiet:
        await concurrentSync.send(f"群文件备份开始  {concurrentNumStr}{attemptCountStr}{waitAfterFailStr}{connectTimeoutStr}{downloadTimeoutStr}"
                                  f"{originModeStr}{ignoreTempFileStr}")

    GroupID = event.group_id
    groupFolder = QQGroupFolder(group_id=GroupID, folder_id=None, folder_name=f"{GroupID}",
                                create_time=0, creator=0, creator_name="", total_file_count=0,
                                local_path="")
    await groupFolder.updateInfoFromQQ(getBot(GroupID))
    msg = await groupFolder.syncFromGroup(dirPath=f"Data/GroupFile_Backup", bot=bot, concurrentNum=concurrentNum,
                                          ignoreTempFile=ignoreTempFile, attemptCount=attemptCount, waitAfterFail=waitAfterFail,
                                          connectTimeout=connectTimeout, downloadTimeout=downloadTimeout, mode=nameMode)
    try:
        if not quiet:
            await concurrentSync.send(msg)
    except Exception:
        if not quiet:
            await concurrentSync.send("下载已完成，报错信息较多，请在log中自行查看")


@uploadSync.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = event.message.extract_plain_text()
    msg = re.sub(pattern=r"^#?本地文件同步", repl="", string=msg).strip(" ").split(" ")
    if len(msg) == 1 and msg[0] == "":
        msg = []
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-q", "--quiet", action="store_true")
    argparser.add_argument("-w", "--wait", type=float, default=0)
    args = argparser.parse_args(msg)
    quiet = args.quiet
    wait = args.wait
    if not quiet:
        await uploadSync.send(f"即将将本地文件同步上传至群文件，每次上传间隔{wait}秒")
    GroupID = event.group_id
    configPath = f"Data/GroupFile_Backup/不区分用户名/{GroupID}/.config/config.json"
    if not os.path.isfile(configPath):
        await uploadSync.send("配置文件不存在，或者本地文件不存在。注意：仅可同步上传按群文件目录格式的群文件夹")
    try:
        with open(configPath, mode="r", encoding="utf-8") as file:
            content = file.read()
            groupFolder = QQGroupFolder.from_dict(json.loads(content))
    except Exception:
        await uploadSync.send("配置解析失败")
    msg = await groupFolder.syncToGroup(bot=bot, waitTime=wait)
    if not quiet:
        await uploadSync.send(msg)


@panBackUp.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    GroupID = event.group_id
    groupFolder = QQGroupFolder(group_id=GroupID, folder_id=None, folder_name=f"{GroupID}",
                                create_time=0, creator=0, creator_name="", total_file_count=0,
                                local_path="")
    await panBackUp.send("正在将文件同步到本地...")
    await groupFolder.updateInfoFromQQ(getBot(GroupID))
    msg = await groupFolder.syncFromGroup(dirPath=f"Data/GroupFile_Backup", bot=bot, concurrentNum=200, ignoreTempFile=True, mode="Origin")
    await panBackUp.send(msg)
    backDir = f"Data/GroupFile_Backup/{GroupID}"
    files = groupFolder.getAllFiles()
    panDir = f"apps/Hiyori/GroupFile_Backup/{GroupID}"
    await panBackUp.send("正在将文件备份至百度网盘...")
    userInfo = await baiduPan.userInfo(QQ=event.user_id, matcher=matcher)
    vip_type = userInfo["vip_type"]
    match vip_type:
        case 2:
            chunkSize = 32
        case 1:
            chunkSize = 16
        case _:
            chunkSize = 4

    for file in files:
        relPath = os.path.relpath(file.local_path, backDir)
        panPath = "/" + os.path.normpath(os.path.dirname(os.path.join(panDir, relPath))).replace("\\", "/").strip("/")

        result = await baiduPan.uploadFile(QQ=event.user_id, localPath=file.local_path, panPath=panPath, chunkSize=chunkSize, matcher=matcher)
        logger.success(json.dumps(result))
        # await panBackUp.send(f"文件{os.path.basename(file.local_path)}上传结果:{json.dumps(result)}")
    msg = MessageSegment.at(event.user_id) + "已将文件上传至百度网盘"
    await panBackUp.send(msg)
