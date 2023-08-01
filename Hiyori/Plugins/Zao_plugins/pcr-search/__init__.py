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

__search_version__ = "0.1.0"
__search_usages__ = f"""
[@bot简介ue] 角色简介
[@bot技能ue] 角色技能
[@bot专武ue] 角色专武
[@bot羁绊ue] 角色羁绊
""".strip()

__plugin_meta__ = PluginMetadata(
    name="pcr查询",
    description="pcr查询角色信息",
    usage=__search_usages__,
    type="application",
    extra={
        "version": __search_version__,
        "CD_Weight": 1,
        "example": "角色简介",
        "permission": "角色简介/角色技能/角色专武/角色羁绊 普通权限",
        "Keep_On": False,
        "Type": "Zao_plugin",
    },
)


search = on_command("#####", block=True, priority=Priority.普通优先级)




