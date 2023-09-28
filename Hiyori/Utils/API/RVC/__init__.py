"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/09/27-09:37
@Desc: RVC对接
@Ver : 1.0.0
"""

from Hiyori.Utils.API.RVC.config import rvcConfig
import aiohttp
import asyncio


def getAllRVCModels() -> set:
    result = set()
    for index, model in rvcConfig.models.items():
        result.add(index)
        result.add(model)
    return result


async def voiceConversion(model: int | str, input_audio_path: str, f0_up_key: int = 0, f0_file: str = "", f0_method: str = "rmvpe",
                          index_rate: float = 0.75, filter_radius: int = 3, resample_sr: int = 0,
                          rms_mix_rate: float = 0.25, protect: float = 0.33) -> bytes | None:
    """
    语音转换

    :param model: 使用模型
    :param input_audio_path: 输入音频路径
    :param f0_up_key: 音高变化 -12~12
    :param f0_file: 音高文件
    :param f0_method: 音高方法 "pm", "harvest", "crepe", "rmvpe"
    :param index_rate: 检索特征占比 0.75
    :param filter_radius: 0~7 >=3 则使用对harvest音高识别的结果使用中值滤波，数值为滤波半径，使用可以削弱哑音
    :param resample_sr: 0~48000 后处理重采样至最终采样率，0为不进行重采样
    :param rms_mix_rate: 0~1 输入源音量包络替换输出音量包络融合比例，越靠近1越使用输出包络
    :param protect: 0~0.5 保护清辅音和呼吸声，防止电音撕裂等artifact，拉满0.5不开启，调低加大保护力度但可能降低索引效果
    :return: 音频 bytes
    """

    if isinstance(model, int):
        model_id = model
    elif isinstance(model, str):
        if model not in rvcConfig.models.keys():
            return None
        model_id = rvcConfig.models[model]
    else:
        return None
    url = f"{rvcConfig.host}:{rvcConfig.port}/voice"
    params = {
        "model_id": model_id,
        "input_audio_path": input_audio_path,
        "f0_up_key": f0_up_key,
        "f0_file": f0_file,
        "f0_method": f0_method,
        "index_rate": index_rate,
        "filter_radius": filter_radius,
        "resample_sr": resample_sr,
        "rms_mix_rate": rms_mix_rate,
        "protect": protect
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                response = await response.read()
                return response
    return None


if __name__ == '__main__':
    asyncio.run(voiceConversion("妃爱", "E:/Projects/Hiyori/Hiyori/Data/Bert_RVC/762911036103973.wav"))
