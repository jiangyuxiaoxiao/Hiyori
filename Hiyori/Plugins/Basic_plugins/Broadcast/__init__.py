"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:30
@Desc: 广播插件
@Ver : 1.0.0
"""
import time
import asyncio
from Hiyori.Utils.Database import DB_User
from Hiyori.Utils.Permissions import HIYORI_OWNER
from Hiyori.Utils.Priority import Priority
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot, PrivateMessageEvent, ActionFailed
from nonebot import on_regex
from nonebot.log import logger
import re

broadcast = on_regex(r"^#broadcast", permission=SUPERUSER | HIYORI_OWNER, priority=Priority.系统优先级, block=True)


@broadcast.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    startTime = time.time_ns()
    # 获取对应广播信息
    message = str(event.message)
    message = re.sub(r"^#broadcast", "", message).lstrip()
    GroupsDict = DB_User.getAllGroups()
    for Group in GroupsDict.values():
        # 群组状态为关闭
        if Group.Permission == 3:
            continue
        else:
            # 群组需要有效
            try:
                await bot.call_api("send_group_msg", **{"group_id": Group.GroupID, "message": message})
                await asyncio.sleep(1)
            except ActionFailed:
                logger.error(f"群组{Group.GroupID}发送消息失败")
                continue

    endTime = time.time_ns()
    Time = (endTime - startTime)/1000000000
    await broadcast.send(f"消息已广播完毕, 用时{Time:.3f}s")


