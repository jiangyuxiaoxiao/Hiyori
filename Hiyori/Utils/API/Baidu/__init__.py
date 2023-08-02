"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/2-8:59
@Desc: 百度云API调用
@Ver : 1.0.0
"""
import json

import aiohttp
from datetime import datetime, timedelta

from Hiyori.Utils.File import DirExist, JsonFileExist

# 模块初始化
status = DirExist("./Data/Utils/API", logEnable=True)


# Json Config 格式定义
class Baidu:
    class Api:
        class AccessToken:
            def __init__(self, access_host="https://aip.baidubce.com/oauth/2.0/token",
                         api_key="", secret_key="", access_token="",
                         timeout_date="1999-12-31 23:59:59"):
                self.access_host = access_host
                self.api_key = api_key
                self.secret_key = secret_key
                self.access_token = access_token
                self.timeout_date = timeout_date

            # 序列化为字典
            def to_dict(self) -> dict[str, any]:
                return {
                    "access_host": self.access_host,
                    "api_key": self.api_key,
                    "secret_key": self.secret_key,
                    "access_token": self.access_token,
                    "timeout_date": self.timeout_date
                }

            # 反序列化
            @classmethod
            def from_dict(cls, data: dict[str, any]):
                return cls(data["access_host"], data["api_key"], data["secret_key"], data["access_token"],
                           data["timeout_date"])

            async def Refresh_Access_Token(self) -> int:
                """
                异步获取access token，当成功获取后根据状态返回值：
                -1 失败
                0 成功，未更新
                1 成功，已更新
                :return:
                """
                # 未配置key
                if self.api_key == "" or self.secret_key == "":
                    return -1

                # 检查是否过期
                timeout = datetime.strptime(self.timeout_date, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                if now < timeout:
                    # 未过期
                    if self.access_token != "":
                        return 0

                # 网络请求access key
                url = self.access_host + "?" \
                                         f"grant_type=client_credentials" \
                                         f"&client_id={self.api_key}" \
                                         f"&client_secret={self.secret_key}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            responseJsonDict = await response.json()
                            if "access_token" in responseJsonDict.keys():
                                self.access_token = responseJsonDict["access_token"]
                                if "expires_in" in responseJsonDict.keys():
                                    expires_in = responseJsonDict["expires_in"]
                                    timeout = now + timedelta(seconds=expires_in)
                                    self.timeout_date = timeout.strftime("%Y-%m-%d %H:%M:%S")
                                    return 1
                                else:
                                    return -1
                return -1

        def __init__(self, Translate=AccessToken()):
            self.Translate = Translate

        def to_dict(self) -> dict[str, any]:
            return {
                "Translate": self.Translate.to_dict()
            }

        @classmethod
        def from_dict(cls, data: dict[str, any]):
            return cls(Baidu.Api.AccessToken.from_dict(data["Translate"]))

    def __init__(self, api=Api()):
        self.Api = api
        # 检查文件是否存在，不存在则初始化创建
        JsonFileExist(Path="./Data/Utils/API/Baidu.json", initContent=self.to_dict(), logEnable=True)
        with open("./Data/Utils/API/Baidu.json", encoding="utf-8", mode="r") as f:
            data = json.loads(f.read())
            self.Api = Baidu.Api.from_dict(data["Api"])

    def to_dict(self) -> dict[str, any]:
        return {
            "Api": self.Api.to_dict()
        }

    def loads(self):
        """从配置文件中读取"""
        with open("./Data/Utils/API/Baidu.json", encoding="utf-8", mode="r") as f:
            data = json.loads(f.read())
            self.Api = Baidu.Api.from_dict(data["Api"])

    def dumps(self):
        """写入配置到文件中"""
        with open("./Data/Utils/API/Baidu.json", encoding="utf-8", mode="w") as f:
            f.write(json.dumps(self.to_dict(), indent=2, ensure_ascii=False))



