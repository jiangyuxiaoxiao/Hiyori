"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/4-8:02
@Desc: 多BOT连接支持插件：每个群聊最多仅有一个bot响应
@Ver : 1.0.0
"""
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.permission import SUPERUSER

from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.Permissions import HIYORI_OWNER
from Hiyori.Utils.Message.At import GetAtQQ

from .config import multiBotConfig
from .hook import *


HiyoriStart = on_regex(pattern=r"妃爱启动", permission=SUPERUSER | HIYORI_OWNER, priority=Priority.系统优先级)


@HiyoriStart.handle()
async def _(event: GroupMessageEvent):
    message = str(event.message)
    QQList = GetAtQQ(message)
    if event.to_me:
        QQList.append(event.self_id)
    # 指令没艾特人
    if len(QQList) == 0:
        msg = MessageSegment.at(event.user_id) + "请艾特需要启动的妃爱哦"
        await HiyoriStart.send(msg)
        return
    QQ = str(QQList[0])  # at中的第一个QQ
    # 在响应序列中
    if QQ in multiBotConfig.priority:
        await HiyoriStart.send("妃爱，启动！")
        multiBotConfig.rule[str(event.group_id)] = QQ
        multiBotConfig.dump()
    else:
        msg = MessageSegment.at(event.user_id) + "你艾特的对象不是妃爱哦"
        await HiyoriStart.send(msg)
    return


