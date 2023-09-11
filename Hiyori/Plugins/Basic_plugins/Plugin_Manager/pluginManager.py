"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:35
@Desc: 
@Ver : 1.0.0
"""
import json
import aiofiles
import os
from nonebot import get_loaded_plugins
from Hiyori.Utils.File import JsonFileExist, DirExist


class pluginsManager:
    GroupPluginInfo: dict[str, dict[str, bool]] = dict()
    UserPluginInfo: dict[str, dict[str, bool]] = dict()
    GroupJsonPath: str = "./Config/Plugin_Manager/groupConfig.json"
    UserJsonPath: str = "./Config/Plugin_Manager/userConfig.json"

    # 初始化
    @staticmethod
    def LoadConfig():
        """初始化，从json文件加载配置"""
        DirExist(os.path.dirname(pluginsManager.GroupJsonPath))
        JsonFileExist(pluginsManager.GroupJsonPath)
        JsonFileExist(pluginsManager.UserJsonPath)
        pluginsManager.GroupPluginInfo.clear()
        pluginsManager.UserPluginInfo.clear()
        # 加载群插件配置
        with open(pluginsManager.GroupJsonPath, encoding="utf-8", mode="r") as file:
            info = file.read()
            pluginsManager.GroupPluginInfo = json.loads(info)
        # 加载用户插件配置
        with open(pluginsManager.UserJsonPath, encoding="utf-8", mode="r") as file:
            info = file.read()
            pluginsManager.UserPluginInfo = json.loads(info)

    # 保存群组配置
    @staticmethod
    async def SaveGroupConfig():
        """保存群组配置"""
        async with aiofiles.open(pluginsManager.GroupJsonPath, encoding="utf-8", mode="w") as file:
            info = json.dumps(pluginsManager.GroupPluginInfo, indent=2, ensure_ascii=False)
            await file.write(info)

    # 保存个人配置
    @staticmethod
    async def SaveUserConfig():
        """保存个人配置"""
        async with aiofiles.open(pluginsManager.UserJsonPath, encoding="utf-8", mode="w") as file:
            info = json.dumps(pluginsManager.UserPluginInfo, indent=2, ensure_ascii=False)
            await file.write(info)

    # 判断群组的对应插件是否开启，若开启返回True，否则返回False
    @staticmethod
    def GroupPluginIsOn(GroupID: str, PluginName: str) -> bool:
        """判断群组的对应插件是否开启，若开启返回True，否则返回False"""
        # 检查插件是否常驻
        if pluginsManager.PluginKeepOn(PluginName):
            return True
        if GroupID in pluginsManager.GroupPluginInfo.keys():
            GroupInfo = pluginsManager.GroupPluginInfo[GroupID]
            # 检查是否开启白名单模式
            if "WhiteList" in GroupInfo.keys():
                # 若开启了白名单模式
                if GroupInfo["WhiteList"]:
                    if PluginName in GroupInfo.keys():
                        return GroupInfo[PluginName]
                    else:
                        return False
                # 未开启白名单模式
            if PluginName in GroupInfo.keys():
                return GroupInfo[PluginName]
        return True

    # 判断用户的对应插件是否开启，若开启返回True，否则返回False
    @staticmethod
    def UserPluginIsOn(QQ: str, PluginName: str) -> bool:
        """判断用户的对应插件是否开启，若开启返回True，否则返回False"""
        # 检查插件是否常驻
        if pluginsManager.PluginKeepOn(PluginName):
            return True
        if QQ in pluginsManager.UserPluginInfo.keys():
            UserInfo = pluginsManager.UserPluginInfo[QQ]
            # 检查是否开启白名单模式
            if "WhiteList" in UserInfo.keys():
                # 若开启了白名单模式
                if UserInfo["WhiteList"]:
                    if PluginName in UserInfo.keys():
                        return UserInfo[PluginName]
                    else:
                        return False
                # 未开启白名单模式
            if PluginName in UserInfo.keys():
                return UserInfo[PluginName]
        return True

    # 更改群组插件状态
    @staticmethod
    async def ChangeGroupPluginStatus(GroupID: str, PluginName: str, status: bool):
        if GroupID not in pluginsManager.GroupPluginInfo:
            pluginsManager.GroupPluginInfo[GroupID] = dict()
        pluginsManager.GroupPluginInfo[GroupID][PluginName] = status
        await pluginsManager.SaveGroupConfig()

    # 改变个人插件状态
    @staticmethod
    async def ChangeUserPluginStatus(QQ: str, PluginName: str, status: bool):
        if QQ not in pluginsManager.UserPluginInfo:
            pluginsManager.UserPluginInfo[QQ] = dict()
        pluginsManager.UserPluginInfo[QQ][PluginName] = status
        await pluginsManager.SaveUserConfig()

    # 获取在黑名单模式下，群组已关闭插件列表
    @staticmethod
    def GetGroupOffPlugins(GroupID: str) -> list[str]:
        """
        获取在黑名单模式下，群组已关闭插件列表

        :param GroupID: 群号
        :return: 已关闭的插件的列表【黑名单模式下】
        """
        result = []
        if GroupID not in pluginsManager.GroupPluginInfo.keys():
            return result
        else:
            groupInfo = pluginsManager.GroupPluginInfo[GroupID]
            if len(groupInfo) != 0:
                for pluginName, status in groupInfo.items():
                    if not status and pluginName != "WhiteList":
                        result.append(pluginName)
            return result

    # 获取在白名单模式下，群组已开启插件列表
    @staticmethod
    def GetGroupOnPlugins(GroupID: str) -> list[str]:
        """
        获取在白名单模式下，群组已开启插件列表

        :param GroupID: 群号
        :return: 已开启的插件的列表【白名单模式下】
        """
        result = []
        if GroupID not in pluginsManager.GroupPluginInfo.keys():
            return result
        else:
            groupInfo = pluginsManager.GroupPluginInfo[GroupID]
            if len(groupInfo) != 0:
                for pluginName, status in groupInfo.items():
                    if status and pluginName != "WhiteList":
                        result.append(pluginName)
            return result

    # 获取在黑名单模式下，个人已关闭插件列表
    @staticmethod
    def GetUserOffPlugins(QQ: str) -> list[str]:
        """
        获取在黑名单模式下，个人已关闭插件列表

        :param QQ: QQ号
        :return: 已关闭的插件的列表【黑名单模式下】
        """
        result = []
        if QQ not in pluginsManager.UserPluginInfo.keys():
            return result
        else:
            userInfo = pluginsManager.UserPluginInfo[QQ]
            for pluginName, status in userInfo.items():
                if not status and pluginName != "WhiteList":
                    result.append(pluginName)
            return result

    # 获取在黑名单模式下，个人已关闭插件列表
    @staticmethod
    def GetUserOnPlugins(QQ: str) -> list[str]:
        """
        获取在黑名单模式下，个人已关闭插件列表

        :param QQ: QQ号
        :return: 已开启的插件的列表【白名单模式下】
        """
        result = []
        if QQ not in pluginsManager.UserPluginInfo.keys():
            return result
        else:
            userInfo = pluginsManager.UserPluginInfo[QQ]
            for pluginName, status in userInfo.items():
                if status and pluginName != "WhiteList":
                    result.append(pluginName)
            return result

    # 检查群组是否是白名单模式
    @staticmethod
    def GroupWhiteListStatus(GroupID: str) -> bool:
        """
        检查群组是否是白名单模式，若是则返回True

        :param GroupID: 群号
        :return: 是否是白名单模式
        """
        # 默认为黑名单模式
        if GroupID not in pluginsManager.GroupPluginInfo.keys():
            return False
        else:
            groupInfo = pluginsManager.GroupPluginInfo[GroupID]
            if "WhiteList" not in groupInfo.keys():
                return False
            else:
                return groupInfo["WhiteList"]

    # 检查用户是否是白名单模式
    @staticmethod
    def UserWhiteListStatus(QQ: str) -> bool:
        """
        检查用户是否是白名单模式，若是则返回True

        :param QQ: QQ号
        :return: 是否是白名单模式
        """
        # 默认为黑名单模式
        if QQ not in pluginsManager.UserPluginInfo.keys():
            return False
        else:
            userInfo = pluginsManager.UserPluginInfo[QQ]
            if "WhiteList" not in userInfo.keys():
                return False
            else:
                return userInfo["WhiteList"]

    # 检查插件是否常驻
    @staticmethod
    def PluginKeepOn(PluginName: str) -> bool:
        """
        检查插件是否常驻

        :param PluginName: 插件名
        :return: 若插件常驻则返回True，否则返回False
        """
        plugins = get_loaded_plugins()
        for plugin in plugins:
            if hasattr(plugin.metadata, "name"):
                if plugin.metadata.name == PluginName:
                    if hasattr(plugin.metadata, "extra"):
                        extraInfo = plugin.metadata.extra
                        if "Keep_On" in extraInfo.keys():
                            return extraInfo["Keep_On"]
                    return False
        return False
