from typing import Awaitable, Callable, NoReturn

from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
from nonebot.internal.adapter import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .config import config
from .draw import ServerType, draw  # noqa

motd_handler = on_command("motd", aliases={"!motd", "！motd"})


@motd_handler.handle()
async def _(matcher: Matcher, msg_arg: Message = CommandArg()):
    arg: str = msg_arg.extract_plain_text()

    svr_type: ServerType = "je"
    be_svr_prefix = ["pe", "be"]
    for p in be_svr_prefix:
        if arg.startswith(p):
            arg = arg.replace(p, "", 1)
            svr_type = "be"
            break

    arg = arg.strip()
    await matcher.finish(await draw(arg, svr_type))


def get_shortcut_handler(
    host: str, svr_type: ServerType
) -> Callable[..., Awaitable[NoReturn]]:
    async def shortcut_handler(matcher: Matcher):
        await matcher.finish(await draw(host, svr_type))

    return shortcut_handler


def startup():
    if s := config.mcstat_shortcuts:
        for shortcut in s:

            async def rule(event: MessageEvent):
                if (wl := shortcut.whitelist) and isinstance(event, GroupMessageEvent):
                    return event.group_id in wl
                return True

            on_regex(shortcut.regex, rule=rule).append_handler(
                get_shortcut_handler(shortcut.host, shortcut.type)
            )


startup()
