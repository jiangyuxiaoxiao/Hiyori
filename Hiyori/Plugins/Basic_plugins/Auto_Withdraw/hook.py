"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/4-16:23
@Desc: 
@Ver : 1.0.0
"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent
from nonebot import get_bot
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from .config import autoWithdrawConfig


# 当bot发送消息后触发，若设置了定时则撤回对应消息
@Bot.on_called_api
async def withdrawSelfMessage(bot: Bot, exception: Exception, api: str, data: dict[str, any], result: any):
    """
    bot发送消息后定时进行撤回。
    """
    # 必须是发送消息的事件
    if api not in ["send_msg", "send_group_msg", "send_private_msg", "send_group_forward_msg", "send_private_forward_msg"]:
        return
    # 必须是群聊事件
    if "group_id" in data:
        GroupID: str = str(data["group_id"])
        # 有群组配置
        if GroupID in autoWithdrawConfig.groupConfig.keys():
            GroupConfig = autoWithdrawConfig.groupConfig[GroupID]
            # 群组开启撤回
            if GroupConfig["on"]:
                asyncio.create_task(withDrawMessage(bot, result["message_id"], GroupConfig["time"]))
        # 无群组配置，默认撤回
        elif autoWithdrawConfig.defaultOn:
            asyncio.create_task(withDrawMessage(bot, result["message_id"], autoWithdrawConfig.defaultWithdrawTime))


# 当事件响应器运行前触发，若设置了定时则撤回目标的消息
@run_preprocessor
async def withdrawTargetMessage(event: MessageEvent, matcher: Matcher):
    if hasattr(event, "group_id"):
        GroupID: str = str(event.group_id)
        # 若群组事件默认撤回：
        if autoWithdrawConfig.defaultOn:
            # 有群组配置
            if GroupID in autoWithdrawConfig.groupConfig.keys():
                GroupConfig = autoWithdrawConfig.groupConfig[GroupID]
                # 群组未开启
                if GroupConfig["on"]:
                    bot = get_bot(str(event.self_id))
                    asyncio.create_task(withDrawMessage(bot, event.message_id, GroupConfig["time"]))
            # 无群组配置
            else:
                bot = get_bot(str(event.self_id))
                asyncio.create_task(withDrawMessage(bot, event.message_id, autoWithdrawConfig.defaultWithdrawTime))


# 定时撤回执行函数
async def withDrawMessage(bot: Bot, message_id: int, time: int):
    await asyncio.sleep(time)
    try:
        await bot.delete_msg(message_id=message_id)
    except Exception as e:
        pass
