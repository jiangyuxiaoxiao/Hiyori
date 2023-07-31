from pathlib import Path
from typing import List, Set, Union

from pydantic import BaseModel, Extra, validator


class Config(BaseModel, extra=Extra.ignore):
    today_waifu_ban_id_list: Set[int] = set()
    today_waifu_default_change_waifu: bool = True
    today_waifu_default_limit_times: int = 2
    today_waifu_aliases: List[str] = ['每日老婆', ]
    today_waifu_record_dir: Path = Path(__file__).parent / 'record'
    today_waifu_superuser_opt: bool = False

    @validator('today_waifu_record_dir', pre=True)
    def check_path(cls, v) -> Path:
        return Path(v) if v else Path(__file__).parent / 'record'

    @validator('today_waifu_ban_id_list', pre=True)
    def check_ban_id(cls, v: List[int]) -> Set[int]:
        if not (isinstance(v, list) or isinstance(v, set)):
            return set()
        return set(map(int, v))

    @validator('today_waifu_aliases', pre=True)
    def check_aliases(cls, v: List[str]) -> List[str]:
        if not isinstance(v, list):
            return ['每日老婆', ]
        return list(set(map(str, v + ['每日老婆', ])))
