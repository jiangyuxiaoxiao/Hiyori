"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/8/1-21:15
@Desc: 
@Ver : 1.0.0
"""

from nonebot.plugin import on_regex
from Hiyori.Utils.Priority import Priority
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import  MessageSegment
import random
import pathlib
import os

__search_version__ = "0.1.0"
__search_usages__ = f"""
[妃爱] 召唤妃爱酱~
""".strip()

__plugin_meta__ = PluginMetadata(
    name="召唤妃爱",
    description="召唤妃爱酱~",
    usage=__search_usages__,
    type="application",
    extra={
        "version": __search_version__,
        "CD_Weight": 1,
        "example": "妃爱",
        "permission": "普通权限",
        "Keep_On": False,
        "Type": "Zao_plugin",
    },
)


reply = on_regex(r"^#?妃爱$", block=True, priority=Priority.普通优先级)


@reply.handle()
async def _():
    message = "我在~"
    image = f"./Data/Reply/images/{random.randint(1,106)}.jpg"
    ImagePath = os.path.abspath(image)
    ImagePath = pathlib.Path(ImagePath).as_uri()
    msg = message + MessageSegment.image(ImagePath)
    await reply.send(msg)