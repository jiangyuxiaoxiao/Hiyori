import re
from nonebot import on_regex, logger
from nonebot.adapters import Event
from .analysis_bilibili import config, b23_extract, bili_keyword
from nonebot.plugin import PluginMetadata
from Hiyori.Utils.Priority import Priority

__plugin_meta__ = PluginMetadata(
    name="bilibili解析",
    description="自动解析bilibili视频、番剧",
    usage="发送B站链接或者B站小程序时自动触发",
    extra={
        "CD_Weight": 1,
        "example": "",
        "Keep_On": False,
        "Type": "Auto_Plugin",
    },
)

analysis_bili = on_regex(
    r"(b23.tv)|(bili(22|23|33|2233).cn)|(.bilibili.com)|(^(av|cv)(\d+))|(^BV([a-zA-Z0-9]{10})+)|"
    r"(\[\[QQ小程序\]哔哩哔哩\])|(QQ小程序&amp;#93;哔哩哔哩)|(QQ小程序&#93;哔哩哔哩)",
    flags=re.I,
    priority=Priority.普通优先级
)

blacklist = getattr(config, "analysis_blacklist", [])
group_blacklist = getattr(config, "analysis_group_blacklist", [])


@analysis_bili.handle()
async def analysis_main(event: Event) -> None:
    text = str(event.message).strip()
    if blacklist and int(event.get_user_id()) in blacklist:
        return
    if re.search(r"(b23.tv)|(bili(22|23|33|2233).cn)", text, re.I):
        # 提前处理短链接，避免解析到其他的
        text = await b23_extract(text)
    if hasattr(event, "group_id"):
        group_id = event.group_id
    elif hasattr(event, "channel_id"):
        group_id = event.channel_id
    else:
        group_id = None
    if group_id in group_blacklist:
        return
    msg = await bili_keyword(group_id, text)
    if msg:
        try:
            await analysis_bili.send(msg)
        except Exception as e:
            logger.exception(e)
            logger.warning(f"{msg}\n此次解析可能被风控，尝试去除简介后发送！")
            msg = re.sub(r"简介.*", "", msg)
            await analysis_bili.send(msg)
