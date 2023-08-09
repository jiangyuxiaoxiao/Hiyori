"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/8/8-20:46
@Desc: 复读机
@Ver : 1.0.0
"""
import random

from nonebot import on_message
from .config import NICKNAME, TEMP_PATH, FUDU_PROBABILITY
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP
from Hiyori.Utils.Message.Image import get_message_img, get_img_hash, ImageMessage
from Hiyori.Utils.Message.Text import get_message_text
from Hiyori.Utils.Spider.Http import AsyncHttpx


class Fudu:
    def __init__(self):
        self.data = {}

    def append(self, key, content):
        self._create(key)
        self.data[key]["data"].append(content)

    def clear(self, key):
        self._create(key)
        self.data[key]["data"] = []
        self.data[key]["is_repeater"] = False

    def size(self, key) -> int:
        self._create(key)
        return len(self.data[key]["data"])

    def check(self, key, content) -> bool:
        self._create(key)
        return self.data[key]["data"][0] == content

    def get(self, key):
        self._create(key)
        return self.data[key]["data"][0]

    def is_repeater(self, key):
        self._create(key)
        return self.data[key]["is_repeater"]

    def set_repeater(self, key):
        self._create(key)
        self.data[key]["is_repeater"] = True

    def _create(self, key):
        if self.data.get(key) is None:
            self.data[key] = {"is_repeater": False, "data": []}


_fudu_list = Fudu()


fudu = on_message(permission=GROUP, priority=999)


@fudu.handle()
async def _(event: GroupMessageEvent):
    if event.is_tome():
        return
    if msg := get_message_text(event.json()):
        if msg.startswith(f"@{NICKNAME}"):
            await fudu.finish("复制粘贴的虚空艾特？", at_sender=True)
    img = get_message_img(event.json())
    msg = get_message_text(event.json())
    if not img and not msg:
        return
    if img:
        img_hash = await get_fudu_img_hash(img[0], event.group_id)
    else:
        img_hash = ""
    add_msg = msg + "|-|" + img_hash
    if _fudu_list.size(event.group_id) == 0:
        _fudu_list.append(event.group_id, add_msg)
    elif _fudu_list.check(event.group_id, add_msg):
        _fudu_list.append(event.group_id, add_msg)
    else:
        _fudu_list.clear(event.group_id)
        _fudu_list.append(event.group_id, add_msg)
    if _fudu_list.size(event.group_id) > 2:
        if random.random() < FUDU_PROBABILITY and not _fudu_list.is_repeater(event.group_id):
            if random.random() < 0.2:
                if msg.endswith("打断施法喵！"):
                    await fudu.finish("打断喵" + msg)
                else:
                    await fudu.finish("打断施法喵！")
            _fudu_list.set_repeater(event.group_id)
            if img and msg:
                rst = msg + ImageMessage(TEMP_PATH / f"compare_{event.group_id}_img.jpg")
            elif img:
                rst = ImageMessage(TEMP_PATH / f"compare_{event.group_id}_img.jpg")
            elif msg:
                rst = msg
            else:
                rst = ""
            if rst:
                await fudu.finish(rst)


async def get_fudu_img_hash(url, group_id):
    try:
        if await AsyncHttpx.download_file(
            url, TEMP_PATH / f"compare_{group_id}_img.jpg"
        ):
            img_hash = get_img_hash(TEMP_PATH / f"compare_{group_id}_img.jpg")
            return str(img_hash)
        else:
            print(f"复读下载图片失败...")
    except Exception as e:
        print(f"复读读取图片Hash出错 {type(e)}：{e}")
    return ""
