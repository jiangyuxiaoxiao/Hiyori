# import datetime
import json

import nonebot
# import requests
# import asyncio
import aiohttp
# import time
# from io import BytesIO
from nonebot import on_keyword, on_command, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.typing import T_State
# from nonebot_plugin_imageutils import Text2Image
from Hiyori.Plugins.Basic_plugins.nonebot_plugin_htmlrender import (
    text_to_pic,
    md_to_pic,
    template_to_pic,
    get_new_page,
)
from Hiyori.Utils.Priority import Priority
from nonebot.plugin import PluginMetadata

help_text = f"""
命令如下(【】中的才是命令哦，记得加命令前缀)：
【配色方案】【配色】获取一种随机配色。例如：/配色
""".strip()

__plugin_meta__ = PluginMetadata(
    name='配色方案',
    description='随机获取一种配色方案',
    usage="#配色方案\n#配色",
    extra={"CD_Weight": 1,  # 调用插件CD权重 不填的话不会触发权重插件
           "example": "",
           "Group": "Daily",
           "version": "1.0",
           "Keep_On": False,
           "Type": "Normal_Plugin",
           }
)

catch_str = on_regex(r"(^#配色方案$)|(^#配色$)", priority=Priority.普通优先级, block=True)


@catch_str.handle()
async def _(bot: Bot, event: Event, state: T_State):
    json_data = await get_colormind()

    color_codes = []
    msg = ""

    try:
        msg += "推荐的配色方案为："
        for color in json_data["result"]:
            r, g, b = color
            color_code = "#{:02X}{:02X}{:02X}".format(r, g, b)
            color_codes.append(color_code)
            msg += color_code + " "
    except:
        msg = '\n调用接口失败，寄！'
        await catch_str.finish(Message(f'{msg}'), at_sender=True)
        return

    img_str = ""
    for color_code in color_codes:
        img_str += '<font color="' + color_code + '" size=7>█</font>'

    output = await md_to_pic(md=img_str, width=230)

    await catch_str.finish(Message(MessageSegment.text(msg) + MessageSegment.image(output)), at_sender=True)


async def get_colormind():
    header1 = {
        'content-type': 'text/plain; charset=utf-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Core/1.94.186.400 QQBrowser/11.3.5195.400'
    }
    API_URL = 'http://colormind.io/api/'
    async with aiohttp.ClientSession() as session:
        async with session.get(
                url=API_URL,
                headers=header1,
                json={"model": "default"}
        ) as response:
            result = await response.read()
            # nonebot.logger.info(result)
            ret = json.loads(result)
    # nonebot.logger.info(ret)
    return ret
