from nonebot.plugin import PluginMetadata

from . import adapters as adapters
from .types import Text, Image, Reply, Custom, Mention
from .utils import (
    TargetQQGroup,
    MessageFactory,
    PlatformTarget,
    TargetQQPrivate,
    TargetOB12Unknow,
    SupportedAdapters,
    TargetQQGuildDirect,
    TargetTelegramForum,
    TargetQQGuildChannel,
    TargetTelegramCommon,
    MessageSegmentFactory,
    TargetKaiheilaChannel,
    TargetKaiheilaPrivate,
    AggregatedMessageFactory,
    get_target,
    extract_target,
    enable_auto_select_bot,
)

__all__ = [
    "Text",
    "Image",
    "Mention",
    "Reply",
    "Custom",
    "MessageFactory",
    "MessageSegmentFactory",
    "AggregatedMessageFactory",
    "SupportedAdapters",
    "extract_target",
    "get_target",
    "enable_auto_select_bot",
    "PlatformTarget",
    "TargetOB12Unknow",
    "TargetQQGroup",
    "TargetQQPrivate",
    "TargetQQGuildDirect",
    "TargetQQGuildChannel",
    "TargetKaiheilaChannel",
    "TargetKaiheilaPrivate",
    "TargetTelegramCommon",
    "TargetTelegramForum",
]

