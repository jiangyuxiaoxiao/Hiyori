"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/1-0:21
@Desc: 戳戳动作
@Ver : 1.0.0
"""
import random
from nonebot.adapters.onebot.v11 import PokeNotifyEvent, Bot
from nonebot import on_notice
from Hiyori.Utils.Priority import Priority
from nonebot.plugin import PluginMetadata
from .rule import isPokeEvent

__plugin_meta__ = PluginMetadata(
    name="戳一戳",
    description="不要再戳妃爱啦",
    usage="",
    extra={
        "CD_Weight": 2,
        "permission": "普通权限",
        "example": "",
        "Keep_On": False,
        "Type": "Auto_Plugin",
    },
)

poke__reply = [
    "不要戳妃爱啦！>_<",
    "你再戳！",
    "？再戳试试？",
    "再戳一下试试？",
    "呼~妃爱睡着了"
]

poke = on_notice(priority=Priority.普通优先级, rule=isPokeEvent, block=False)


@poke.handle()
async def _(bot: Bot, event: PokeNotifyEvent):
    if event.sender_id != event.target_id and event.target_id == event.self_id:
        QQ = event.user_id
        GroupID = event.group_id
        message = f"[CQ:poke,qq={QQ}]"
        await bot.call_api("send_group_msg", **{"group_id": GroupID, "message": message})
        message = random.choice(poke__reply)
        await bot.call_api("send_group_msg", **{"group_id": GroupID, "message": message})
