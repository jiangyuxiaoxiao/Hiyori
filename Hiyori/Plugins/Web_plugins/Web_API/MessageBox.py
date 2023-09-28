"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/09/23-07:39
@Desc:
@Ver : 1.0.0
"""
from nonebot import get_asgi
from nonebot.adapters.onebot.v11 import Bot
from Hiyori.Plugins.Basic_plugins.MultiBot_Support import getBot
import fastapi

app = get_asgi()


@app.get("/Plugins/Web_plugins/Web_API/Message/Send")
async def _(message: str, QQ: int = 0, GroupID: int = 0):
    if QQ != 0:
        pass
    else:
        bot = getBot(GroupID)
        if bot is not None:
            await bot.send_group_msg(group_id=GroupID, message=message)
            return {"result": "ok"}

