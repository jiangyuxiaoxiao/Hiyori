from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_imageutils")

from .__main__ import *  # noqa

__plugin_meta__ = PluginMetadata(
    name="MC服务器查询",
    description="查询MC服务器状态",
    usage="#mc 查询穹妹服务器\n"
          "#motd ip 查询Java服务器\n"
          "#motdpe ip 查询基岩服务器\n ",
    extra={
        "CD_Weight": 1,
        "permission": "普通权限",
        "Keep_On": False,
        "Type": "Normal_Plugin",
    },
)

__version__ = "0.2.6.post1"
