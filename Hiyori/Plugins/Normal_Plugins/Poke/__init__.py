"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/1-0:21
@Desc: 戳戳动作
@Ver : 1.0.0
"""
from nonebot.adapters.onebot.v11 import PokeNotifyEvent, MessageSegment, Bot
from nonebot import on_notice
from Hiyori.Utils.Priority import Priority

poke = on_notice(priority=Priority.普通优先级, block=False)


@poke.handle()
async def _(bot: Bot, event: PokeNotifyEvent):
    if event.sender_id != event.target_id and event.target_id == event.self_id:
        QQ = event.user_id
        GroupID = event.group_id
        message = f"[CQ:poke,qq={QQ}]"
        await bot.call_api("send_group_msg", **{"group_id": GroupID, "message": message})
        message = "不要戳妃爱啦！>_<"
        await bot.call_api("send_group_msg", **{"group_id": GroupID, "message": message})
