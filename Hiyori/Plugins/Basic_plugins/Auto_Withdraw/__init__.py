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

StatusOn = on_regex(r"^#?开启定时撤回", permission=GROUP_ADMIN | GROUP_OWNER | HIYORI_ADMIN | HIYORI_OWNER | SUPERUSER,
                    priority=Priority.系统优先级, block=True)
StatusOff = on_regex(r"^#?关闭定时撤回", permission=GROUP_ADMIN | GROUP_OWNER | HIYORI_ADMIN | HIYORI_OWNER | SUPERUSER,
                     priority=Priority.系统优先级, block=True)
ChangeTime = on_regex(r"^#?修改定时撤回时间", permission=GROUP_ADMIN | GROUP_OWNER | HIYORI_ADMIN | HIYORI_OWNER | SUPERUSER,
                      priority=Priority.系统优先级, block=True)


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
