import os
import random
import re

from .config import NICKNAME, DATA_PATH, TL_KEY, ALAPI_TOKEN, IMAGE_PATH, ALAPI_AI_CHECK
from Hiyori.Utils.Spider.Http import AsyncHttpx
from Hiyori.Utils.Message.Image import face, ImageMessage

from .utils import ai_message_manager

try:
    import ujson as json
except ModuleNotFoundError:
    import json


url = "http://openapi.tuling123.com/openapi/api/v2"

check_url = "https://v2.alapi.cn/api/censor/text"

index = 0

Hiyori_data = json.load(open(DATA_PATH / "Hiyori.json", "r", encoding="utf8"))


async def get_chat_result(text: str, img_url: str, user_id: int, nickname: str) -> str:
    """
    获取 AI 返回值，顺序： 特殊回复 -> 图灵 -> 青云客
    :param text: 问题
    :param img_url: 图片链接
    :param user_id: 用户id
    :param nickname: 用户昵称
    :return: 回答
    """
    global index
    ai_message_manager.add_message(user_id, text)
    special_rst = await ai_message_manager.get_result(user_id, nickname)
    if special_rst:
        ai_message_manager.add_result(user_id, special_rst)
        return special_rst
    if index == 5:
        index = 0
    if len(text) < 6 and random.random() < 0.6:
        keys = Hiyori_data.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(Hiyori_data[key]).replace("你", nickname)
    rst = await tu_ling(text, img_url, user_id)
    if not rst:
        rst = await xie_ai(text)
    if not rst:
        return no_result()
    if nickname:
        if len(nickname) < 5:
            if random.random() < 0.5:
                nickname = "~".join(nickname) + "~"
                if random.random() < 0.2:
                    if nickname.find("大人") == -1:
                        nickname += "大~人~"
        rst = str(rst).replace("小主人", nickname).replace("小朋友", nickname)
    ai_message_manager.add_result(user_id, rst)
    return rst


# 图灵接口
async def tu_ling(text: str, img_url: str, user_id: int) -> str:
    """
    获取图灵接口的回复
    :param text: 问题
    :param img_url: 图片链接
    :param user_id: 用户id
    :return: 图灵回复
    """
    global index
    req = None
    if not TL_KEY:
        return ""
    try:
        if text:
            req = {
                "perception": {
                    "inputText": {"text": text},
                    "selfInfo": {
                        "location": {"city": "陨石坑", "province": "火星", "street": "第5坑位"}
                    },
                },
                "userInfo": {"apiKey": TL_KEY[index], "userId": str(user_id)},
            }
        elif img_url:
            req = {
                "reqType": 1,
                "perception": {
                    "inputImage": {"url": img_url},
                    "selfInfo": {
                        "location": {"city": "陨石坑", "province": "火星", "street": "第5坑位"}
                    },
                },
                "userInfo": {"apiKey": TL_KEY[index], "userId": str(user_id)},
            }
    except IndexError:
        index = 0
        return ""
    text = ""
    response = await AsyncHttpx.post(url, json=req)
    if response.status_code != 200:
        return no_result()
    resp_payload = json.loads(response.text)
    if int(resp_payload["intent"]["code"]) in [4003]:
        return ""
    if resp_payload["results"]:
        for result in resp_payload["results"]:
            if result["resultType"] == "text":
                text = result["values"]["text"]
                if "请求次数超过" in text:
                    text = ""
    return text


# 屑 AI
async def xie_ai(text: str) -> str:
    """
    获取青云客回复
    :param text: 问题
    :return: 青云可回复
    """
    res = await AsyncHttpx.get(
        f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={text}"
    )
    content = ""
    try:
        data = json.loads(res.text)
        if data["result"] == 0:
            content = data["content"]
            if "菲菲" in content:
                content = content.replace("菲菲", NICKNAME)
            if "艳儿" in content:
                content = content.replace("艳儿", NICKNAME)
            if "公众号" in content:
                content = ""
            if "{br}" in content:
                content = content.replace("{br}", "\n")
            if "提示" in content:
                content = content[: content.find("提示")]
            if "淘宝" in content or "taobao.com" in content:
                return ""
            while True:
                r = re.search("{face:(.*)}", content)
                if r:
                    id_ = r.group(1)
                    content = content.replace(
                        "{" + f"face:{id_}" + "}", str(face(int(id_)))
                    )
                else:
                    break
        return (
            content
            if not content and ALAPI_AI_CHECK is False
            else await check_text(content)
        )
    except Exception as e:
        print(f"Ai xie_ai 发生错误 {type(e)}：{e}")
        return ""


def hello() -> str:
    """
    一些打招呼的内容
    """
    result = random.choice(
        (
            "你好Ov<",
            "你好喵~",
        )
    )
    result += ImageMessage(IMAGE_PATH / "hellp.png")
    return result


# 没有回答时回复内容
def no_result() -> str:
    """
    没有回答时的回复
    """
    return random.choice(
        [
            f"纯洁的{NICKNAME}没听懂",
            "下次再告诉你喵~",
            "我！不！知！道！",
        ]
    )


async def check_text(text: str) -> str:
    """
    ALAPI文本检测，主要针对青云客API，检测为恶俗文本改为无回复的回答
    :param text: 回复
    """
    if not ALAPI_TOKEN:
        return text
    params = {"token": ALAPI_TOKEN, "text": text}
    try:
        data = (await AsyncHttpx.get(check_url, timeout=2, params=params)).json()
        if data["code"] == 200:
            if data["data"]["conclusion_type"] == 2:
                return ""
    except Exception as e:
        print(f"检测违规文本错误...{type(e)}：{e}")
    return text
