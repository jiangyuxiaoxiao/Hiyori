"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:34
@Desc: 帮助菜单插件
@Ver : 1.0.0
"""
from nonebot.plugin import _plugins
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from .api import *
from Hiyori.Utils.Priority import Priority

from Hiyori.Plugins.Basic_plugins import nonebot_plugin_htmlrender as htmlRender
from Hiyori.Plugins.Basic_plugins import Plugin_Manager

get_Menu = on_regex(r"(^#?帮助$)|(^#?菜单$)", priority=Priority.系统优先级, block=True)

Menu_HTML_Path = "./Data/Menu/Template/menu_百岁珊.html"
Menu_PNG_Path = "./Data/Menu/Template/menu_百岁珊.png"
Has_Generate_Menu = False


@get_Menu.handle()
async def _(event: MessageEvent):
    # 由于菜单会显示群组插件状态的原因，现在每次调用都会动态生成菜单。
    global Menu_HTML_Path, Menu_PNG_Path, Has_Generate_Menu
    Group_event = False
    GroupID = 0
    if hasattr(event, "group_id"):
        Group_event = True
        GroupID = event.group_id
    with open(Menu_HTML_Path, "r", encoding="utf-8") as file:
        htmlStr = file.read()
    templateStrs = ["", "", ""]  # 插件类型分别为 Normal_Plugin, Admin_Plugin, Auto_Plugin
    plugins = list(_plugins.values())
    for plugin in plugins:
        if hasattr(plugin, "metadata"):
            if plugin.metadata:
                metadata = plugin.metadata
                # 检查插件类型
                Type = 0
                if hasattr(metadata, "extra"):
                    extra = metadata.extra
                    if "Type" in extra.keys():
                        match extra["Type"]:
                            case "Normal_Plugin":
                                Type = 0
                            case "Admin_Plugin":
                                Type = 1
                            case "Auto_Plugin":
                                Type = 2
                            case "Anonymous_Plugin":
                                continue
                # 填充模板
                templateStrs[Type] = templateStrs[Type] + "<tr>"
                # 插件名
                if hasattr(metadata, "name"):
                    # 是群聊事件
                    if Group_event:
                        if not Plugin_Manager.pluginsManager.GroupPluginIsOn(GroupID=str(GroupID),
                                                                             PluginName=metadata.name):
                            templateStrs[Type] = templateStrs[Type] + \
                                                 f"<td style=\"color: rgb(201, 071, 055); text-decoration: " \
                                                 f"line-through\">{metadata.name}</td> "
                        elif not Plugin_Manager.pluginsManager.UserPluginIsOn(QQ=str(event.user_id),
                                                                              PluginName=metadata.name):
                            templateStrs[Type] = templateStrs[Type] + \
                                                 f"<td style=\"color: rgb(0, 0, 0); text-decoration: " \
                                                 f"line-through\">{metadata.name}</td> "
                        else:
                            templateStrs[Type] = templateStrs[Type] + f"<td>{metadata.name}</td>"
                    # 是私聊事件
                    else:
                        if not Plugin_Manager.pluginsManager.UserPluginIsOn(QQ=str(event.user_id),
                                                                            PluginName=metadata.name):
                            templateStrs[Type] = templateStrs[Type] + \
                                                 f"<td style=\"color: rgb(0, 0, 0); text-decoration: " \
                                                 f"line-through\">{metadata.name}</td> "
                        else:
                            templateStrs[Type] = templateStrs[Type] + f"<td>{metadata.name}</td>"
                else:
                    templateStrs[Type] = templateStrs[Type] + "<td></td>"
                # 插件介绍
                if hasattr(metadata, "description"):
                    description = metadata.description.replace("\n", "<br>")
                    templateStrs[Type] = templateStrs[Type] + f"<td>{description}</td>"
                else:
                    templateStrs[Type] = templateStrs[Type] + "<td></td>"
                # 插件用法
                if hasattr(metadata, "usage"):
                    usage = metadata.usage.replace("\n", "<br>")
                    templateStrs[Type] = templateStrs[Type] + f"<td>{usage}</td>"
                else:
                    templateStrs[Type] = templateStrs[Type] + "<td></td>"
                # extra信息
                if hasattr(metadata, "extra"):
                    extra = metadata.extra
                    # 权限要求
                    if "permission" in extra.keys():
                        permission = extra["permission"].replace("\n", "<br>")
                        templateStrs[Type] = templateStrs[Type] + f"<td>{permission}</td>"
                    else:
                        templateStrs[Type] = templateStrs[Type] + "<td>普通权限</td>"
                    # CD权重
                    if "CD_Weight" in extra.keys():
                        CD_Weight = extra["CD_Weight"]
                        templateStrs[Type] = templateStrs[Type] + f"<td>{CD_Weight}</td>"
                    else:
                        templateStrs[Type] = templateStrs[Type] + "<td>0</td>"
                else:
                    templateStrs[Type] = templateStrs[Type] + "<td>普通权限</td><td>0</td>"
                templateStrs[Type] = templateStrs[Type] + "</tr>"
    htmlStr = htmlStr.replace("Normal_Plugin", templateStrs[0])
    htmlStr = htmlStr.replace("Admin_Plugin", templateStrs[1])
    htmlStr = htmlStr.replace("Auto_Plugin", templateStrs[2])
    图片二进制数据 = await htmlRender.html_to_pic(
        html=htmlStr, type="png", viewport={"width": 2160, "height": 10},
    )
    # 菜单图片 = Image.open(io.BytesIO(图片二进制数据))
    # workPath = os.getcwd()
    # 图片路径 = os.path.join(workPath, Menu_PNG_Path)
    # 菜单图片.save(图片路径, format="PNG")
    # 发送图片
    # ImgDirUri = pathlib.Path(图片路径).as_uri()

    message = MessageSegment.at(event.user_id)
    message = message + MessageSegment.image(图片二进制数据)
    await get_Menu.send(message)
