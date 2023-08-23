import json
import asyncio
from .. import baidu
import aiohttp


async def Translate(Sentence: str, to_Language: str = "zh", from_Language: str = "") -> str | None:
    """
    :param Sentence: 待翻译语句
    :param from_Language: 待翻译语句语言
    :param to_Language: 目标语言
    :return: 翻译后语句 出错时返回None

    常见语言代码：中文 zh 英语 en 日语 jp
    """
    status = await baidu.Api.Translate.Refresh_Access_Token()
    if status == 1:
        baidu.dumps()
    if status == -1:
        return None
    token = baidu.Api.Translate.access_token
    url = f"https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token={token}"
    if from_Language == "":
        from_Language = "auto"
    headers = {'Content-Type': 'application/json'}
    params = {'q': Sentence, 'from': from_Language, 'to': to_Language}
    # 发送请求
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=json.dumps(params)) as response:
            if response.status == 200:
                response = await response.json()
                if "result" in response.keys():
                    result = response["result"]
                    if "trans_result" in result.keys():
                        trans_result = result["trans_result"][0]
                        if "dst" in trans_result.keys():
                            dst = trans_result["dst"]
                            return dst
    return None


async def Test():
    result = await Translate(Sentence="早上好", to_Language="jp")
    print(result)
    return result


if __name__ == "__main__":
    asyncio.run(Test())
