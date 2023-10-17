"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/09/28-15:08
@Desc: vits/bert-vits2 插件
@Ver : 1.0.0
"""
import re

from nonebot import on_regex
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment

from Hiyori.Plugins.Basic_plugins.nonebot_plugin_htmlrender import md_to_pic
from Hiyori.Utils.Priority import Priority
import Hiyori.Utils.API.BertVits as BertVits
import Hiyori.Utils.API.Vits as Vits

from .rule import vitsCheck

__plugin_meta__ = PluginMetadata(
    name="老婆语音",
    description="Vits语音合成，让妃爱学你的老婆说话吧！",
    usage="xx说[要说的话] \n详细的人物列表请调用指令#老婆语音列表 来查看",
    extra={
        "CD_Weight": 2,
        "permission": "普通权限",
        "example": "",
        "Keep_On": False,
        "Type": "Normal_Plugin",
    },
)

bertMap = BertVits.getBV_Map()
vitsMap = Vits.getVits_Map()
bertModels = BertVits.getModelsConfig()
vitsModels = Vits.getModelsConfig()
vitsModelsInfo: dict[str, list[str]] = dict()
bertModelsInfo: dict[str, list[str]] = dict()

for model in bertModels:
    if model["names"][0] not in bertModelsInfo.keys():
        bertModelsInfo[model["names"][0]] = list(model["spk2id"])
    else:
        bertModelsInfo[model["names"][0]] += list(model["spk2id"])

for model in vitsModels:
    if model["names"][0] not in vitsModelsInfo.keys():
        vitsModelsInfo[model["names"][0]] = list(model["spk2id"])
    else:
        vitsModelsInfo[model["names"][0]] += list(model["spk2id"])

vitsSound = on_regex(pattern=r"#?.+说", priority=Priority.普通优先级, block=False, rule=vitsCheck)
helpMenu = on_regex(r"^#?老婆语音列表$", priority=Priority.高优先级, block=True)


@vitsSound.handle()
async def _(event: MessageEvent):
    msg = event.message.extract_plain_text()
    text = msg.split("说", maxsplit=1)[1]
    if text == "":
        return
    msg = re.match(pattern=r"#?.+说", string=msg)
    if msg is None:
        return
    name = msg.group().split("说")[0].lstrip("#").strip()
    # 优先使用bert模型
    if name in bertMap.keys():
        audio = await BertVits.getVoice(text=text, model=bertMap[name]["mid"], character=bertMap[name]["cid"])
        await vitsSound.send(MessageSegment.record(audio))
        return
    if name in vitsMap.keys():
        audio = await Vits.getVoice(text=text, model=vitsMap[name]["mid"], character=vitsMap[name]["cid"])
        await vitsSound.send(MessageSegment.record(audio))


@helpMenu.handle()
async def _(event: MessageEvent):
    mdContent = "# 老婆语音列表  \n"
    mdContent += "## 一.Vits模型  \n"
    for name, characters in vitsModelsInfo.items():
        mdContent += f"### {name}  \n\n"
        mdContent += ", ".join(characters)
        mdContent += "\n---\n"
    mdContent += "\n## 二.bertVits2模型  \n"
    for name, characters in bertModelsInfo.items():
        if name == "崩原":
            continue
        mdContent += f"### {name}  \n\n"
        mdContent += ", ".join(characters)
        mdContent += "\n---\n"
    image = await md_to_pic(md=mdContent, width=1200)
    await helpMenu.send(MessageSegment.image(image))
