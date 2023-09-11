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
from playwright.async_api import async_playwright

from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment

from Hiyori.Utils.File import DirExist, JsonFileExist

# 模块初始化
status = DirExist("Config/Utils/API", logEnable=True)


# Json Config 格式定义
class Baidu:
    class Api:
        class AccessToken:
            def __init__(self, access_host="https://aip.baidubce.com/oauth/2.0/token",
                         api_key="", secret_key="", access_token="", refresh_token="",
                         timeout_date="1999-12-31 23:59:59"):
                self.access_host = access_host
                self.api_key = api_key
                self.secret_key = secret_key
                self.access_token = access_token
                self.refresh_token = refresh_token
                self.timeout_date = timeout_date

            # 序列化为字典Z
            def to_dict(self) -> dict[str, any]:
                return {
                    "access_host": self.access_host,
                    "api_key": self.api_key,
                    "secret_key": self.secret_key,
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "timeout_date": self.timeout_date
                }

            # 反序列化
            @classmethod
            def from_dict(cls, data: dict[str, any]):
                return cls(data["access_host"], data["api_key"], data["secret_key"], data["access_token"], data["refresh_token"],
                           data["timeout_date"])

            async def Refresh_Access_Token(self) -> int:
                """
                异步获取access token，当成功获取后根据状态返回值：\n
                -1 失败\n
                0 成功，未更新\n
                1 成功，已更新\n
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

        class PanAccessToken:
            def __init__(self, access_host: str = "http://openapi.baidu.com/oauth/2.0",
                         app_key: str = "", secret_key: str = "", userInfo: dict = None):
                if userInfo is None:
                    userInfo = {}
                self.access_host = access_host
                self.app_key = app_key
                self.secret_key = secret_key
                self.userInfo = userInfo

            def to_dict(self) -> dict[str, any]:
                return {
                    "access_host": self.access_host,
                    "app_key": self.app_key,
                    "secret_key": self.secret_key,
                    "userInfo": self.userInfo
                }

            @classmethod
            def from_dict(cls, data: dict[str, any]):
                return cls(data["access_host"], data["app_key"], data["secret_key"], data["userInfo"])

            async def openapi_Refresh_Access_Token(self, QQ: int, matcher: Matcher) -> int:
                """
                异步更新access token，当成功获取后根据状态返回值：\n
                -1 失败\n
                0 成功，未更新\n
                1 成功，已更新\n
                当返回1说明配置文件需要在外部进行变更保存。
                """
                # 未配置key
                if self.app_key == "" or self.secret_key == "":
                    return -1
                # 未配置refreshToken:
                flag_get_refresh_token = False  # 是否新获得refresh_token
                if self.userInfo[str(QQ)]["refresh_token"] == "":
                    stat = await self.openapi_Get_Refresh_Token(QQ, matcher)
                    if stat == -1:
                        return -1
                    else:
                        flag_get_refresh_token = True
                # 检查是否过期
                timeout = datetime.strptime(self.userInfo[str(QQ)]["timeout_date"], "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                if now < timeout:
                    # 未过期
                    if self.userInfo[str(QQ)]["access_token"] != "":
                        # 已刷新refresh token，配置已更新
                        if flag_get_refresh_token:
                            return 1
                        else:
                            return 0
                # 网络请求access key
                refresh_token = self.userInfo[str(QQ)]["refresh_token"]
                url = f"https://openapi.baidu.com/oauth/2.0/token?" \
                      f"grant_type=refresh_token" \
                      f"&refresh_token={refresh_token}" \
                      f"&client_id={self.app_key}" \
                      f"&client_secret={self.secret_key}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            responseJsonDict = await response.json()
                            self.userInfo[str(QQ)]["refresh_token"] = responseJsonDict["refresh_token"]
                            if "access_token" in responseJsonDict.keys():
                                self.userInfo[str(QQ)]["access_token"] = responseJsonDict["access_token"]
                                if "expires_in" in responseJsonDict.keys():
                                    expires_in = responseJsonDict["expires_in"]
                                    timeout = now + timedelta(seconds=expires_in)
                                    self.userInfo[str(QQ)]["timeout_date"] = timeout.strftime("%Y-%m-%d %H:%M:%S")
                                    return 1
                                else:
                                    return -1
                return -1

            async def openapi_Get_Refresh_Token(self, QQ: int, matcher: Matcher) -> int:
                """
                异步获取RefreshToken，根据获取状态返回值：\n
                -1 失败\n
                1 成功，已更新\n
                :return:
                """
                # 未配置key
                if self.app_key == "" or self.secret_key == "":
                    return -1
                # 未提供matcher
                if matcher is None:
                    return -1
                # 获取token
                url = f"http://openapi.baidu.com/oauth/2.0/authorize?" \
                      f"&response_type=code" \
                      f"&client_id={self.app_key}" \
                      f"&redirect_uri=oob" \
                      f"&qrcode=1" \
                      f"&scope=basic,netdisk"
                now = datetime.now()
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context()
                    page = await context.new_page()
                    await page.goto(url)
                    await page.wait_for_selector(".g-bd-wp.wordwrap.clearfix")
                    screen = await page.query_selector(".g-bd-wp.wordwrap.clearfix")
                    image = await screen.screenshot()
                    msg = "操作前请先登录。请扫描百度网盘二维码登录。扫描后妃爱将获得网盘操作的授权，请谨慎操作。"
                    msg += MessageSegment.at(QQ) + MessageSegment.image(image)
                    await matcher.send(msg)
                    await page.wait_for_selector("#Verifier", timeout=120000)
                    code = await page.query_selector("#Verifier")
                    code = await code.get_attribute("value")
                    code = str(code)
                url = f"https://openapi.baidu.com/oauth/2.0/token?" \
                      f"grant_type=authorization_code&" \
                      f"&code={code}" \
                      f"&client_id={self.app_key}" \
                      f"&client_secret={self.secret_key}" \
                      f"&redirect_uri=oob"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            responseJsonDict = await response.json()
                            if str(QQ) not in self.userInfo.keys():
                                self.userInfo[str(QQ)] = {}
                            self.userInfo[str(QQ)]["refresh_token"] = responseJsonDict["refresh_token"]
                            if "access_token" in responseJsonDict.keys():
                                self.userInfo[str(QQ)]["access_token"] = responseJsonDict["access_token"]
                                if "expires_in" in responseJsonDict.keys():
                                    expires_in = responseJsonDict["expires_in"]
                                    timeout = now + timedelta(seconds=expires_in)
                                    self.userInfo[str(QQ)]["timeout_date"] = timeout.strftime("%Y-%m-%d %H:%M:%S")
                                    msg = MessageSegment.at(QQ) + "登录成功"
                                    await matcher.send(msg)
                                    return 1
                return -1

        def __init__(self, Translate=AccessToken(), Pan=PanAccessToken(), OpenTranslate=AccessToken()):
            self.Translate = Translate
            self.Pan = Pan
            self.OpenTranslate = OpenTranslate

        def to_dict(self) -> dict[str, any]:
            return {
                "Translate": self.Translate.to_dict(),
                "Pan": self.Pan.to_dict(),
                "OpenTranslate": self.OpenTranslate.to_dict()
            }

        @classmethod
        def from_dict(cls, data: dict[str, any]):
            return cls(Baidu.Api.AccessToken.from_dict(data["Translate"]),
                       Baidu.Api.PanAccessToken.from_dict(data["Pan"]),
                       Baidu.Api.AccessToken.from_dict(data["OpenTranslate"]))

    def __init__(self, api=Api()):
        self.Api = api
        # 检查文件是否存在，不存在则初始化创建
        JsonFileExist(Path="./Config/Utils/API/Baidu.json", initContent=self.to_dict(), logEnable=True)
        with open("./Config/Utils/API/Baidu.json", encoding="utf-8", mode="r") as f:
            data = json.loads(f.read())
            self.Api = Baidu.Api.from_dict(data["Api"])

    def to_dict(self) -> dict[str, any]:
        return {
            "Api": self.Api.to_dict()
        }

    def loads(self):
        """从配置文件中读取"""
        with open("./Config/Utils/API/Baidu.json", encoding="utf-8", mode="r") as f:
            data = json.loads(f.read())
            self.Api = Baidu.Api.from_dict(data["Api"])

    def dumps(self):
        """写入配置到文件中"""
        with open("./Config/Utils/API/Baidu.json", encoding="utf-8", mode="w") as f:
            f.write(json.dumps(self.to_dict(), indent=2, ensure_ascii=False))


baidu = Baidu()
