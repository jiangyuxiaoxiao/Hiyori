"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/8-10:14
@Desc: 配置文件
@Ver : 1.0.0
"""
import json
import os
from Hiyori.Utils.Config import Config

from Hiyori.Utils.File import JsonFileExist, DirExist
from Hiyori.Utils.Config import Config


class TranslatorConfig(Config):
    ConfigPath = "./Data/Translator/config.json"

    def __init__(self):
        DirExist(os.path.dirname(self.ConfigPath))
        initContent = {}
        JsonFileExist(Path=self.ConfigPath, initContent=initContent, logEnable=True, logInfo="【翻译插件】配置文件不存在，正在创建中。")
        with open(file=self.ConfigPath, mode="r", encoding="utf-8") as file:
            self.config = json.loads(file.read())

    def dump(self):
        """导出到配置文件中"""
        with open(file=self.ConfigPath, mode="w", encoding="utf-8") as file:
            file.write(json.dumps(self.config))

    def load(self):
        """从配置文件中导入"""
        with open(file=self.ConfigPath, mode="r", encoding="utf-8") as file:
            self.config = json.loads(file.read())


translatorConfig = TranslatorConfig()
