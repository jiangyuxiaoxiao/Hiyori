from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent, MessageSegment
from nonebot import on_notice
from Hiyori.Utils.Priority import Priority

from .rule import isGroupIncreaseNoticeEvent

__plugin_meta__ = PluginMetadata(
    name="新成员欢迎",  # 用于在菜单显示 用于插件开关
    description="有新成员进群时自动触发，不会在静默状态的群聊调用",  # 用于在菜单中描述
    usage="新成员入群自动触发",
    extra={"CD_Weight": 0,  # 调用插件CD权重 不填的话不会触发权重插件
           "example": "",
           "Group": "Feature",
           "version": "1.0",
           "Keep_On": False,
           "Type": "Auto_Plugin",
           }
)

welcome = on_notice(priority=Priority.高优先级, rule=isGroupIncreaseNoticeEvent, block=False)


@welcome.handle()
async def _(event: GroupIncreaseNoticeEvent):
    QQ = event.user_id
    message = MessageSegment.text("好耶！超可爱的") + MessageSegment.at(QQ) + MessageSegment.text("入群了哦！欢迎~")
    await welcome.send(message)
    message = "请输入 #帮助 来查看妃爱的具体功能，"
    await welcome.send(message)
