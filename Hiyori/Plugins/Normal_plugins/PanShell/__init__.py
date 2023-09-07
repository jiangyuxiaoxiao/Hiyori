"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/28-15:32
@Desc: 私人百度网盘CLI demo
@Ver : 1.0.0
"""
import re
import os
import random
import time

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent, Bot, MessageSegment
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata

from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.File import DirExist
import Hiyori.Utils.API.Baidu.Pan as baiduPan
from Hiyori.Utils.API.Baidu import baidu
from Hiyori.Utils.Time import printTimeInfo

from .utils import printFileInfo, printSizeInfo

__plugin_meta__ = PluginMetadata(
    name="妃爱网盘",
    description="通过妃爱操作百度网盘。",
    usage="pan ls 【查询当前路径目录】\n"
          "pan cd 路径 【切换到指定路径，可模糊匹配】\n"
          "pan dl 文件路径 【下载指定文件到对应群聊/私聊，可模糊匹配】\n"
          "pan login 【百度网盘登录】\n"
          "pan logout 【百度网盘登出】\n"
          "pan df 【查询网盘容量】",
    extra={
        "CD_Weight": 2,
        "example": "",
        "Keep_On": False,
        "Type": "Normal_Plugin",
    },
)

Dir: dict = {}

myPan = on_regex(r"^pan\s+ls$", priority=Priority.普通优先级, block=True)
cd = on_regex(r"^pan\s+cd\s+", priority=Priority.普通优先级, block=True)
download = on_regex(r"^pan\s+dl\s+", priority=Priority.普通优先级, block=True)
login = on_regex(r"^pan\s+login", priority=Priority.普通优先级, block=True)
logout = on_regex(r"^pan\s+logout", priority=Priority.普通优先级, block=True)
delete = on_regex(r"^pan\s+rm", priority=Priority.普通优先级, block=True)
disk = on_regex(r"^pan\s+df", priority=Priority.普通优先级, block=True)


async def initFunc(QQ: int, matcher: Matcher):
    """通用初始化函数"""
    if QQ not in Dir.keys():
        Dir[QQ] = "/"
    if str(QQ) not in baidu.Api.Pan.userInfo.keys():
        msg = MessageSegment.at(QQ) + "请先登录后再操作，指令为： pan login"
        await matcher.finish(msg)


@myPan.handle()
async def _(matcher: Matcher, bot: Bot, event: MessageEvent):
    global Dir
    QQ = event.user_id
    await initFunc(QQ, matcher)
    infos = await baiduPan.listDir(path=Dir[QQ], QQ=QQ, matcher=matcher)
    msg = ""
    if infos is None:
        await myPan.send("目录获取失败")
    else:
        await myPan.send(printFileInfo(infos=infos, msgBefore=f"[pan {QQ}]$    {Dir[QQ]}>\n"))


@cd.handle()
async def _(matcher: Matcher, bot: Bot, event: MessageEvent):
    global Dir
    QQ = event.user_id
    await initFunc(QQ, matcher)
    goto = re.sub(r"^pan\s+cd\s+", string=event.message.extract_plain_text(), repl="")
    if goto.startswith("/"):
        newDir = goto
    else:
        # newDir = os.path.join(Dir[QQ], goto)
        newDir = os.path.normpath(Dir[QQ] + goto)
        newDir = newDir.replace("\\", "/")
    # 模糊查询新文件夹信息
    newDirInfo = await baiduPan.fileInfo(QQ=QQ, matcher=matcher, path=newDir, ignoreFile=True, fuzzy_matching=True)
    if newDirInfo is None and newDir != "/":  # 根目录特殊处理
        msg = MessageSegment.at(event.user_id) + "目录不存在"
        await cd.send(msg)
        return
    else:
        if newDir != "/":
            if newDir.endswith("/"):
                newDir = newDir.rstrip("/")
            newDirName: str = newDirInfo["filename"]
            newDir = os.path.join(os.path.dirname(newDir), newDirName)
            # 文件名标准化，必须为'/'，不能包含'\'，且路径必须以'/'结尾
            newDir = newDir.replace("\\", "/")
            if not newDir.endswith("/"):
                newDir += "/"
        infos = await baiduPan.listDir(QQ=QQ, path=newDir, matcher=matcher)
        if infos is None:
            msg = MessageSegment.at(event.user_id) + "目录不存在"
            await cd.send(msg)
            return
        else:
            # 打印目录，并将当前目录切换至该目录
            Dir[QQ] = newDir
            await cd.send(printFileInfo(infos=infos, msgBefore=f"[pan {QQ}]$    {Dir[QQ]}>\n"))
            return


@download.handle()
async def _(matcher: Matcher, bot: Bot, event: MessageEvent):
    """在群聊中将上传至群文件，在私聊中将上传私聊文件"""
    global Dir
    QQ = event.user_id
    await initFunc(QQ, matcher)
    file = re.sub(r"^pan\s+dl\s+", string=event.message.extract_plain_text(), repl="")
    if file.startswith("/"):
        file = file
    else:
        file = os.path.normpath(Dir[QQ] + file)
        file = file.replace("\\", "/")
    DirExist("Data/BaiduPan/Cache")
    localPath = os.path.abspath(os.path.join("Data/BaiduPan/Cache", str(random.randint(1, 10 ** 10)) + ".hiyoriCache"))
    startTime = time.time_ns()
    try:
        size, fileName = await baiduPan.downloadFile(localPath=localPath, panPath=file, QQ=QQ, matcher=matcher, fuzzy_matching=True)
    except Exception:
        msg = MessageSegment.at(event.user_id) + "文件下载失败，网络故障或文件不存在。"
        await download.send(msg)
        if os.path.exists(localPath):
            os.remove(path=localPath)
        return
    endTime = time.time_ns()
    try:
        msg = MessageSegment.at(
            event.user_id) + f"网盘文件：{fileName}下载完毕，文件大小{printSizeInfo(size)}，用时{printTimeInfo(endTime - startTime, 3)}。正在上传"
        await download.send(msg)
        startTime = time.time_ns()
        if isinstance(event, PrivateMessageEvent):
            QQ = event.user_id
            await bot.call_api(api="upload_private_file", **{"user_id": QQ, "file": localPath, "name": fileName})
        elif isinstance(event, GroupMessageEvent):
            Group = event.group_id
            await bot.call_api(api="upload_group_file", **{"group_id": Group, "file": localPath, "name": fileName})
    except Exception:
        msg = MessageSegment.at(event.user_id) + "文件上传失败"
        await download.send(msg)
        if os.path.exists(localPath):
            os.remove(path=localPath)
        return
    endTime = time.time_ns()
    msg = MessageSegment.at(event.user_id) + f"文件上传成功，用时{printTimeInfo(endTime - startTime, 3)}"
    await download.send(msg)
    if os.path.exists(localPath):
        os.remove(path=localPath)


@login.handle()
async def _(matcher: Matcher, event: MessageEvent):
    QQ = event.user_id
    status = await baidu.Api.Pan.openapi_Get_Refresh_Token(QQ=QQ, matcher=matcher)
    if status == 1:
        baidu.dumps()


@logout.handle()
async def _(matcher: Matcher, event: MessageEvent):
    QQ = event.user_id
    msg = MessageSegment.at(QQ)
    if str(QQ) in baidu.Api.Pan.userInfo.keys():
        del baidu.Api.Pan.userInfo[str(QQ)]
        baidu.dumps()
        await logout.send(msg + "登出成功")
    else:
        await logout.send(msg + "你还没有登录哦")


@delete.handle()
async def _(matcher: Matcher, event: MessageEvent):
    global Dir
    QQ = event.user_id
    await initFunc(QQ, matcher)
    file = re.sub(r"^pan\s+rm", string=str(event.message), repl="")


@disk.handle()
async def _(matcher: Matcher, event: MessageEvent):
    QQ = event.user_id
    await initFunc(QQ, matcher)
    info = await baiduPan.diskInfo(QQ, matcher)
    if info is None:
        msg = MessageSegment.at(event.user_id) + "网盘容量查询失败"
        await disk.send(msg)
    else:
        used = printSizeInfo(info["used"])
        total = printSizeInfo(info["total"])
        msg = MessageSegment.at(event.user_id) + f"当前网盘使用情况：{used}/{total}"
        await disk.send(msg)
