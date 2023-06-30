from typing import Literal

ServerType = Literal["je", "be"]

CODE_COLOR = {
    "0": "#000000",
    "1": "#0000AA",
    "2": "#00AA00",
    "3": "#00AAAA",
    "4": "#AA0000",
    "5": "#AA00AA",
    "6": "#FFAA00",
    "7": "#AAAAAA",
    "8": "#555555",
    "9": "#5555FF",
    "a": "#55FF55",
    "b": "#55FFFF",
    "c": "#FF5555",
    "d": "#FF55FF",
    "e": "#FFFF55",
    "f": "#FFFFFF",
    "g": "#DDD605",
}

STROKE_COLOR = {
    "0": "#000000",
    "1": "#00002A",
    "2": "#002A00",
    "3": "#002A2A",
    "4": "#2A0000",
    "5": "#2A002A",
    "6": "#2A2A00",
    "7": "#2A2A2A",
    "8": "#151515",
    "9": "#15153F",
    "a": "#153F15",
    "b": "#153F3F",
    "c": "#3F1515",
    "d": "#3F153F",
    "e": "#3F3F15",
    "f": "#3F3F3F",
    "g": "#373501",
}

STRING_CODE = {
    "black": "0",
    "dark_blue": "1",
    "dark_green": "2",
    "dark_aqua": "3",
    "dark_red": "4",
    "dark_purple": "5",
    "gold": "6",
    "gray": "7",
    "dark_gray": "8",
    "blue": "9",
    "green": "a",
    "aqua": "b",
    "red": "c",
    "light_purple": "d",
    "yellow": "e",
    "white": "f",
    "bold": "l",
    "italic": "o",
    "underlined": "n",
    "strikethrough": "m",
}

STYLE_BBCODE = {
    "l": ["[b]", "[/b]"],
    "m": ["", ""],  # 不支持
    "n": ["", ""],  # 不支持
    "o": ["", ""],  # 不支持
}

GAME_MODE_MAP = {"Survival": "生存", "Creative": "创造", "Adventure": "冒险"}

FORMAT_CODE_REGEX = r"§[0-9abcdefgklmnor]"
