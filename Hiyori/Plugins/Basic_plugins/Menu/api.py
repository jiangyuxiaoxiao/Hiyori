"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/3-15:59
@Desc: Menu API调用，获取插件信息，以及插件当前状态
@Ver : 1.0.0
"""
from nonebot import get_asgi
from fastapi.responses import JSONResponse
from nonebot.plugin import _plugins

app = get_asgi()


@app.get("/Menu/Plugins/data", response_class=JSONResponse)
async def _():
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
            if hasattr(data, "description"):
                result["description"] = data.description
                result["descriptions"] = [des for des in data.description.split("\n") if des.strip() != ""]
            if hasattr(data, "usage"):
                result["usage"] = data.usage
                # 去除空格
                result["usages"] = [use for use in data.usage.split("\n") if use.strip() != ""]
            if len(result):
                results.append(result)
    return results



