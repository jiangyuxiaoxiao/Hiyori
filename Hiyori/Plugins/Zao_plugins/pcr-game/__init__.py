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

__game_version__ = "0.1.0"
__game_usages__ = f"""
[猜角色] 检测厨力的时候到了！
[猜头像] 检测深度的时候到了！
""".strip()

__plugin_meta__ = PluginMetadata(
    name="猜角色，猜头像",
    description="星乃今天要猜猜乐吗？",
    usage=__game_usages__,
    type="application",
    extra={
        "version": __game_version__,
        "CD_Weight": 0,
        "example": "猜头像",
        "permission": "猜头像/猜角色 普通权限",
        "Keep_On": False,
        "Type": "Zao_plugin",
    },
)

cai = on_command("########", block=True, priority=Priority.普通优先级)



