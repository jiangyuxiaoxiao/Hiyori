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
[盖章] 获得一枚章
[收集册] 查看获得的所有章
""".strip()

__plugin_meta__ = PluginMetadata(
    name="盖章",
    description="星乃今天要盖章吗？",
    usage=__gaizhang_usages__,
    type="application",
    extra={
        "version": __gaizhang_version__,
        "CD_Weight": 1,
        "example": "盖章",
        "permission": "盖章/收集册 普通权限",
        "Keep_On": False,
        "Type": "Zao_plugin",
    },
)

gaizhang = on_command("#######", block=True, priority=Priority.普通优先级)




