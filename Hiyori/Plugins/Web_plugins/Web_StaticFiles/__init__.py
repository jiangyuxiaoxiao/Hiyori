"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/31-17:30
@Desc: 后端，处理静态文件请求
@Ver : 1.0.0
"""
import os
from nonebot import get_asgi
from fastapi.staticfiles import StaticFiles

app = get_asgi()

StaticDir: str = "Data/Web"
# 获取 static 文件夹下的所有子文件夹
dirs = [fir.name for fir in os.scandir(StaticDir) if fir.is_dir()]
files = [fir.name for fir in os.scandir(StaticDir) if fir.is_dir()]
for dirName in dirs:
    app.mount(f"/{dirName}", StaticFiles(directory=f"./{StaticDir}/{dirName}"), name=dirName)
