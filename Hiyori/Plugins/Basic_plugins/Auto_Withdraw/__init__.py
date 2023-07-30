"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/30-21:34
@Desc: 发言自动定时撤回
@Ver : 1.0.0
"""
import json
import os
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent
from nonebot import get_bot
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from .config import Config
from Hiyori.Utils.File import JsonFileExist

# 文件初始化
JsonFileExist(os.path.join(Config.path, "Group.json"))  # 不存在文件则进行创建
JsonFileExist(os.path.join(Config.path, "Private.json"))  # 不存在文件则进行创建


class withDrawHelper:
    @staticmethod
    def getInfo(QQ: int = 0, GroupID: int = 0) -> dict[str, any]:
        """
        若传入QQ，则读取个人的撤回设置信息。否则读取群组的撤回设置信息
        """
        if QQ == 0:
            Path = os.path.join(Config.path, "Group.json")
            Target = str(GroupID)
        else:
            Path = os.path.join(Config.path, "Private.json")
            Target = str(QQ)
        with open(Path, mode="r", encoding="utf-8") as file:
            info: dict = json.loads(file.read())

        # 若信息不存在，则先写入
        if Target not in info.keys():
            info[Target] = {
                "CD": 60,
                "On": True
            }
            with open(Path, mode="w", encoding="utf-8") as file:
                file.write(json.dumps(info, ensure_ascii=False, indent=4))
        return info[Target]

    @staticmethod
    def setInfo(QQ: int = 0, GroupID: int = 0, setInfo: dict = None):
        """
        若传入QQ，则写入个人的撤回设置信息。否则写入群组的撤回设置信息
        """
        if QQ == 0:
            Path = os.path.join(Config.path, "Group.json")
            Target = str(GroupID)
        else:
            Path = os.path.join(Config.path, "Private.json")
            Target = str(QQ)
        with open(Path, mode="r", encoding="utf-8") as file:
            info: dict = json.loads(file.read())
        info[Target] = setInfo
        with open(Path, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(info, ensure_ascii=False, indent=4))


@Bot.on_called_api
async def withdrawSelfMessage(bot: Bot, exception: Exception, api: str, data: dict[str, any], result: any):
    """
    bot发送消息后定时进行撤回。
    TODO：支持群组，用户进行自定义配置。删除转发消息。

    """
    # event: Event = current_event.get()
    if "group_id" in data:
        if data["group_id"] == 794284558:
            if api in ["send_msg", "send_group_msg", "send_private_msg", "send_group_forward_msg", "send_private_forward_msg"]:
                if "message_id" in result.keys():
                    # 设置异步任务，避免阻塞
                    asyncio.create_task(withDrawMessage(bot, result["message_id"]))
                    # asyncio.create_task(withDrawMessage(bot, event.message_id))


@run_preprocessor
async def withdrawTargetMessage(event: MessageEvent, matcher: Matcher):
    if hasattr(event, "group_id"):
        if event.group_id == 794284558:
            if hasattr(event, "message_id"):
                bot = get_bot(str(event.self_id))
                asyncio.create_task(withDrawMessage(bot, event.message_id))


async def withDrawMessage(bot: Bot, message_id: int):
    await asyncio.sleep(Config.defaultCD)
    try:
        await bot.delete_msg(message_id=message_id)
    except Exception as e:
        pass
