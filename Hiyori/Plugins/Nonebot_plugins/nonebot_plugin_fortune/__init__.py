from nonebot import on_command, on_regex, on_fullmatch
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from nonebot.params import Depends, CommandArg, RegexMatched
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot import require
from nonebot.adapters.onebot.v11 import GROUP, GROUP_ADMIN, GROUP_OWNER, Message, GroupMessageEvent, MessageSegment
from .data_source import fortune_manager
from .config import FortuneThemesDict
from Hiyori.Utils.Priority import Priority

require("nonebot_plugin_apscheduler")
from Hiyori.Plugins.Basic_plugins.nonebot_plugin_apscheduler import scheduler

__fortune_version__ = "v0.4.9"
__fortune_usage__ = f'''
[今日运势/抽签/运势] 一般抽签
[xx抽签]     指定主题抽签
[指定xx签] 指定特殊角色签底，需要自己尝试哦~
[设置xx签] 设置群抽签主题
[重置主题] 重置群抽签主题
[主题列表] 查看可选的抽签主题
[查看主题] 查看群抽签主题'''.strip()

__plugin_meta__ = PluginMetadata(
    name="今日运势",
    description="抽签！占卜你的今日运势~",
    usage=__fortune_usage__,
    extra={
        "CD_Weight": 0,
        "example": "运势",
        "permission": "个人抽签：普通权限\n"
                      "主题设置/重置：群管权限",
        "version": __fortune_version__,
        "Keep_On": False,
        "Type": "Normal_Plugin",
    }
)

divine = on_regex(r"(^#?今日运势$)|(^#?运势$)|(^#?抽签$)", permission=GROUP, priority=Priority.普通优先级)
divine_specific = on_regex(r"^[^/]\S+抽签$", permission=GROUP, priority=Priority.普通优先级)
limit_setting = on_regex(r"^指定(.*?)签$", permission=GROUP, priority=Priority.普通优先级)
theme_setting = on_regex(r"^设置(.*?)签$", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority=Priority.普通优先级, block=True)
reset = on_regex("^重置(抽签)?主题$", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority=Priority.普通优先级, block=True)
theme_list = on_fullmatch("主题列表", permission=GROUP, priority=Priority.普通优先级, block=True)
show = on_regex("^查看(抽签)?主题$", permission=GROUP, priority=Priority.普通优先级, block=True)
refresh = on_fullmatch("刷新抽签", permission=SUPERUSER, priority=Priority.普通优先级, block=True)


@show.handle()
async def _(event: GroupMessageEvent):
    gid: str = str(event.group_id)
    theme: str = fortune_manager.get_group_theme(gid)
    await show.finish(f"当前群抽签主题：{FortuneThemesDict[theme][0]}")


@theme_list.handle()
async def _(event: GroupMessageEvent):
    msg: str = fortune_manager.get_main_theme_list()
    await theme_list.finish(msg)


@divine.handle()
async def _(event: GroupMessageEvent):
    gid: str = str(event.group_id)
    uid: str = str(event.user_id)
    nickname: str = event.sender.card if event.sender.card else event.sender.nickname

    is_first, image_file = fortune_manager.divine(gid, uid, nickname, None, None)
    if not image_file:
        await divine.finish("今日运势生成出错……")

    if not is_first:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)

    await divine.finish(msg, at_sender=True)


async def get_user_theme(matcher: Matcher, args: str = RegexMatched()) -> str:
    arg: str = args[:-2]
    if len(arg) < 1:
        await matcher.finish("输入参数错误")

    return arg


@divine_specific.handle()
async def _(event: GroupMessageEvent, user_theme: str = Depends(get_user_theme)):
    for theme in FortuneThemesDict:
        if user_theme in FortuneThemesDict[theme]:
            if not fortune_manager.theme_enable_check(theme):
                await divine_specific.finish("该抽签主题未启用~")
            else:
                gid: str = str(event.group_id)
                uid: str = str(event.user_id)
                nickname: str = event.sender.card if event.sender.card else event.sender.nickname

                is_first, image_file = fortune_manager.divine(gid, uid, nickname, theme, None)
                if not image_file:
                    await divine_specific.finish("今日运势生成出错……")

                if not is_first:
                    msg = MessageSegment.text("你今天抽过签了，再给你看一次哦\n") + MessageSegment.image(image_file)
                else:
                    logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
                    msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)

            await divine_specific.finish(msg, at_sender=True)

    await divine_specific.finish("还没有这种抽签主题哦~")


async def get_user_arg(matcher: Matcher, args: str = RegexMatched()) -> str:
    arg: str = args[2:-1]
    if len(arg) < 1:
        await matcher.finish("输入参数错误")

    return arg


@theme_setting.handle()
async def _(event: GroupMessageEvent, user_theme: str = Depends(get_user_arg)):
    gid: str = str(event.group_id)

    for theme in FortuneThemesDict:
        if user_theme in FortuneThemesDict[theme]:
            if not fortune_manager.divination_setting(theme, gid):
                await theme_setting.finish("该抽签主题未启用~")
            else:
                await theme_setting.finish("已设置当前群抽签主题~")

    await theme_setting.finish("还没有这种抽签主题哦~")


@limit_setting.handle()
async def _(event: GroupMessageEvent, limit: str = Depends(get_user_arg)):
    logger.warning("指定签底抽签功能将在 v0.5.x 弃用")

    gid: str = str(event.group_id)
    uid: str = str(event.user_id)
    nickname: str = event.sender.card if event.sender.card else event.sender.nickname

    if limit == "随机":
        is_first, image_file = fortune_manager.divine(gid, uid, nickname, None, None)
        if not image_file:
            await limit_setting.finish("今日运势生成出错……")
    else:
        spec_path = fortune_manager.specific_check(limit)
        if not spec_path:
            await limit_setting.finish("还不可以指定这种签哦，请确认该签底对应主题开启或图片路径存在~")
        else:
            is_first, image_file = fortune_manager.divine(gid, uid, nickname, None, spec_path)
            if not image_file:
                await limit_setting.finish("今日运势生成出错……")

    if not is_first:
        msg = MessageSegment.text("你今天抽过签了，再给你看一次哦\n") + MessageSegment.image(image_file)
    else:
        logger.info(f"User {event.user_id} | Group {event.group_id} 占卜了今日运势")
        msg = MessageSegment.text("✨今日运势✨\n") + MessageSegment.image(image_file)

    await limit_setting.finish(msg, at_sender=True)


@reset.handle()
async def _(event: GroupMessageEvent):
    gid: str = str(event.group_id)
    if not fortune_manager.divination_setting("random", gid):
        await reset.finish("重置群抽签主题失败！")

    await reset.finish("已重置当前群抽签主题为随机~")


@refresh.handle()
async def _():
    fortune_manager.reset_fortune()
    await refresh.finish("今日运势已刷新!")


# 重置每日占卜
@scheduler.scheduled_job("cron", hour=0, minute=0, misfire_grace_time=60)
async def _():
    fortune_manager.reset_fortune()
    logger.info("今日运势已刷新！")
