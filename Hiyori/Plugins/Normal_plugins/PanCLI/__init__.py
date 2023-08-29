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

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent, Bot, MessageSegment
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata

from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.File import DirExist
from Hiyori.Utils.Message.Forward_Message import Nodes
import Hiyori.Utils.API.Baidu.Pan as baiduPan
from Hiyori.Utils.API.Baidu import baidu

from .utils import printFileInfo, 文件模糊匹配, 文件夹模糊匹配

__plugin_meta__ = PluginMetadata(
    name="妃爱网盘",
    description="通过妃爱操作百度网盘。",
    usage="pan ls 【查询当前路径目录】\n"
          "pan cd 路径 【切换到指定路径，可模糊匹配】\n"
          "pan dl 文件路径 【下载指定文件到对应群聊/私聊】\n"
          "pan login 【百度网盘登录】"
          "pan logout 【百度网盘登出】",
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
        msg = printFileInfo(infos)
    if len(infos) > 10 and isinstance(event, GroupMessageEvent):
        msg = Nodes(qID=event.self_id, name="妃爱网盘", content=msg)
        await bot.call_api("send_group_forward_msg", **{"group_id": event.group_id, "messages": msg.msg()})
    else:
        await myPan.send(msg)


@cd.handle()
async def _(matcher: Matcher, bot: Bot, event: MessageEvent):
    global Dir
    QQ = event.user_id
    await initFunc(QQ, matcher)
    goto = re.sub(r"^pan\s+cd\s+", string=str(event.message), repl="")
    if goto.startswith("/"):
        newDir = goto
        infos = await baiduPan.listDir(path=newDir, QQ=QQ, matcher=matcher)
        # 精确匹配不存在则进行模糊匹配
        if infos is None:
            # 进行模糊查找
            newDir = await 文件夹模糊匹配(path=newDir, QQ=QQ, matcher=matcher)
            if newDir is None:
                await cd.send("目录不存在")
                return
            else:
                infos = await baiduPan.listDir(path=newDir, QQ=QQ, matcher=matcher)
        # 判断是空文件夹还是文件
        if len(infos) == 0:
            breakFlag = True
            if newDir.endswith("/"):
                newDir = newDir.rstrip("/")  # 去掉尾部的/来获取正确上级文件夹
            新路径的上级文件夹路径 = os.path.dirname(newDir)
            新路径文件名 = os.path.basename(newDir)
            infos2 = await baiduPan.listDir(path=新路径的上级文件夹路径, QQ=QQ, matcher=matcher)
            for info in infos2:
                if info["server_filename"] == 新路径文件名 and info["isdir"] == 1:
                    breakFlag = False
                    break
            if breakFlag:
                await cd.send("路径不是目录")
                return
        if not newDir.endswith("/"):
            newDir += "/"
        Dir[QQ] = newDir
        msg = printFileInfo(infos)
        await cd.send(f"[pan {QQ}]$    {Dir[QQ]}>")
        # 在群聊中，过长会进行转发
        if len(infos) > 10 and isinstance(event, GroupMessageEvent):
            msg = Nodes(qID=event.self_id, name="妃爱网盘", content=msg)
            await bot.call_api("send_group_forward_msg", **{"group_id": event.group_id, "messages": msg.msg()})
        else:
            await myPan.send(msg)
        return
    else:
        # newDir = os.path.join(Dir[QQ], goto)
        newDir = os.path.normpath(Dir[QQ] + goto)
        newDir = newDir.replace("\\", "/")
        infos = await baiduPan.listDir(path=newDir, QQ=QQ, matcher=matcher)
        if infos is None:
            # 进行模糊查找
            newDir = await 文件夹模糊匹配(path=newDir, QQ=QQ, matcher=matcher)
            if newDir is None:
                await cd.send("目录不存在")
                return
            else:
                infos = await baiduPan.listDir(path=newDir, QQ=QQ, matcher=matcher)
        # 判断是空文件夹还是文件
        if len(infos) == 0:
            breakFlag = True
            if newDir.endswith("/"):
                newDir = newDir.rstrip("/")  # 去掉尾部的/来获取正确上级文件夹
            新路径的上级文件夹路径 = os.path.dirname(newDir)
            新路径文件名 = os.path.basename(newDir)
            infos2 = await baiduPan.listDir(path=新路径的上级文件夹路径, QQ=QQ, matcher=matcher)
            for info in infos2:
                if info["server_filename"] == 新路径文件名 and info["isdir"] == 1:
                    breakFlag = False
                    break
            if breakFlag:
                await cd.send("路径不是目录")
                return
        if not newDir.endswith("/"):
            newDir += "/"
        Dir[QQ] = newDir
        msg = printFileInfo(infos)
        await cd.send(f"[pan {QQ}]$    {Dir[QQ]}>")
        if len(infos) > 10 and isinstance(event, GroupMessageEvent):
            msg = Nodes(qID=event.self_id, name="妃爱网盘", content=msg)
            await bot.call_api("send_group_forward_msg", **{"group_id": event.group_id, "messages": msg.msg()})
        else:
            await myPan.send(msg)
        return


@download.handle()
async def _(matcher: Matcher, bot: Bot, event: MessageEvent):
    """在群聊中将上传至群文件，在私聊中将上传私聊文件"""
    global Dir
    QQ = event.user_id
    await initFunc(QQ, matcher)
    file = re.sub(r"^pan\s+dl\s+", string=str(event.message), repl="")
    if file.startswith("/"):
        file = file
    else:
        file = os.path.normpath(Dir[QQ] + file)
        file = file.replace("\\", "/")
    fileName = os.path.basename(file)
    DirExist("Data/BaiduPan/Cache")
    localPath = os.path.abspath(os.path.join("Data/BaiduPan/Cache", str(random.randint(1, 10 ** 10)) + ".hiyoriCache"))
    try:
        await baiduPan.downloadFile(localPath=localPath, panPath=file, QQ=QQ, matcher=matcher)
    except Exception:
        await download.send("文件下载失败")
        if os.path.exists(localPath):
            os.remove(path=localPath)
        return
    try:
        if isinstance(event, PrivateMessageEvent):
            QQ = event.user_id
            await bot.call_api(api="upload_private_file", **{"user_id": QQ, "file": localPath, "name": fileName})
        elif isinstance(event, GroupMessageEvent):
            Group = event.group_id
            await bot.call_api(api="upload_group_file", **{"group_id": Group, "file": localPath, "name": fileName})
    except Exception:
        await download.send("文件上传失败")
        if os.path.exists(localPath):
            os.remove(path=localPath)
        return
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
    QQ = event.user_id
    await initFunc(QQ, matcher)
    file = re.sub(r"^pan\s+rm", string=str(event.message), repl="")
