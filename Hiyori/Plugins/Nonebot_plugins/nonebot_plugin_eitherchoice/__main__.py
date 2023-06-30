from typing import Tuple

from nonebot import logger, on_command
from nonebot.internal.adapter import Message
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.typing import T_State
from Hiyori.Plugins.Basic_plugins.nonebot_plugin_saa import Image, MessageFactory
from Hiyori.Utils.Priority import Priority

from .data_source import get_choice_pic


async def check_rule(state: T_State, arg: Message = CommandArg()) -> bool:
    arg_str = arg.extract_plain_text()

    if arg_str.count("和") != 1:
        return False

    ta, tb = arg_str.split("和")
    ta = ta.strip()
    tb = tb.strip()
    if not (ta and tb):
        return False

    state["things"] = ta, tb
    return True


cmd_choice = on_command(
    "对比",
    rule=check_rule,
    aliases={"比较", "比较一下", "锐评", "锐评一下", "如何评价"},
    priority=Priority.普通优先级
)


@cmd_choice.handle()
async def _(matcher: Matcher, state: T_State):
    things: Tuple[str, str] = state["things"]

    await matcher.send("请稍等，AI 正在帮你评价...")
    try:
        pic = await get_choice_pic(*things)
    except Exception:
        logger.exception("发生错误")
        await matcher.finish("发生错误，请检查后台日志")

    await MessageFactory(Image(pic)).finish()
