"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/7/31-21:53
@Desc: 
@Ver : 1.0.0
"""
from nonebot.plugin import on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from Hiyori.Utils.Priority import Priority
import requests
import json
import random
import time

__novelai_version__ = "0.1.0"
__novelai_usages__ = f"""
[#二次元的我] 康康你的二次元形象
""".strip()

__plugin_meta__ = PluginMetadata(
    name="二次元的我",
    description="康康你的二次元形象",
    usage=__novelai_usages__,
    type="application",
    extra={
        "version": __novelai_version__,
        "CD_Weight": 0,
        "example": "二次元的我",
        "permission": "普通权限",
        "Keep_On": False,
        "Type": "Zao_plugin",
    },
)


search = on_command("二次元的我", block=True, priority=Priority.普通优先级)

with open(f"./Data/Novelai/tag_data.json",encoding="utf-8") as f: #初始化tags
    tag_data = json.load(f)
tags_id = ["优秀实践","风格","头发","发色","衣服","鞋子","装饰","胸","类型","身份","表情","二次元","基础动作","手动作","腿动作","复合动作","露出","场景","物品","天气","环境"]
tags = "{{highly detailed}},{{masterpiece}},{ultra-detailed},{illustration},{{1girl}},{{best quality}}" #正面默认tags
ntags = "lowres,bad anatomy,bad hands,text,error,missing fingers,extra digit,fewer digits,cropped,worst quality,low quality,normal quality,jpeg artifacts,signature,watermark,username,blurry,missing arms,long neck,Humpbacked"


async def be_girl(uid):
    tags = ""
    goal_tag = {}
    uid = int(uid)
    random.seed(uid * (int(time.time()/3600/24)))
    for i in tags_id:
        tag_list = []
        for j in tag_data[i]:
            tag_list.append(j)
        goal_tag[i] = random.choice(tag_list)
    for i in goal_tag:
        tags += "," + tag_data[i][goal_tag[i]]
    msg = f'头发是{goal_tag["发色"]}{goal_tag["头发"]},胸部{goal_tag["胸"]},穿着{goal_tag["衣服"]},{goal_tag["鞋子"]},{goal_tag["装饰"]},萌点是{goal_tag["二次元"]},身份是{goal_tag["身份"]}{goal_tag["类型"]}'
    return msg,tags
@search.handle()
async def _(event: MessageEvent):
    uid = event.user_id
    url = "http://liuliying.cn:6633/api/novelai"
    width = "512"
    height = "768"
    msg, prompt = await be_girl(uid)
    try:
        resimg = requests.get(f"{url}?width={width}&height={height}&prompt={prompt}&seed=-1&negative={ntags}&draw_type=txt").json()["url"]
        msg = f"二次元少女的你今天,{msg}"
        message = msg + MessageSegment.image(resimg)
    except:
        message = "接往二次元世界的大门打开失败了喵"
    await search.send(message)



