"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/8/1-21:43
@Desc: 
@Ver : 1.0.0
"""
import shutil
import asyncio
from asyncio.subprocess import Process
import os
import requests
import time

from nonebot.plugin import on_regex
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment
from nonebot.typing import T_State
from nonebot.params import Arg, Depends
from nonebot.plugin import PluginMetadata

from Hiyori.Utils.Message.Image import get_message_img, ImageMessage
from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.File import DirExist


__plugin_meta__ = PluginMetadata(
    name="图片超分",  # 用于在菜单显示 用于插件开关
    description="图片超分，提高图片分辨率",  # 用于在菜单中描述
    usage="#清晰术",
    extra={"CD_Weight": 2,  # 调用插件CD权重 不填的话不会触发权重插件
           "Group": "Daily",
           "Keep_On": False,
           "Type": "Normal_Plugin",
           }
)


# 配置 是否移除缓存文件
remove_temp_file = True

qinxi = on_regex(r"^#?清晰术", block=True, priority=Priority.普通优先级)


def parse_image(key: str):
    async def _key_parser(
            state: T_State, img: Message = Arg(key)
    ):
        if not get_message_img(img):
            await qinxi.reject_arg(key, "请发送要识别的图片！")
        state[key] = img

    return _key_parser


@qinxi.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    """
    msg = arg.extract_plain_text().strip()
    if msg:
        state["mod"] = msg
    else:
        state["mod"] = "saucenao"
    """
    if get_message_img(event.json()):
        state["img"] = event.message


@qinxi.got("img", prompt="图来！", parameterless=[Depends(parse_image("img"))])
async def _(img: Message = Arg("img")):
    img = get_message_img(img)[0]
    await qinxi.send("妃爱修复中~")
    url = str(img)
    res = requests.get(url)
    # 下载图片
    Time = str(time.time())
    # 检查文件夹是否存在，不存在则创建
    DirExist("./Data/Clarifications/image")
    fromImage = f"./Data/Clarifications/image/{Time}.jpg"  # 超分原图
    toImage = f"./Data/Clarifications/image/{Time}.png"  # 超分后保存路径
    with open(fromImage, mode="wb") as f:
        f.write(res.content)
    # 异步执行超分程序调用指令
    exePath = os.path.abspath("./Data/Clarifications/realcugan-ncnn-vulkan/realcugan-ncnn-vulkan.exe")
    process: Process = await asyncio.create_subprocess_exec(exePath, "-i", fromImage, "-o", toImage)
    await process.wait()
    msg = ImageMessage(toImage)  # 工具函数，将Path转MessageSegment
    await qinxi.send(msg, at_sender=True)
    # 打扫现场
    global remove_temp_file
    if remove_temp_file:
        shutil.rmtree("./Data/Clarifications/image")  # 递归删除所有文件
