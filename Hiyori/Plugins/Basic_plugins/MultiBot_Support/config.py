"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/4-8:58
@Desc: 配置函数，注意，在本插件实现中，QQ与GroupID均为str类型
@Ver : 1.0.0
"""
import json
import os
from Hiyori.Utils.File import JsonFileExist, DirExist
from Hiyori.Utils.Config import Config

ConfigPath = "./Config/MultiBot_Support/config.json"
ConfigDir = os.path.dirname(ConfigPath)


class MultiBotConfig(Config):
    """单例类 MultiBotConfig\n
    在配置文件中的保存格式： \n
    {
        "默认优先顺序":["1234","1235"],  \n
        "群组规则":{
            "1234588":"1234",  \n
            "762183":"1235"  \n
        }
    }
    """

    def __init__(self):
        initContent = {
            "默认优先顺序": [],
            "群组规则": {
            }
        }
        DirExist(ConfigDir)
        JsonFileExist(Path=ConfigPath, initContent=initContent, logEnable=True, logInfo="【多Bot连接支持插件】配置文件不存在，正在创建中。")
        with open(file=ConfigPath, mode="r", encoding="utf-8") as file:
            config = json.loads(file.read())
            self.priority: list[str] = config["默认优先顺序"]
            self.rule: dict[str, str] = config["群组规则"]
            self.groupSet: dict[str, set[str]] = {}  # 检查对应Bot是否在群组中，key=Bot_QQ, value=群组set
            self.activeBots: set[str] = set()  # 检查对应Bot是否已注册成功

    def dump(self):
        """导出到配置文件中"""
        with open(file=ConfigPath, mode="w", encoding="utf-8") as file:
            content = {
                "默认优先顺序": self.priority,
                "群组规则": self.rule
            }
            file.write(json.dumps(content, ensure_ascii=False, indent=2))

    def load(self):
        """从配置文件中导入"""
        initContent = {
            "默认优先顺序": [],
            "群组规则": {
            }
        }
        JsonFileExist(Path=ConfigPath, initContent=initContent, logEnable=True, logInfo="【多Bot连接支持插件】群组规则不存在，正在创建中。")
        with open(file=ConfigPath, mode="r", encoding="utf-8") as file:
            config = json.loads(file.read())
            self.priority: list[str] = config["默认优先顺序"]
            self.rule: dict[str, str] = config["群组规则"]


multiBotConfig: MultiBotConfig = MultiBotConfig()
