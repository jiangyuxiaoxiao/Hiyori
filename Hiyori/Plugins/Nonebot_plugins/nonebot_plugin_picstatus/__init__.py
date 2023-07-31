from nonebot.plugin import PluginMetadata

from .__main__ import *
from .config import config
from .statistics import *
from .version import __version__

usage = "#状态 #运行状态"
if config.ps_need_at:
    usage += "\n注意：使用指令时需要@机器人"
if config.ps_only_su:
    usage += "\n注意：仅SuperUser可以使用此指令"

__plugin_meta__ = PluginMetadata(
    name="服务器状态",
    description="以图片形式显示妃爱的运行状态",
    usage=usage,
    extra={
        "CD_Weight": 5,
        "example": "",
        "permission": "普通权限",
        "Keep_On": False,
        "Type": "Normal_Plugin",
    },
)
