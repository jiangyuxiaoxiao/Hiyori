"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/31-17:34
@Desc: API, 获取Bot配置
@Ver : 1.0.0
"""
from fastapi.responses import JSONResponse
from nonebot import get_asgi, get_driver

app = get_asgi()


@app.get("/Plugins/Web_plugins/Web_API/Config", response_class=JSONResponse)
async def _():
    return get_driver().config.dict()
