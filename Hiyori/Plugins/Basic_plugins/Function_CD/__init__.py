"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:32
@Desc: 调用冷却插件
@Ver : 1.0.0
"""
from .hook import 功能调用CD检查
from nonebot.adapters.onebot.v11 import Event, Bot
from Hiyori.Utils.Permissions import HIYORI_OWNER
from nonebot.permission import SUPERUSER
from nonebot import on_regex
from Hiyori.Utils.Database import DB_User
from Hiyori.Utils.Priority import Priority
import re
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="响应冷却",
    description="每次功能调用时触发所在群以及调用者的功能调用权重累积，超限后停止响应。",
    usage="功能调用时自动触发\n"
          "用户默认权重为10/分钟，群组默认权重为30/分钟，统计周期为5分钟。",
    extra={
        "example": "",
        "Keep_On": True,
        "Type": "Auto_Plugin",
    },
)

changeCD = on_regex(r"(^#?change\s+cd)|(^#?CD修改)|(^#?cd修改)", priority=Priority.系统优先级, block=True,
                    permission=HIYORI_OWNER | SUPERUSER)


@changeCD.handle()
async def _(bot: Bot, event: Event):
    # 指令处理解析
    message = str(event.message)
    message = re.sub(r"(^#?change\s+(cd)|(CD))|(^#?CD修改)|(^#?cd修改)", "", message).lstrip()
    # 模式匹配
    # -u指令 修改用户CD
    if message.startswith("-u") or message.startswith("-U"):
        message = re.sub(r"(^-u)|(^-U)", "", message).lstrip()
        # CQ码去除
        if message.startswith("[CQ:at,qq="):
            message = message.replace("[CQ:at,qq=", "").lstrip()
            message = message.replace("]", "").lstrip()
        # 检查输入格式是否正确
        msgs = message.split(" ")
        # isdigit已经包含了不为负数的隐藏条件
        if len(msgs) == 2 and msgs[0].isdigit() and msgs[1].isdigit():
            QQ = int(msgs[0])
            CD = int(msgs[1])
            # 若未查询到用户，则会先刷新一遍
            if not DB_User.hasUser(QQ):
                await DB_User.refreshAll()
                if not DB_User.hasUser(QQ):
                    await changeCD.send("用户不存在")
                    return
            User = DB_User.getUser(QQ)
            LastCD = User.CD
            User.CD = CD
            DB_User.updateUser(User)
            await changeCD.send("用户 {} 功能调用权重上限: {} → {}".format(User.Name, LastCD, CD))
        else:
            await changeCD.send("QQ号或者CD格式不正确，或者不存在对应用户")
    # -g指令 修改群组CD
    elif message.startswith("-g") or message.startswith("-G"):
        message = re.sub(r"(^-g)|(^-G)", "", message).lstrip()
        msgs = message.split(" ")
        # 直接修改所在群组
        # isdigit已经包含了不为负数的隐藏条件
        if len(msgs) == 1 and msgs[0].isdigit() and hasattr(event, "group_id"):
            GroupID = event.group_id
            CD = int(msgs[0])
            Group = DB_User.getGroup(GroupID)
            LastCD = Group.CD
            Group.CD = CD
            DB_User.updateGroup(Group)
            await changeCD.send("群组 {} 功能调用权重上限: {} → {}".format(Group.GroupName, LastCD, CD))
        # 修改指定群组
        # isdigit已经包含了不为负数的隐藏条件
        elif len(msgs) == 2 and msgs[0].isdigit() and msgs[1].isdigit():
            GroupID = int(msgs[0])
            CD = int(msgs[1])
            # 检查群组是否存在，不存在则先刷新一次，再检测:
            if not DB_User.hasGroup(GroupID):
                await DB_User.refreshAll()
                if not DB_User.hasGroup(GroupID):
                    await changeCD.send("群组不存在")
                    return
            Group = DB_User.getGroup(GroupID)
            LastCD = Group.CD
            Group.CD = CD
            DB_User.updateGroup(Group)
            await changeCD.send("群组 {} 功能调用权重上限: {} → {}".format(Group.GroupName, LastCD, CD))
        else:
            await changeCD.send("群号或者CD格式不正确，或者不存在对应群聊")

