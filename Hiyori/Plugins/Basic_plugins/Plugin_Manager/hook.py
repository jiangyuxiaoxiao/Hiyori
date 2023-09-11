"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:35
@Desc: 
@Ver : 1.0.0
"""

from nonebot.message import run_preprocessor
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Event
from nonebot.exception import IgnoredException
from nonebot import get_driver

from .pluginManager import pluginsManager

driver = get_driver()


# 插件开关审核
@run_preprocessor
async def check_group_plugin_status(matcher: Matcher, event: Event):
    PluginInfo = matcher.plugin.metadata
    # 没有则不做检查
    if not hasattr(PluginInfo, "name"):
        return
    PluginName = PluginInfo.name
    # 检查是否常驻开启
    if hasattr(PluginInfo, "extra"):
        extraInfo = PluginInfo.extra
        if "Keep_On" in extraInfo.keys():
            # 常开插件
            if extraInfo["Keep_On"]:
                return
    # 检查群组状态
    if hasattr(event, "group_id"):
        GroupID = str(event.group_id)
        if not pluginsManager.GroupPluginIsOn(GroupID, PluginName):
            raise IgnoredException("群插件已关闭")
    # 检查个人状态
    if hasattr(event, "user_id"):
        QQ = str(event.user_id)
        if not pluginsManager.UserPluginIsOn(QQ, PluginName):
            raise IgnoredException("个人插件已关闭")
