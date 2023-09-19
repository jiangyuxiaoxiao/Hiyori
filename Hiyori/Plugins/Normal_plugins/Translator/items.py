"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/8-10:13
@Desc: 
@Ver : 1.0.0
"""

from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from Hiyori.Utils.Shop import Item
from .config import translatorConfig


class 中文翻译模块(Item):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        if str(QQ) in translatorConfig.config.keys():
            if translatorConfig.config[str(QQ)] == "zh":
                translatorConfig.config[str(QQ)] = ""
                translatorConfig.dump()
                msg = MessageSegment.at(QQ) + "已取消中文翻译模块"
                await matcher.send(msg)
                return
        translatorConfig.config[str(QQ)] = "zh"
        translatorConfig.dump()
        msg = MessageSegment.at(QQ) + "已切换至中文翻译模块，再次使用可取消。"
        await matcher.send(msg)


class 广东话翻译模块(Item):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        if str(QQ) in translatorConfig.config.keys():
            if translatorConfig.config[str(QQ)] == "yue":
                translatorConfig.config[str(QQ)] = ""
                translatorConfig.dump()
                msg = MessageSegment.at(QQ) + "已取消粤语翻译模块"
                await matcher.send(msg)
                return
        translatorConfig.config[str(QQ)] = "yue"
        translatorConfig.dump()
        msg = MessageSegment.at(QQ) + "已切换至粤语翻译模块，再次使用可取消。"
        await matcher.send(msg)


class 文言文翻译模块(Item):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        if str(QQ) in translatorConfig.config.keys():
            if translatorConfig.config[str(QQ)] == "wyw":
                translatorConfig.config[str(QQ)] = ""
                translatorConfig.dump()
                msg = MessageSegment.at(QQ) + "已取消文言文翻译模块"
                await matcher.send(msg)
                return
        translatorConfig.config[str(QQ)] = "wyw"
        translatorConfig.dump()
        msg = MessageSegment.at(QQ) + "已切换至文言文翻译模块，再次使用可取消。"
        await matcher.send(msg)


class 日语翻译模块(Item):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        if str(QQ) in translatorConfig.config.keys():
            if translatorConfig.config[str(QQ)] == "jp":
                translatorConfig.config[str(QQ)] = ""
                translatorConfig.dump()
                msg = MessageSegment.at(QQ) + "已取消日语翻译模块"
                await matcher.send(msg)
                return
        translatorConfig.config[str(QQ)] = "jp"
        translatorConfig.dump()
        msg = MessageSegment.at(QQ) + "已切换至日语翻译模块，再次使用可取消。"
        await matcher.send(msg)


class 韩语翻译模块(Item):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None, state: T_State = None):
        if str(QQ) in translatorConfig.config.keys():
            if translatorConfig.config[str(QQ)] == "kor":
                translatorConfig.config[str(QQ)] = ""
                translatorConfig.dump()
                msg = MessageSegment.at(QQ) + "已取消韩语翻译模块"
                await matcher.send(msg)
                return
        translatorConfig.config[str(QQ)] = "kor"
        translatorConfig.dump()
        msg = MessageSegment.at(QQ) + "已切换至韩语翻译模块，再次使用可取消。"
        await matcher.send(msg)


class 英语翻译模块(Item):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
                  state: T_State = None):
        if str(QQ) in translatorConfig.config.keys():
            if translatorConfig.config[str(QQ)] == "en":
                translatorConfig.config[str(QQ)] = ""
                translatorConfig.dump()
                msg = MessageSegment.at(QQ) + "已取消英语翻译模块"
                await matcher.send(msg)
                return
        translatorConfig.config[str(QQ)] = "en"
        translatorConfig.dump()
        msg = MessageSegment.at(QQ) + "已切换至英语翻译模块，再次使用可取消。"
        await matcher.send(msg)


class 德语翻译模块(Item):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
                  state: T_State = None):
        if str(QQ) in translatorConfig.config.keys():
            if translatorConfig.config[str(QQ)] == "de":
                translatorConfig.config[str(QQ)] = ""
                translatorConfig.dump()
                msg = MessageSegment.at(QQ) + "已取消德语翻译模块"
                await matcher.send(msg)
                return
        translatorConfig.config[str(QQ)] = "de"
        translatorConfig.dump()
        msg = MessageSegment.at(QQ) + "已切换至德语翻译模块，再次使用可取消。"
        await matcher.send(msg)


class 法语翻译模块(Item):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
                  state: T_State = None):
        if str(QQ) in translatorConfig.config.keys():
            if translatorConfig.config[str(QQ)] == "de":
                translatorConfig.config[str(QQ)] = ""
                translatorConfig.dump()
                msg = MessageSegment.at(QQ) + "已取消法语翻译模块"
                await matcher.send(msg)
                return
        translatorConfig.config[str(QQ)] = "de"
        translatorConfig.dump()
        msg = MessageSegment.at(QQ) + "已切换至法语翻译模块，再次使用可取消。"
        await matcher.send(msg)


class 俄语翻译模块(Item):
    async def use(self, QQ: int, Targets: list[int] = None, Num: int = 0, bot: Bot = None, event: Event = None, matcher: Matcher = None,
                  state: T_State = None):
        if str(QQ) in translatorConfig.config.keys():
            if translatorConfig.config[str(QQ)] == "ru":
                translatorConfig.config[str(QQ)] = ""
                translatorConfig.dump()
                msg = MessageSegment.at(QQ) + "已取消俄语翻译模块"
                await matcher.send(msg)
                return
        translatorConfig.config[str(QQ)] = "ru"
        translatorConfig.dump()
        msg = MessageSegment.at(QQ) + "已切换至俄语翻译模块，再次使用可取消。"
        await matcher.send(msg)
