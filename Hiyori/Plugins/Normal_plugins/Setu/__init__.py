"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/8/3-18:02
@Desc: 
@Ver : 1.0.0
"""
import re
from nonebot.plugin import on_regex
from Hiyori.Utils.Priority import Priority
from nonebot.plugin import PluginMetadata
from nonebot.matcher import Matcher
from Hiyori.Utils.Spider.Http import AsyncHttpx
from nonebot.adapters.onebot.v11 import (
    GROUP,
    GroupMessageEvent,
    MessageSegment,
)


__setu_version__ = "0.1.0"
__setu_usages__ = f"""
[涩图] 获取一张随机涩图
[mika涩图] 获取一张mika的涩图
""".strip()

__plugin_meta__ = PluginMetadata(
    name="涩图",
    description="谁不喜欢涩图呢~",
    usage=__setu_usages__,
    type="application",
    extra={
        "version": __setu_version__,
        "CD_Weight": 1,
        "example": "涩图",
        "permission": "普通权限",
        "Keep_On": False,
        "Type": "Normal_plugin",
    },
)


setu = on_regex(r"^(.*?)涩图$", permission=GROUP, priority=Priority.普通优先级)

url = "https://api.lolicon.app/setu/v2"

@setu.handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    user_tag = re.search(r"^(.*?)涩图$", str(event.message)).group(1)
    params = {
        "r18": 0,  # 添加r18参数 0为否，1为是，2为混合
        "tag": user_tag,  # 若指定tag
        "num": 1,  # 一次返回的结果数量
        "size": ["original"],
    }
    try:
        res = await AsyncHttpx.get(url=url, timeout=10000, params=params)
        if res.status_code == 200:
            data = res.json()
            if not data["error"]:
                data = data["data"][0]
                pid = data["pid"]
                uid = data["uid"]
                title = data["title"]
                imgurl = data["urls"]["original"]
                message = f'''
                pid : {pid} \nuid : {uid} \ntitle: {title}
                '''.strip()
                message = message + MessageSegment.image(imgurl)
                if not imgurl:
                    await setu.send("没找到符合条件的色图...")
                await setu.send(message, at_sender=True)
            else:
                await setu.send("没找到符合条件的色图...")
    except:
        await setu.send("没找到符合条件的色图...")
