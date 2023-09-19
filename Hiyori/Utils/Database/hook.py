"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/09/19-08:35
@Desc: nonebot2钩子函数
@Ver : 1.0.0
"""
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent, FriendAddNoticeEvent, Bot
from nonebot import on_notice

from Hiyori.Utils.Priority import Priority

from .user import DB_User

updateUser = on_notice(block=False, priority=Priority.系统优先级)


@updateUser.handle()
async def _(event: GroupIncreaseNoticeEvent | FriendAddNoticeEvent):
    if isinstance(event, GroupIncreaseNoticeEvent):
        DB_User.userExist(QQ=event.user_id)
        logger.success(f"群聊{event.group_id}新增成员{event.user_id}，已更新添加用户信息。")
    else:
        DB_User.userExist(QQ=event.user_id)
        logger.success(f"添加好友{event.user_id}，已更新用户信息。")
