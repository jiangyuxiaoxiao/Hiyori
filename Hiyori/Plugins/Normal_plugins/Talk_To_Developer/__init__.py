"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/2-15:16
@Desc: 与开发者对话
@Ver : 1.0.0
"""

from nonebot import get_driver
from nonebot import on_regex
from nonebot.params import Received
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, GroupMessageEvent, MessageSegment

from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.API.QQ import GetQQStrangerName, GetQQGrouperName, GetGroupName
from Hiyori.Utils.Message.Forward_Message import Nodes

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="对话开发者",  # 用于在菜单显示 用于插件开关
    description="对话开发者",  # 用于在菜单中描述
    usage="#对话开发者 【对话内容】",
    extra={"CD_Weight": 5,  # 调用插件CD权重 不填的话不会触发权重插件
           "example": "",
           "Group": "Daily",
           "version": "1.0",
           "Keep_On": False,
           "Type": "Admin_Plugin",
           }
)

WhereIsMom = on_regex(r"^#?对话开发者", priority=Priority.普通优先级, block=True)


@WhereIsMom.handle()
async def _(bot: Bot, event: MessageEvent):
    await WhereIsMom.send("请告诉妃爱你要说的话哦。")


@WhereIsMom.receive("")
async def _(bot: Bot, event: MessageEvent = Received("")):
    forwardMessage = Nodes(msgID=event.message_id)  # 要转发的消息
    superusers = get_driver().config.superusers
    if isinstance(event, GroupMessageEvent):
        Info = await GetQQGrouperName(bot=bot, QQ=event.user_id, Group=event.group_id)
        group_name = await GetGroupName(bot=bot, Group=event.group_id)
        message = f"来自群{group_name}({event.group_id})\n" \
                  f"用户{Info}({event.user_id})的消息："
    else:
        Info = await GetQQStrangerName(bot=bot, QQ=event.user_id)
        message = f"来自用户{Info}({event.user_id})的消息："
        message = MessageSegment.text(message) + event.message
    for superuser in superusers:
        await bot.send_private_msg(user_id=int(superuser), message=message)
        await forwardMessage.send_private_forward_msg(bot=bot, QQ=int(superuser))
    await WhereIsMom.send("已将消息转述给开发者~")
