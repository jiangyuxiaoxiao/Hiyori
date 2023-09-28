"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/09/28-14:22
@Desc: Vits封装
@Ver : 1.0.0
"""
import aiohttp
import aiofiles
from Hiyori.Utils.API.Vits.config import vitsConfig
from Hiyori.Utils.API.Baidu.OpenTranslate import Translate


def getVits_Map() -> dict:
    """获取角色名——(model_id,chr_id)映射"""
    chrDict: dict[str, dict[str, int]] = dict()
    for index, model in enumerate(vitsConfig.models):
        for name, cid in model["spk2id"].items():
            chrDict[name] = {
                "mid": index,
                "cid": cid
            }
    return chrDict


def getModelsConfig() -> list:
    """获取模型配置信息"""
    return vitsConfig.models


async def getVoice(text: str, model: int | str, character: int | str) -> bytes | None:
    model_id = 0
    vits_model = None
    if isinstance(model, int):
        model_id = model
        if model_id >= len(vitsConfig.models):
            # 无效模型
            return None
        vits_model = vitsConfig.models[model_id]
    elif isinstance(model, str):
        for index, m in enumerate(vitsConfig.models):
            if model in m["names"]:
                vits_model = m
                model_id = index
                break
        if vits_model is None:
            return None
    else:
        raise TypeError("model should be a str or int value")
    if isinstance(character, int):
        chr_id = character
    elif isinstance(character, str):
        if character not in vits_model["spk2id"].keys():
            return None
        chr_id = vits_model["spk2id"][character]
    else:
        raise TypeError("character should be a str or int value")
    if "language" in vits_model.keys() and vits_model["language"] == "zh":
        pass
    else:
        text = await Translate(Sentence=text, to_Language="jp")
    url = f"{vitsConfig.host}:{vitsConfig.port}/voice?model_id={model_id}&chr_id={chr_id}&typ=t&text={text}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response = await response.read()
                return response


async def saveVoice(savePath: str, text: str, model: int | str, character: int | str) -> bool:
    """保存音频文件至本地"""
    audio = await getVoice(text, model, character)
    if audio is None:
        return False
    async with aiofiles.open(savePath, 'wb') as f:
        await f.write(audio)
    return True
