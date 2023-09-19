"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:29
@Desc: 
@Ver : 1.0.0
"""
from nonebot import get_driver
from nonebot.message import event_preprocessor, run_preprocessor
from nonebot.exception import IgnoredException
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, Event
from Hiyori.Utils.Database import DB_User

config = get_driver().config


# 黑名单审核
@event_preprocessor
async def check_blacklist(bot: Bot, event: Event):
    global config
    if hasattr(event, "user_id"):
        QQ = event.user_id
        permission = DB_User.getUser(QQ).Permission
        if permission == 3:
            raise IgnoredException("用户黑名单屏蔽")
        # 对于主人和管理员发起的事件，无视黑名单审核
        if permission in (0, 1) or str(QQ) in config.superusers:
            if hasattr(event, "group_id"):
                # 确保群聊存在
                GroupID = event.group_id
                DB_User.groupExist(GroupID)
            return
    if hasattr(event, "group_id"):
        GroupID = event.group_id
        permission = DB_User.getGroup(GroupID).Permission
        if permission == 3:
            raise IgnoredException("群黑名单屏蔽")


# 群开关审核
@run_preprocessor
async def check_group_switch(matcher: Matcher, bot: Bot, event: Event):
    global config
    # 放行特殊插件
    if matcher.plugin_name in ("Database_Manager", "Blacklist"):
        return
    if hasattr(event, "user_id"):
        QQ = event.user_id
        permission = DB_User.getUser(QQ).Permission
        # 对于主人和管理员发起的事件，无视黑名单审核
        if permission in (0, 1) or str(QQ) in config.superusers:
            return
    if hasattr(event, "group_id"):
        GroupID = event.group_id
        Status = DB_User.getGroup(GroupID).Status
        if Status == "off":
            raise IgnoredException("群开关关闭")



















