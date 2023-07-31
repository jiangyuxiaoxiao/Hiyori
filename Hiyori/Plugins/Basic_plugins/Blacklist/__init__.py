"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:28
@Desc: 黑名单管理插件
@Ver : 1.0.0
"""
from .hook import check_blacklist  # 黑名单审核
from .hook import check_group_switch  # 群开关检查
from nonebot import on_startswith, on_regex
from nonebot.adapters.onebot.v11 import Event, GroupMessageEvent, GROUP_OWNER, GROUP_ADMIN
from Hiyori.Utils.Database import DB_User
from Hiyori.Utils.Permissions import Hiyori_OWNER, Hiyori_ADMIN
from Hiyori.Utils.Priority import Priority
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="群聊开关",
    description="开启或关闭妃爱在对应群聊的响应。呜，妃爱还不想睡觉！",
    usage="#开机\n"
          "#关机\n",
    extra={
        "CD_Weight": 5,
        "permission": "群管/妃爱管理员及以上权限",
        "example": "",
        "Keep_On": True,
        "Type": "Admin_Plugin",
    },
)

setBlacklist = on_startswith(("#设置黑名单", "#ban"), priority=Priority.系统优先级, block=True,
                             permission=Hiyori_OWNER | SUPERUSER)
unsetBlacklist = on_startswith(("#解除黑名单", "#unban"), priority=Priority.系统优先级, block=True,
                               permission=Hiyori_OWNER | SUPERUSER)
switchOn = on_regex(r"(^#开机$)|(^#?switch\s+on$)|(^#?change\s+status\s+on$)", priority=Priority.系统优先级, block=True,
                    permission=Hiyori_OWNER | SUPERUSER | GROUP_OWNER | GROUP_ADMIN | Hiyori_ADMIN)
switchOff = on_regex(r"(^#关机$)|(^#?switch\s+off$)|(^#?change\s+status\s+off$)", priority=Priority.系统优先级,
                     block=True,
                     permission=Hiyori_OWNER | SUPERUSER | GROUP_OWNER | GROUP_ADMIN | Hiyori_ADMIN)


# config = get_driver().config  # 获取nb env文件属性的方法
# config.superusers  # 举例 获取全部的superusers

# 设置黑名单
@setBlacklist.handle()
async def _(event: Event):
    # 指令处理解析
    message = str(event.message)
    message = message.replace("#设置黑名单", "").lstrip()
    message = message.replace("#ban", "").lstrip()
    # -u 指令 根据QQ号进行封禁用户
    if message.startswith("-u") or message.startswith("-U"):
        message = message.replace("-u", "").lstrip()
        message = message.replace("-U", "").lstrip()
        # 通过直接@获取QQ号
        if message.startswith("[CQ:at,qq="):
            message = message.replace("[CQ:at,qq=", "")
            message = message.replace("]", "")
        # 检查输入格式是否正确
        if message.isdigit():
            QQ = int(message)
            # 若未查询到用户，则会先刷新一遍
            if not DB_User.hasUser(QQ):
                await DB_User.refreshAll()
                if not DB_User.hasUser(QQ):
                    await setBlacklist.send("用户不存在")
                    return
            user = DB_User.getUser(QQ)
            user.Permission = 3
            DB_User.updateUser(user)
            await setBlacklist.send("封禁成功")
            return
        else:
            await setBlacklist.send("QQ格式不正确")
    # -g 指令 根据群号进行封禁
    elif message.startswith("-g") or message.startswith("-G"):
        message = message.replace("-g", "").lstrip()
        message = message.replace("-G", "").lstrip()
        # 若message已为空，则封禁群组
        if len(message) == 0:
            if hasattr(event, "group_id"):
                GroupID = event.group_id
                group = DB_User.getGroup(GroupID)
                group.Permission = 3
                DB_User.updateGroup(group)
                await setBlacklist.send("封禁成功")
            else:
                await setBlacklist.send("需要在群内发送")
            return
        # 若message不为空，则解析群号
        if message.isdigit():
            GroupID = int(message)
            # 若未查询到用户，则会先刷新一遍
            if not DB_User.hasGroup(GroupID):
                await DB_User.refreshAll()
                if not DB_User.hasGroup(GroupID):
                    await setBlacklist.send("群组不存在")
                    return
            group = DB_User.getGroup(GroupID)
            group.Permission = 3
            DB_User.updateGroup(group)
            await setBlacklist.send("封禁成功")
            return
        else:
            await setBlacklist.send("群号格式不正确")


# 解除黑名单
# noinspection DuplicatedCode
@unsetBlacklist.handle()
async def _(event: Event):
    # 指令处理解析
    message = str(event.message)
    message = message.replace("#解除黑名单", "").lstrip()
    message = message.replace("#unban", "").lstrip()
    # -u 指令 根据QQ号进行用户解封
    if message.startswith("-u") or message.startswith("-U"):
        message = message.replace("-u", "").lstrip()
        message = message.replace("-U", "").lstrip()
        # 通过直接@获取QQ号
        if message.startswith("[CQ:at,qq="):
            message = message.replace("[CQ:at,qq=", "")
            message = message.replace("]", "")
        # 检查输入格式是否正确
        if message.isdigit():
            QQ = int(message)
            # 若未查询到用户，则会先刷新一遍
            if not DB_User.hasUser(QQ):
                await DB_User.refreshAll()
                if not DB_User.hasUser(QQ):
                    await setBlacklist.send("用户不存在")
                    return
            user = DB_User.getUser(QQ)
            user.Permission = 2
            DB_User.updateUser(user)
            await setBlacklist.send("解封成功")
            return
        else:
            await setBlacklist.send("QQ格式不正确")
    # -g 指令 根据群号进行封禁
    elif message.startswith("-g") or message.startswith("-G"):
        message = message.replace("-g", "").lstrip()
        message = message.replace("-G", "").lstrip()
        # 若message已为空，则封禁群组
        if len(message) == 0:
            if hasattr(event, "group_id"):
                GroupID = event.group_id
                group = DB_User.getGroup(GroupID)
                group.Permission = 2
                DB_User.updateGroup(group)
                await setBlacklist.send("解封成功")
            else:
                await setBlacklist.send("需要在群内发送")
            return
        # 若message不为空，则解析群号
        if message.isdigit():
            GroupID = int(message)
            # 若未查询到用户，则会先刷新一遍
            if not DB_User.hasGroup(GroupID):
                await DB_User.refreshAll()
                if not DB_User.hasGroup(GroupID):
                    await setBlacklist.send("群组不存在")
                    return
            group = DB_User.getGroup(GroupID)
            group.Permission = 2
            DB_User.updateGroup(group)
            await setBlacklist.send("解封成功")
            return
        else:
            await setBlacklist.send("群号格式不正确")


# 群状态改为开启
@switchOn.handle()
async def _(event: GroupMessageEvent):
    GroupID = event.group_id
    Group = DB_User.getGroup(GroupID)
    if Group.Status != "on":
        Group.Status = "on"
        DB_User.updateGroup(Group)
        await switchOn.send("妃爱开机啦~")
    else:
        await switchOn.send("好烦哦，妃爱已经开机啦！")


# 群状态改为关机
@switchOff.handle()
async def _(event: GroupMessageEvent):
    GroupID = event.group_id
    Group = DB_User.getGroup(GroupID)
    if Group.Status != "off":
        Group.Status = "off"
        DB_User.updateGroup(Group)
        await switchOff.send("妃爱关机啦~")
