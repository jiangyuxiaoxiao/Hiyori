"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/3-16:27
@Desc: 检查插件状态
@Ver : 1.0.0
"""
from nonebot import get_asgi
from fastapi.responses import JSONResponse
from nonebot.plugin import _plugins
from .pluginManager import pluginsManager

app = get_asgi()


@app.get("/Plugins/Basic_plugins/Plugin_Manager/Plugin_info", response_class=JSONResponse)
async def _(QQ: int, Group: int):
    results = []
    plugins = list(_plugins.values())
    for plugin in plugins:
        result = {}
        if hasattr(plugin, "metadata"):
            data = plugin.metadata
            if hasattr(data, "extra"):
                result["extra"] = data.extra
            if hasattr(data, "name"):
                result["name"] = data.name
                # 添加插件状态
                if Group != 0:
                    result["group_status"] = pluginsManager.GroupPluginIsOn(GroupID=str(Group), PluginName=data.name)
                result["person_status"] = pluginsManager.UserPluginIsOn(QQ=str(QQ), PluginName=data.name)
            if hasattr(data, "description"):
                result["description"] = data.description
            if hasattr(data, "usage"):
                result["usage"] = data.usage
            # 仅当插件有名时进行返回
            if hasattr(data, "name"):
                results.append(result)
    return results
