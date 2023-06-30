from typing import Optional

from nonebot import get_driver
from pydantic import BaseModel


class ConfigModel(BaseModel):
    proxy: Optional[str] = None
    either_choice_timeout: int = 90
    either_choice_lang: str = "zh-CN"
    either_choice_allow_public: bool = True
    either_choice_pic_width: int = 1280
    either_choice_main_font: str = (
        "'Microsoft YaHei UI', 'Microsoft YaHei', "
        "'Source Han Sans CN', 'Source Han Sans SC', "
        "'PingFang SC', 'Hiragino Sans GB', 'WenQuanYi Micro Hei', sans-serif"
    )
    either_choice_code_font: str = (
        "'Victor Mono', 'VictorMono Nerd Font', "
        "'JetBrains Mono', 'JetBrainsMono Nerd Font', "
        "'Fira Code', 'FiraCode Nerd Font', "
        "'Cascadia Code', 'CascadiaCode Nerd Font', "
        "'Consolas', 'Courier New', monospace"
    )


config: ConfigModel = ConfigModel.parse_obj(get_driver().config.dict())
