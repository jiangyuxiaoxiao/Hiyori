"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/09/27-10:38
@Desc: 
@Ver : 1.0.0
"""
import os
import json
from Hiyori.Utils.File import JsonFileExist, DirExist
from Hiyori.Utils.Config import Config

ConfigPath = "./Config/Utils/API/BertVits.json"


class BertVitsConfig(Config):
    def __init__(self):
        initContent = {
            "host": "http://127.0.0.1",
            "port": 14010,
            "models": []
        }
        DirExist(os.path.dirname(ConfigPath))
        JsonFileExist(Path=ConfigPath, initContent=initContent, logEnable=True, logInfo="【BertVits支持】配置文件不存在，正在创建中。")
        with open(file=ConfigPath, mode="r", encoding="utf-8") as file:
            config = json.loads(file.read())
            self.host: str = config["host"]
            self.port: int = config["port"]
            self.models: list[dict] = config["models"]

    def dump(self):
        """导出到配置文件中"""
        with open(file=ConfigPath, mode="w", encoding="utf-8") as file:
            content = {
                "host": self.host,
                "port": self.port,
                "models": self.models
            }
            file.write(json.dumps(content, ensure_ascii=False, indent=2))

    def load(self):
        """从配置文件中导入"""
        initContent = {
            "host": "http://127.0.0.1",
            "port": 14010,
            "models": []
        }
        JsonFileExist(Path=ConfigPath, initContent=initContent, logEnable=True, logInfo="【BertVits支持】配置文件不存在，正在创建中。")
        with open(file=ConfigPath, mode="r", encoding="utf-8") as file:
            config = json.loads(file.read())
            self.host = config["host"]
            self.port = config["port"]
            self.models = config["models"]


bertVitsConfig = BertVitsConfig()
