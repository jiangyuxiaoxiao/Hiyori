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
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent, Bot

from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.File import DirExist
from Hiyori.Utils.Permissions import HIYORI_OWNER
from Hiyori.Utils.Message.Forward_Message import Nodes
import Hiyori.Utils.API.Baidu.Pan as baiduPan

Dir = "/"

myPan = on_regex(r"^pan\s+ls$", permission=HIYORI_OWNER, priority=Priority.系统优先级, block=True)
cd = on_regex(r"^pan\s+cd\s+", permission=HIYORI_OWNER, priority=Priority.系统优先级, block=True)
download = on_regex(r"^pan\s+dl\s+", permission=HIYORI_OWNER, priority=Priority.系统优先级, block=True)


@myPan.handle()
async def _(bot: Bot, event: MessageEvent):
    global Dir
    infos = await baiduPan.listDir(path=Dir)
    msg = ""
    if infos is None:
        await myPan.send("目录获取失败")
    else:
        for info in infos:
            if info["isdir"] == 1:
                msg += info["server_filename"] + "/\n"
            else:
                msg += info["server_filename"] + "\n"
    if len(infos) > 10 and isinstance(event, GroupMessageEvent):
        msg = Nodes(qID=event.self_id, name="妃爱网盘", content=msg)
        await bot.call_api("send_group_forward_msg", **{"group_id": event.group_id, "messages": msg.msg()})
    else:
        await myPan.send(msg)


@cd.handle()
async def _(bot: Bot, event: MessageEvent):
    global Dir
    goto = re.sub(r"^pan\s+cd\s+", string=str(event.message), repl="")
    if goto.startswith("/"):
        newDir = goto
        infos = await baiduPan.listDir(path=newDir)
        if infos is None:
            await cd.send("目录不存在")
        else:
            Dir = newDir
            msg = ""

            for info in infos:
                if info["isdir"] == 1:
                    msg += info["server_filename"] + "/\n"
                else:
                    msg += info["server_filename"] + "\n"
            await cd.send(f"[pan]$    {Dir}>")
            # 在群聊中，过长会进行转发
            if len(infos) > 10 and isinstance(event, GroupMessageEvent):
                msg = Nodes(qID=event.self_id, name="妃爱网盘", content=msg)
                await bot.call_api("send_group_forward_msg", **{"group_id": event.group_id, "messages": msg.msg()})
            else:
                await myPan.send(msg)
        return
    newDir = os.path.normpath(Dir + goto)
    newDir = newDir.replace("\\", "/")
    if not newDir.endswith("/"):
        newDir += "/"
    infos = await baiduPan.listDir(path=newDir)
    if infos is None:
        await cd.send("目录不存在")
    else:
        Dir = newDir
        msg = ""
        for info in infos:
            if info["isdir"] == 1:
                msg += info["server_filename"] + "/\n"
            else:
                msg += info["server_filename"] + "\n"
        await cd.send(f"[pan]$    {Dir}>")
        if len(infos) > 10 and isinstance(event, GroupMessageEvent):
            msg = Nodes(qID=event.self_id, name="妃爱网盘", content=msg)
            await bot.call_api("send_group_forward_msg", **{"group_id": event.group_id, "messages": msg.msg()})
        else:
            await myPan.send(msg)
    return


@download.handle()
async def _(bot: Bot, event: MessageEvent):
    """在群聊中将上传至群文件，在私聊中将上传私聊文件"""
    global Dir
    file = re.sub(r"^pan\s+dl\s+", string=str(event.message), repl="")
    if file.startswith("/"):
        file = file
    else:
        file = os.path.normpath(Dir + file)
        file = file.replace("\\", "/")
    fileName = os.path.basename(file)
    DirExist("Data/BaiduPan/Cache")
    localPath = os.path.abspath(os.path.join("Data/BaiduPan/Cache", str(random.randint(1, 10 ** 10)) + ".hiyoriCache"))
    try:
        await baiduPan.downloadFile(localPath=localPath, panPath=file)
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
