from typing import List, Optional, TypedDict

from nonebot import get_driver
from pydantic import BaseModel

from .const import ServerType


class ShortcutType(BaseModel):
    regex: str
    host: str
    type: ServerType
    whitelist: Optional[List[int]] = []


class ConfigClass(BaseModel):
    mcstat_shortcuts: Optional[List[ShortcutType]] = []


config = ConfigClass.parse_obj(get_driver().config)
