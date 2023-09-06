"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/6-16:41
@Desc: 百度翻译开放平台接入
@Ver : 1.0.0
"""
import json
import asyncio
if __name__ == "__main__":
    from Hiyori.Utils.API.Baidu import baidu
else:
    from .. import baidu
import aiohttp
import random
import hashlib


async def Translate(Sentence: str, to_Language: str = "zh", from_Language: str = "") -> str | None:
    """
    :param Sentence: 待翻译语句
    :param from_Language: 待翻译语句语言
    :param to_Language: 目标语言
    :return: 翻译后语句 出错时返回None

    常见语言代码：中文 zh 英语 en 日语 jp
    """
    appid = baidu.Api.OpenTranslate.api_key
    key = baidu.Api.OpenTranslate.secret_key
    url = f"https://fanyi-api.baidu.com/api/trans/vip/translate"

    # 签名计算 参考文档 https://api.fanyi.baidu.com/product/113
    salt = str(random.randint(1, 100000))
    signString = appid + Sentence + salt + key
    hs = hashlib.md5()
    hs.update(signString.encode("utf-8"))
    signString = hs.hexdigest()
    if from_Language == "":
        from_Language = "auto"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {"q": Sentence, "from": from_Language, "to": to_Language, "appid": appid, "salt": salt, "sign": signString}
    # 发送请求
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=payload, headers=headers) as response:
            if response.status == 200:
                response = await response.json()
                if "trans_result" in response.keys():
                    result = response["trans_result"][0]
                    if "dst" in result.keys():
                        dst = result["dst"]
                        return dst

    return None


async def Test():
    result = await Translate(Sentence="早上好", to_Language="jp")
    print(result)
    return result


if __name__ == "__main__":
    asyncio.run(Test())
