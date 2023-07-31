"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/7/31-21:53
@Desc: 
@Ver : 1.0.0
"""
from nonebot.plugin import on_command
from nonebot.plugin import PluginMetadata
from Hiyori.Utils.Priority import Priority

__novelai_version__ = "0.1.0"
__novelai_usages__ = f"""
[二次元的我] 康康你的二次元形象
""".strip()

__plugin_meta__ = PluginMetadata(
    name="二次元的我",
    description="康康你的二次元形象",
    usage=__novelai_usages__,
    type="application",
    extra={
        "version": __novelai_version__,
        "CD_Weight": 0,
        "example": "角色简介",
        "permission": "普通权限",
        "Keep_On": False,
        "Type": "Zao_plugin",
    },
)


search = on_command("二次元的我", block=True, priority=Priority.普通优先级)