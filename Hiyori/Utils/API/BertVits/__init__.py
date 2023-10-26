"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/09/27-10:34
@Desc: BertVits2封装
@Ver : 1.0.0
"""
import aiohttp
import asyncio
import aiofiles
from Hiyori.Utils.API.BertVits.config import bertVitsConfig
from Hiyori.Utils.API.Baidu.OpenTranslate import Translate


def getBV_Map() -> dict:
    """获取角色名——(model_id,chr_id)映射"""
    chrDict: dict[str, dict[str, int]] = dict()
    for index, model in enumerate(bertVitsConfig.models):
        for name, cid in model["spk2id"].items():
            chrDict[name] = {
                "mid": index,
                "cid": cid
            }
    return chrDict


def getModelsConfig() -> list:
    return bertVitsConfig.models


async def getVoice(text: str, model: int | str, character: int | str, sdp_ratio: float = 0.2,
                   noise: float = 0.2, noisew: float = 0.9,
                   length: float = 1.0, url=None) -> bytes | None:
    """
    获取bertVits语音（TTS)

    :param text: 待转换文本
    :param model: 当为int时为模型索引id，当为str时为模型名
    :param character: 当为int时为角色索引id，当为str时为角色名
    :param sdp_ratio:
    :param noise:
    :param noisew:
    :param length:
    :param url: 临时的url
    :return: 音频字节
    """
    if url is None:
        url = f"{bertVitsConfig.host}:{bertVitsConfig.port}/voice"
    bv_model = None
    model_id = 0
    if isinstance(model, int):
        model_id = model
        if model_id >= len(bertVitsConfig.models):
            # 无效模型
            return None
        bv_model = bertVitsConfig.models[model_id]
    elif isinstance(model, str):
        for index, m in enumerate(bertVitsConfig.models):
            if model in m["names"]:
                bv_model = m
                model_id = index
                break
        if bv_model is None:
            return None
    else:
        raise TypeError("model should be a str or int value")

    if isinstance(character, int):
        chr_id = character
    elif isinstance(character, str):
        if character not in bv_model["spk2id"].keys():
            return None
        chr_id = bv_model["spk2id"][character]
    else:
        raise TypeError("character should be a str or int value")

    # 检查是否需要翻译
    if "trans" in bv_model:
        trans = bv_model["trans"]
        texts = text.split("\n")
        outs = []
        for t in texts:
            if t != "":
                out = await Translate(Sentence=t, to_Language=trans)
                outs.append(out)
            else:
                outs.append(t)
        text = "\n".join(outs)

    params = {
        "model_id": model_id,
        "chr_id": chr_id,
        "text": text,
        "sdp_ratio": sdp_ratio,
        "noise": noise,
        "noisew": noisew,
        "length": length
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                response = await response.read()
                return response
    return None


async def saveVoice(savePath: str, text: str, model: int | str, chr: int | str, sdp_ratio: float = 0.2,
                    noise: float = 0.2, noisew: float = 0.9,
                    length: float = 1.0) -> bool:
    """保存音频文件至本地"""
    audio = await getVoice(text, model, chr, sdp_ratio, noise, noisew, length)
    if audio is None:
        return False
    async with aiofiles.open(savePath, 'wb') as f:
        await f.write(audio)
    return True


if __name__ == '__main__':
    asyncio.run(saveVoice("Data/Test/1.wav", "",
                          1, "顾真真"))
