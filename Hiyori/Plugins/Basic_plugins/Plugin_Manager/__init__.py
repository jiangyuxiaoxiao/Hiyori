"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:34
@Desc: 
@Ver : 1.0.0
"""
import re

from nonebot import on_regex
from nonebot import get_loaded_plugins
from nonebot.plugin import PluginMetadata
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent, MessageSegment
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER

from Hiyori.Plugins.Basic_plugins.nonebot_plugin_htmlrender import md_to_pic

from Hiyori.Utils.Permissions import HIYORI_OWNER, HIYORI_ADMIN
from Hiyori.Utils.Priority import Priority

from .pluginManager import pluginsManager
from .hook import check_group_plugin_status
from .api import *

__plugin_meta__ = PluginMetadata(
    name="插件开关",
    description="开启或者关闭对群聊/个人的插件响应",
    usage="#群组开启插件 插件名\n"
          "#群组关闭插件 插件名\n"
          "#群组插件状态\n"
          "#群组插件白名单模式/群组插件黑名单模式\n"
          "#个人开启插件 插件名\n"
          "#个人关闭插件 插件名\n"
          "#个人插件状态\n"
          "#个人插件白名单模式/个人插件黑名单模式\n",
    extra={
        "CD_Weight": 2,
        "example": "",
        "permission": "个人：普通权限\n"
                      "群聊：群管/妃爱管理员及以上权限\n"
                      "状态查看：普通权限",
        "Keep_On": True,
        "Type": "Admin_Plugin",
    },
)

# 初始化
pluginsManager.LoadConfig()
logger.success("插件开关配置成功加载")

# 群组插件开关
groupPluginSwitch = on_regex(r"(^#群组开启插件)|(^#群组关闭插件)", priority=Priority.系统优先级,
                             permission=HIYORI_OWNER | GROUP_OWNER | GROUP_ADMIN | HIYORI_ADMIN,
                             block=True)
# 个人插件开关
userPluginSwitch = on_regex(r"(^#个人开启插件)|(^#个人关闭插件)", priority=Priority.系统优先级,
                            block=True)
# 群组插件状态查询
groupPluginStatus = on_regex(r"^#群组插件状态$", priority=Priority.系统优先级, block=True)
# 个人插件状态查询
userPluginStatus = on_regex(r"^#个人插件状态$", priority=Priority.系统优先级, block=True)
# 群组开启黑/白名单
groupPluginWhiteList = on_regex(r"(^#群组插件白名单模式$)|(^#群组插件黑名单模式$)", priority=Priority.系统优先级,
                                permission=HIYORI_OWNER | GROUP_OWNER | GROUP_ADMIN | HIYORI_ADMIN,
                                block=True)
# 个人开启黑/白名单
userPluginWhiteList = on_regex(r"(^#个人插件白名单模式$)|(^#个人插件黑名单模式$)", priority=Priority.系统优先级,
                               block=True)


# 群组插件开关
@groupPluginSwitch.handle()
async def _(event: GroupMessageEvent):
    plugins = get_loaded_plugins()
    message = str(event.message)
    GroupID = str(event.group_id)
    if re.match("^#群组开启插件", message):
        Type = True
    else:
        Type = False
    message = re.sub(r"(^#群组开启插件)|(^#群组关闭插件)", "", message).lstrip()
    for plugin in plugins:
        if hasattr(plugin.metadata, "name"):
            if message == plugin.metadata.name:
                if hasattr(plugin.metadata, "extra"):
                    extra = plugin.metadata.extra
                    if "Keep_On" in extra.keys():
                        if extra["Keep_On"]:
                            await userPluginSwitch.send("插件无法关闭")
                            return
                await pluginsManager.ChangeGroupPluginStatus(GroupID, message, Type)
                await groupPluginSwitch.send(f"插件【{message}】群组状态修改成功")
                return
    await groupPluginSwitch.send(f"未找到插件【{message}】")


# 个人插件开关
@userPluginSwitch.handle()
async def _(event: MessageEvent):
    plugins = get_loaded_plugins()
    message = str(event.message)
    QQ = str(event.user_id)
    if re.match("^#个人开启插件", message):
        Type = True
    else:
        Type = False
    message = re.sub(r"(^#个人开启插件)|(^#个人关闭插件)", "", message).lstrip()
    for plugin in plugins:
        if hasattr(plugin.metadata, "name"):
            if message == plugin.metadata.name:
                if hasattr(plugin.metadata, "extra"):
                    extra = plugin.metadata.extra
                    if "Keep_On" in extra.keys():
                        if extra["Keep_On"]:
                            await userPluginSwitch.send("插件无法关闭")
                            return
                await pluginsManager.ChangeUserPluginStatus(QQ, message, Type)
                await userPluginSwitch.send(f"插件【{message}】个人状态修改成功")
                return
    await userPluginSwitch.send(f"未找到插件【{message}】")


# 群组插件状态查询
@groupPluginStatus.handle()
async def _(event: GroupMessageEvent):
    GroupID = str(event.group_id)
    message = "## 群组插件状态"
    # 白名单模式
    if pluginsManager.GroupWhiteListStatus(GroupID):
        message = message + "   `白名单模式`\n"
        plugins = pluginsManager.GetGroupOnPlugins(GroupID)
        if len(plugins) == 0:
            message = message + "**本群暂无开启插件**"
        else:
            message = message + "已开启插件:  \n\n"
            for plugin in plugins:
                message = message + f"+ {plugin}\n"
    else:
        message = message + "   `黑名单模式`\n"
        plugins = pluginsManager.GetGroupOffPlugins(GroupID)
        if len(plugins) == 0:
            message = message + "**本群暂无关闭插件**"
        else:
            message = message + "已关闭插件:  \n\n"
            for plugin in plugins:
                message = message + f"+ {plugin}\n"
    pic = await md_to_pic(md=message)
    await groupPluginStatus.send(MessageSegment.image(pic))


# 个人插件状态查询
@userPluginStatus.handle()
async def _(event: MessageEvent):
    QQ = str(event.user_id)
    message = "## 个人插件状态"
    # 白名单模式
    if pluginsManager.UserWhiteListStatus(QQ):
        message = message + "   `白名单模式`\n"
        plugins = pluginsManager.GetUserOnPlugins(QQ)
        if len(plugins) == 0:
            message = message + "**暂无开启插件**"
        else:
            message = message + "已开启插件:  \n\n"
            for plugin in plugins:
                message = message + f"+ {plugin}\n"
    else:
        message = message + "   `黑名单模式`\n"
        plugins = pluginsManager.GetUserOffPlugins(QQ)
        if len(plugins) == 0:
            message = message + "**暂无关闭插件**"
        else:
            message = message + "已关闭插件:  \n\n"
            for plugin in plugins:
                message = message + f"+ {plugin}\n"
    pic = await md_to_pic(md=message)
    await userPluginStatus.send(MessageSegment.image(pic))


@groupPluginWhiteList.handle()
async def _(event: GroupMessageEvent):
    GroupID = str(event.group_id)
    message = str(event.message)
    if message == "#群组插件白名单模式":
        await pluginsManager.ChangeGroupPluginStatus(GroupID=GroupID, PluginName="WhiteList", status=True)
        await groupPluginWhiteList.send("群组插件响应已修改为白名单模式")
    else:
        await pluginsManager.ChangeGroupPluginStatus(GroupID=GroupID, PluginName="WhiteList", status=False)
        await groupPluginWhiteList.send("群组插件响应已修改为黑名单模式")


@userPluginWhiteList.handle()
async def _(event: MessageEvent):
    QQ = str(event.user_id)
    message = str(event.message)
    if message == "#个人插件白名单模式":
        await pluginsManager.ChangeUserPluginStatus(QQ=QQ, PluginName="WhiteList", status=True)
        await groupPluginWhiteList.send("个人插件响应已修改为白名单模式")
    else:
        await pluginsManager.ChangeUserPluginStatus(QQ=QQ, PluginName="WhiteList", status=False)
        await groupPluginWhiteList.send("个人插件响应已修改为黑名单模式")
