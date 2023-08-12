"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/9-21:06
@Desc: 早晚安
@Ver : 1.0.0
"""

import asyncio
import os.path
import random

from nonebot.adapters.onebot.v11 import Bot
from nonebot.plugin import PluginMetadata

from Hiyori.Plugins.Basic_plugins.nonebot_plugin_apscheduler import scheduler
from Hiyori.Plugins.Basic_plugins.Plugin_Manager import pluginsManager
from Hiyori.Plugins.Basic_plugins.MultiBot_Support import getBot
from Hiyori.Utils.Database.user import DB_User
from Hiyori.Utils.Message.Record import RecordMessage

__plugin_meta__ = PluginMetadata(
    name="妃爱晚安",  # 用于在菜单显示 用于插件开关
    description="妃爱早安~",  # 用于在菜单中描述
    usage="早晚自动触发",
    extra={"CD_Weight": 0,  # 调用插件CD权重 不填的话不会触发权重插件
           "example": "",
           "Group": "Feature",
           "version": "1.0",
           "Keep_On": False,
           "Type": "Auto_Plugin",
           }
)


# 早安
@scheduler.scheduled_job("cron", hour=7, minute=30, misfire_grace_time=60)
async def Ohayou():
    GroupsDict = DB_User.getAllGroups()
    RecordDir = "./Data/Src/Sound/Hiyori"
    RecordList = ["fem_hiy_11472.ogg", "fem_hiy_12257.ogg"]

    for Group in GroupsDict.values():
        # 黑名单
        if Group.Permission == 3:
            continue
        # 群组关闭
        if Group.Status == "off":
            continue
        # 插件关闭
        if not pluginsManager.GroupPluginIsOn(GroupID=str(Group.GroupID), PluginName="妃爱晚安"):
            continue
        else:
            try:
                bot: Bot = getBot(Group.GroupID)
                record: str = random.choice(RecordList)
                RecordMsg = RecordMessage(os.path.join(RecordDir, record))
                await bot.send_group_msg(message="大家早上好~", group_id=Group.GroupID)
                await bot.send_group_msg(message=RecordMsg, group_id=Group.GroupID)
                await asyncio.sleep(1)
            except Exception:
                continue


# 晚安
@scheduler.scheduled_job("cron", hour=0, minute=30, misfire_grace_time=60)
async def Oyasumi():
    GroupsDict = DB_User.getAllGroups()
    RecordDir = "./Data/Src/Sound/Hiyori"
    RecordList = ["fem_hiy_10197.ogg"]
    for Group in GroupsDict.values():
        # 黑名单
        if Group.Permission == 3:
            continue
        # 群组关闭
        if Group.Status == "off":
            continue
        # 插件关闭
        if not pluginsManager.GroupPluginIsOn(GroupID=str(Group.GroupID), PluginName="妃爱晚安"):
            continue
        else:
            try:
                bot: Bot = getBot(Group.GroupID)
                record: str = random.choice(RecordList)
                RecordMsg = RecordMessage(os.path.join(RecordDir, record))
                await bot.send_group_msg(message="大家晚安~", group_id=Group.GroupID)
                await bot.send_group_msg(message=RecordMsg, group_id=Group.GroupID)
                await asyncio.sleep(1)
            except Exception:
                continue
