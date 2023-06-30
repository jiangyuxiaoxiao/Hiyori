"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/1-0:20
@Desc: 昵称插件
@Ver : 1.0.0
"""
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot import on_regex
import re

from Hiyori.Utils.Database import DB_User
from Hiyori.Utils.Priority import Priority

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="昵称设置",
    description="设置自己的昵称，让妃爱记住你的名字",
    usage="#改名 昵称 【改为对应的昵称】\n"
          "#改名 【清除昵称设置】",
    extra={
        "CD_Weight": 2,
        "permission": "普通权限",
        "example": "",
        "Keep_On": False,
        "Type": "Normal_Plugin",
    },
)

ChangeName = on_regex(r"^#改名", block=False, priority=Priority.普通优先级)


@ChangeName.handle()
async def _(event: MessageEvent):
    message = str(event.message)
    message = re.sub(pattern=r"^#改名", repl="", string=message).strip()
    User = DB_User.getUser(QQ=event.user_id)
    User.NickName = message
    DB_User.updateUser(User)
    msg = MessageSegment.at(event.user_id) + f"妃爱记住你的新名字{message}啦！"
    await ChangeName.send(msg)
