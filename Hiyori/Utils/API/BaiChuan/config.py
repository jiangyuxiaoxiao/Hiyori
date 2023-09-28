"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/09/28-10:17
@Desc: 配置文件
@Ver : 1.0.0
"""
import os
import json
from Hiyori.Utils.File import JsonFileExist, DirExist
from Hiyori.Utils.Config import Config

ConfigPath = "./Config/Utils/API/BaiChuan.json"


class BaiChuanConfig(Config):

    def __init__(self):
        initContent = {
            "host": "http://127.0.0.1",
            "port": 8080,
            "最长对话轮数": 10
        }
        DirExist(os.path.dirname(ConfigPath))
        JsonFileExist(Path=ConfigPath, initContent=initContent, logEnable=True, logInfo="【Baichuan-chat支持】配置文件不存在，正在创建中。")
        with open(file=ConfigPath, mode="r", encoding="utf-8") as file:
            config = json.loads(file.read())
            self.host = config["host"]
            self.port = config["port"]
            self.maxLength = config["最长对话轮数"]

    def dump(self):
        """导出到配置文件中"""
        with open(file=ConfigPath, mode="w", encoding="utf-8") as file:
            content = {
                "host": self.host,
                "port": self.port,
                "最长对话轮数": self.maxLength
            }
            file.write(json.dumps(content, ensure_ascii=False, indent=2))

    def load(self):
        initContent = {
            "host": "http://127.0.0.1",
            "port": 8080,
            "最长对话轮数": 10
        }
        JsonFileExist(Path=ConfigPath, initContent=initContent, logEnable=True, logInfo="【Baichuan-chat支持】配置文件不存在，正在创建中。")
        with open(file=ConfigPath, mode="r", encoding="utf-8") as file:
            config = json.loads(file.read())
            self.host = config["host"]
            self.port = config["port"]
            self.maxLength = config["最长对话轮数"]


baiChuanConfig = BaiChuanConfig()
