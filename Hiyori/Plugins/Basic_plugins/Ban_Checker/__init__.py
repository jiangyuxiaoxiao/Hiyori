"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:27
@Desc: 双向禁言插件
@Ver : 1.0.0
"""
from nonebot.adapters.onebot.v11 import GroupBanNoticeEvent, Bot
from nonebot import on_notice
from nonebot import get_driver
from nonebot import get_bots
from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.Database.user import DB_User

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="双向禁言",  # 用于在菜单显示 用于插件开关
    description="禁言审核，当妃爱被所在群禁言时会自动拉黑对应群聊。\n"
                "需要关闭妃爱的回复响应请参考【群聊开关】插件，请勿随意禁言。",  # 用于在菜单中描述
    usage="被禁言时自动触发",
    extra={"example": "",
           "Group": "Daily",
           "version": "1.0",
           "Keep_On": True,
           "Type": "Auto_Plugin",
           }
)

superusers = get_driver().config.superusers

Ban_Checker = on_notice(block=False, priority=Priority.系统优先级)


@Ban_Checker.handle()
async def _(bot: Bot, event: GroupBanNoticeEvent):
    global superusers
    bots = get_bots().values()
    botsID = {int(b.self_id) for b in bots}
    # 如果自己被禁言了 或者群中的其他bot被禁言
    if (event.self_id == event.user_id) or (event.user_id in botsID):
        # 封禁对应群聊
        GroupID = event.group_id
        Group = DB_User.getGroup(GroupID)
        Group.Permission = 3
        DB_User.updateGroup(Group)
        # 发送消息给开发者
        group_info = await bot.get_group_info(group_id=event.group_id)
        group_name = group_info["group_name"]
        message = f"群{group_name}({GroupID})触发封禁反击机制"
        for superuser in superusers:
            await bot.send_private_msg(user_id=int(superuser), message=message)
