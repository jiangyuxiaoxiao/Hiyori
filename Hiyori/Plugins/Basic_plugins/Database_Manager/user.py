"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:31
@Desc: 用户数据库相关
@Ver : 1.0.0
"""
from nonebot import get_driver
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, Event
from Hiyori.Utils.Database import DB_User
from Hiyori.Utils.Priority import Priority

# 用户数据库刷新，根据群列表以及群成员列表更新User,Group表以及对应内存
update_all = on_regex("(^#用户数据库刷新$)|(^#refresh\\s+[d,D][b,B])$", priority=Priority.系统优先级, block=True)
# 用户数据库重载，将数据库重新载入内存
reload_all = on_regex("(^#用户数据库重载$)|(^#reload\\s+[d,D][b,B])$", priority=Priority.系统优先级, block=True)

config = get_driver().config


@update_all.handle()
async def _(bot: Bot, event: Event):
    global config
    if hasattr(event, "user_id"):
        if str(event.user_id) in config.superusers or DB_User.isOwner(event.user_id):
            await DB_User.refreshAll()
            await update_all.send("用户数据库刷新成功")


@reload_all.handle()
async def _(bot: Bot, event: Event):
    global config
    if hasattr(event, "user_id"):
        if str(event.user_id) in config.superusers or DB_User.isOwner(event.user_id):
            DB_User.reload()
            await reload_all.send("用户数据库重载成功")
