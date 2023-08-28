"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/28-15:32
@Desc: 私人百度网盘CLI demo
@Ver : 1.0.0
"""
import re
import os

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent

from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.Permissions import HIYORI_OWNER
import Hiyori.Utils.API.Baidu.Pan as baiduPan

Dir = "/"

myPan = on_regex(r"^pan\s+ls$", permission=HIYORI_OWNER, priority=Priority.系统优先级, block=True)
cd = on_regex(r"^pan\s+cd\s+", permission=HIYORI_OWNER, priority=Priority.系统优先级, block=True)


@myPan.handle()
async def _(event: MessageEvent):
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
    await myPan.send(msg)


@cd.handle()
async def _(event: MessageEvent):
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
        await myPan.send(msg)
    return
