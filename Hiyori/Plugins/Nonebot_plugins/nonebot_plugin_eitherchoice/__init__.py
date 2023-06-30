from nonebot import require
from nonebot.plugin import PluginMetadata


from . import __main__ as __main__  # noqa: E402
from .config import ConfigModel  # noqa: E402

__version__ = "0.1.0"
__plugin_meta__ = PluginMetadata(
    name="AI比对",
    description="让 AI 帮你对比两件事物",
    usage=(
        "指令：#对比 要顶的事物 和 要踩的事物\n"
        "别名：#比较、#比较一下、#锐评、#锐评一下、#如何评价\n"
        "\n"
        "例：\n"
        "对比 Python 和 JavaScript\n"
        "比较一下 C# 和 Java"
    ),
    config=ConfigModel,
    extra={"CD_Weight": 5,  # 调用插件CD权重 不填的话不会触发权重插件
           "Group": "Daily",
           "version": "1.0",
           "Keep_On": False,
           "Type": "Normal_Plugin",
           }
)
