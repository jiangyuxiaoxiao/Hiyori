"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/30-21:34
@Desc: 发言自动定时撤回
@Ver : 1.0.0
"""
import re

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from Hiyori.Utils.Permissions import HIYORI_OWNER, HIYORI_ADMIN
from Hiyori.Utils.Priority import Priority
from .config import autoWithdrawConfig
from .hook import *

__plugin_meta__ = PluginMetadata(
    name="群聊消息自动撤回",
    description="开启后妃爱将定时撤回自己发送的消息",
    usage="#开启定时撤回\n"
          "#开启定时撤回 定时时间\n"
          "#关闭定时撤回\n"
          "#修改定时撤回时间 定时时间\n"
          "#查看定时撤回状态\n",
    extra={
        "CD_Weight": 5,
        "permission": "群管/妃爱管理员及以上权限",
        "example": "",
        "Keep_On": True,
        "Type": "Admin_Plugin",
    },
)

StatusOn = on_regex(r"^#?开启定时撤回", permission=GROUP_ADMIN | GROUP_OWNER | HIYORI_ADMIN | HIYORI_OWNER | SUPERUSER,
                    priority=Priority.系统优先级, block=True)
StatusOff = on_regex(r"^#?关闭定时撤回", permission=GROUP_ADMIN | GROUP_OWNER | HIYORI_ADMIN | HIYORI_OWNER | SUPERUSER,
                     priority=Priority.系统优先级, block=True)
ChangeTime = on_regex(r"^#?修改定时撤回时间", permission=GROUP_ADMIN | GROUP_OWNER | HIYORI_ADMIN | HIYORI_OWNER | SUPERUSER,
                      priority=Priority.系统优先级, block=True)

CheckStatus = on_regex(r"^#?查看定时撤回状态", priority=Priority.系统优先级, block=True)


@StatusOn.handle()
async def _(event: GroupMessageEvent):
    message = str(event.message)
    time = re.sub(r"^#?开启定时撤回", string=message, repl="").strip()
    # 配置文件中本群组不存在
    if str(event.group_id) not in autoWithdrawConfig.groupConfig.keys():
        if time.isdigit():
            time = int(time)
        else:
            time = autoWithdrawConfig.defaultWithdrawTime
    else:
        if time.isdigit():
            time = int(time)
        else:
            time = autoWithdrawConfig.groupConfig[str(event.group_id)]["time"]
    if time > autoWithdrawConfig.maxWithdrawTime:
        await StatusOn.send(f"最长可以设置的定时时间为{autoWithdrawConfig.maxWithdrawTime}秒")
        return

    autoWithdrawConfig.groupConfig[str(event.group_id)] = {
        "on": True,
        "time": time
    }
    autoWithdrawConfig.dump()
    await StatusOn.send(f"本群组已开启定时撤回，定时{time}秒")


@StatusOff.handle()
async def _(event: GroupMessageEvent):
    # 配置文件中本群组不存在
    if str(event.group_id) not in autoWithdrawConfig.groupConfig.keys():
        autoWithdrawConfig.groupConfig[str(event.group_id)] = {
            "on": False,
            "time": autoWithdrawConfig.defaultWithdrawTime
        }
    else:
        autoWithdrawConfig.groupConfig[str(event.group_id)]["on"] = False
    autoWithdrawConfig.dump()
    await StatusOff.send("本群组已关闭定时撤回")


@ChangeTime.handle()
async def _(event: GroupMessageEvent):
    message = str(event.message)
    time = re.sub(r"^#?修改定时撤回时间", string=message, repl="").strip()
    if time.isdigit():
        time = int(time)
    else:
        time = autoWithdrawConfig.defaultWithdrawTime
    if time > autoWithdrawConfig.maxWithdrawTime:
        await ChangeTime.send(f"最长可以设置的定时时间为{autoWithdrawConfig.maxWithdrawTime}秒")
        return
    # 配置文件中不存在
    if str(event.group_id) not in autoWithdrawConfig.groupConfig.keys():
        autoWithdrawConfig.groupConfig[str(event.group_id)] = {
            "on": False,
            "time": time
        }
    else:
        autoWithdrawConfig.groupConfig[str(event.group_id)]["time"] = time
    autoWithdrawConfig.dump()
    await StatusOff.send(f"本群组定时撤回设定时间已改为{time}")


@CheckStatus.handle()
async def _(event: GroupMessageEvent):
    if str(event.group_id) not in autoWithdrawConfig.groupConfig.keys():
        status = f"已开启，设定时间{autoWithdrawConfig.defaultWithdrawTime}" if autoWithdrawConfig.defaultOn else "未开启"
        await CheckStatus.send(f"当前设定状态：定时撤回{status}")
    else:
        on = autoWithdrawConfig.groupConfig[str(event.group_id)]["on"]
        time = autoWithdrawConfig.groupConfig[str(event.group_id)]["time"]
        status = f"已开启，设定时间{time}" if on else "未开启"
        await CheckStatus.send(f"当前设定状态：定时撤回{status}")
