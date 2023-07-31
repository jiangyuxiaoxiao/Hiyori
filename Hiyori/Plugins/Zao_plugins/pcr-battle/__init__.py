"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/7/31-17:34
@Desc:
@Ver : 1.0.0
"""

from nonebot.plugin import on_command
from nonebot.plugin import PluginMetadata
from Hiyori.Utils.Priority import Priority


__gaizhang_version__ = "0.1.0"
__gaizhang_usages__ = f"""
详细帮助见会战群公告
""".strip()

__plugin_meta__ = PluginMetadata(
    name="pcr公会战",
    description="你只需要出刀",
    usage=__gaizhang_usages__,
    type="application",
    extra={
        "version": __gaizhang_version__,
        "CD_Weight": 0,
        "example": "催刀",
        "permission": "普通权限",
        "Keep_On": False,
        "Type": "Zao_plugin",
    },
)


pcrjjc = on_command("#####￥#￥#￥#￥#", block=True, priority=Priority.普通优先级)
