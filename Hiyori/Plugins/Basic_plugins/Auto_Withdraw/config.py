"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/30-21:35
@Desc: 相关配置
@Ver : 1.0.0
"""
import os
import json
from Hiyori.Utils.File import DirExist, JsonFileExist
from Hiyori.Utils.Config import Config

ConfigPath = "./Config/Auto_Withdraw/config.json"
ConfigDir = os.path.dirname(ConfigPath)


class AutoWithdrawConfig(Config):

    def __init__(self):
        initContent: dict = {
            "默认撤回时间": 60,
            "最长撤回时间": 110,
            "群组默认开启": False,
            "群组撤回配置": {
                "111": {
                    "on": True,
                    "time": 70
                }
            },
        }
        DirExist(ConfigDir)
        JsonFileExist(Path=ConfigPath, initContent=initContent, logEnable=True, logInfo="【定时撤回插件】配置文件不存在，正在创建中。")
        with open(file=ConfigPath, mode="r", encoding="utf-8") as file:
            config = json.loads(file.read())
            self.defaultWithdrawTime: int = config["默认撤回时间"]
            self.maxWithdrawTime: int = config["最长撤回时间"]
            self.defaultOn: bool = config["群组默认开启"]
            self.groupConfig: dict[str, dict[str, any]] = config["群组撤回配置"]

    def dump(self):
        """导出配置到配置文件中"""
        with open(file=ConfigPath, mode="w", encoding="utf-8") as file:
            content = {
                "默认撤回时间": self.defaultWithdrawTime,
                "最长撤回时间": self.maxWithdrawTime,
                "群组默认开启": self.defaultOn,
                "群组撤回配置": self.groupConfig,

            }
            file.write(json.dumps(content, ensure_ascii=False, indent=2))

    def load(self):
        """从配置文件中导入配置"""
        initContent: dict = {
            "默认撤回时间": 60,
            "最长撤回时间": 110,
            "群组默认开启": False,
            "群组撤回配置": {},
        }
        DirExist(ConfigDir)
        JsonFileExist(Path=ConfigPath, initContent=initContent, logEnable=True, logInfo="【定时撤回插件】配置文件不存在，正在创建中。")
        with open(file=ConfigPath, mode="r", encoding="utf-8") as file:
            config = json.loads(file.read())
            self.defaultWithdrawTime: int = config["默认撤回时间"]
            self.maxWithdrawTime: int = config["最长撤回时间"]
            self.defaultOn: bool = config["群组默认开启"]
            self.groupConfig: dict[str, bool] = config["群组撤回配置"]


autoWithdrawConfig: AutoWithdrawConfig = AutoWithdrawConfig()
