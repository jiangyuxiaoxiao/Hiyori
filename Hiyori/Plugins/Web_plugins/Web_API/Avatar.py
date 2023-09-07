"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/11-16:20
@Desc: 
@Ver : 1.0.0
"""
from fastapi.responses import JSONResponse
import asyncio
import aiohttp
import random

from nonebot import get_asgi

from Hiyori.Utils.File import DirExist

app = get_asgi()

DirExist("Data/Avatar/QQGroup")
DirExist("Data/Avatar/QQUser")


@app.get("/Plugins/Web_plugins/Web_API/Avatar", response_class=JSONResponse)
async def _(QQ: int = 0, Group: int = 0, Size: int = 640):
    if Group == 0 and QQ != 0:

        pass
    elif QQ == 0 and Group != 0:
        pass
    else:
        pass
