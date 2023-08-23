"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/4-8:02
@Desc: 多BOT连接支持插件：每个群聊最多仅有一个bot响应
@Ver : 1.0.0
"""
from nonebot import on_regex, get_bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, Bot, Event
from nonebot.permission import SUPERUSER
from nonebot.message import handle_event

from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.Permissions import HIYORI_OWNER
from Hiyori.Utils.Message.At import GetAtQQs
from Hiyori.Utils.API.QQ import GetQQStrangerName

from .config import multiBotConfig
from .hook import *

HiyoriStart = on_regex(pattern=r"妃爱启动", permission=SUPERUSER | HIYORI_OWNER, priority=Priority.系统优先级)
CheckStatus = on_regex(pattern=r"^#?状态$", permission=SUPERUSER, priority=Priority.系统优先级, block=False)


@HiyoriStart.handle()
async def _(event: GroupMessageEvent):
    message = str(event.message)
    QQList = GetAtQQs(message)
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


def getBot(GroupID: int | str) -> Bot | None:
    """
    在多Bot连接的情况下，根据群组ID来返回对应的Bot。如果群组无对应Bot，则返回None。

    :param GroupID: 群号
    """
    bots = get_bots()
    GroupID = str(GroupID)
    # 群组不在特殊规则中
    if GroupID not in multiBotConfig.rule.keys():
        # 遍历响应优先序列，按顺序找到第一个已开启且在本群聊中的QQ
        for botQQ in multiBotConfig.priority:
            # 对应Bot已开启 而且这个Bot在群聊中
            if (botQQ in bots) and (GroupID in multiBotConfig.groupSet[botQQ]):
                return get_bot(self_id=botQQ)
        # 没找到就返回None
        return None
    else:
        # 特定规则指定的QQ
        ruleQQ = multiBotConfig.rule[GroupID]
        # 特定规则指定的QQ已开启
        if ruleQQ in bots.keys():
            return get_bot(self_id=ruleQQ)
        else:
            # 则按照顺序优先级返回
            for botQQ in multiBotConfig.priority:
                # 对应Bot已开启 而且这个Bot在群聊中
                if (botQQ in bots) and (GroupID in multiBotConfig.groupSet[botQQ]):
                    return get_bot(self_id=botQQ)
            # 没找到就返回None
            return None


@CheckStatus.handle()
async def _(bot: Bot):
    msg = "当前已连接Bot列表：\n"
    for hiyori in multiBotConfig.activeBots:
        name = await GetQQStrangerName(bot=bot, QQ=int(hiyori))
        msg += f"{name}({hiyori})\n"
    await CheckStatus.send(msg)
