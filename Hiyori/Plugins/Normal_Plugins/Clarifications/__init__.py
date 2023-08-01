"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/8/1-21:43
@Desc: 
@Ver : 1.0.0
"""
from nonebot.plugin import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message,MessageSegment
from nonebot.typing import T_State
from Hiyori.Utils.Image import get_message_img
from nonebot.params import CommandArg, Arg, ArgStr, Depends
import os
import requests
import time

qinxi = on_command("清晰术", block=True, priority=5)

def parse_image(key: str):
    async def _key_parser(
        state: T_State, img: Message = Arg(key)
    ):
        if not get_message_img(img):
            await qinxi.reject_arg(key, "请发送要识别的图片！")
        state[key] = img
    return _key_parser


@qinxi.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    if msg:
        state["mod"] = msg
    else:
        state["mod"] = "saucenao"
    if get_message_img(event.json()):
        state["img"] = event.message


@qinxi.got("img", prompt="图来！", parameterless=[Depends(parse_image("img"))])
async def _(
    bot: Bot,
    event: MessageEvent,
    state: T_State,
    mod: str = ArgStr("mod"),
    img: Message = Arg("img"),
):
    img = get_message_img(img)[0]
    await qinxi.send("少女修复中")
    url = str(img)
    res = requests.get(url)
    # 下载图片
    Time = str(time.time())
    fromImage = os.path.abspath(f"./Data/Clarifications/image/{Time}.jpg")
    toImage = os.path.abspath(f"./Data/Clarifications/image/{Time}.png")
    with open(fromImage, mode="wb") as f:
        f.write(res.content)
    procedure = rf'D:\Users\feiai\Downloads\Hiyori\Hiyori\Data\Clarifications\realcugan-ncnn-vulkan\realcugan-ncnn-vulkan.exe -i {fromImage} -o {toImage}'
    os.system(procedure)
    image = MessageSegment.image(toImage)
    await qinxi.send(image,at_sender=True)
    os.remove(fromImage)
    os.remove(toImage)


