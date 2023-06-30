"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:37
@Desc: 更新公告插件
@Ver : 1.0.0
"""
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent
from nonebot import on_regex
from nonebot.plugin import PluginMetadata
from Hiyori.Plugins.Basic_plugins.nonebot_plugin_htmlrender import md_to_pic
from Hiyori.Utils.Priority import Priority
import os

__plugin_meta__ = PluginMetadata(
    name="更新公告",  # 用于在菜单显示 用于插件开关
    description="查看妃爱的更新新闻",  # 用于在菜单中描述
    usage="#查看更新 或 #更新\n",
    extra={"CD_Weight": 1,  # 调用插件CD权重 不填的话不会触发权重插件
           "Group": "Daily",
           "version": "1.0",
           "Keep_On": False,
           "Type": "Normal_Plugin",
           }
)

checkUpdate = on_regex("^#(查看)?更新$", priority=Priority.普通优先级, block=False)


@checkUpdate.handle()
async def _(event: MessageEvent):
    # 文件夹路径
    folder_path = os.path.dirname(os.path.abspath(__file__))
    # md文件路径
    md_path = os.path.join(folder_path, "update.md")
    img = await md_to_pic(md_path=md_path, width=1200)
    msg = MessageSegment.image(img)
    await checkUpdate.send(msg)
