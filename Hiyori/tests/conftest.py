"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/12-16:23
@Desc: 测试配置文件
@Ver : 1.0.0
"""

import pytest
import sys
import json
import time
import os

import nonebot
from nonebot.log import logger
from nonebot.plugin import _plugins
from nonebot.adapters.onebot.v11 import Adapter

from Hiyori.Utils.File import DirExist

os.environ["ENVIRONMENT"] = "test"


@pytest.fixture(scope="session", autouse=True)
def load_bot():
    # 加载适配器
    driver = nonebot.get_driver()
    driver.register_adapter(Adapter)

    # 加载插件
    # 插件目录加载进环境变量
    sys.path.append("../")
    sys.path.append("./Plugins/Basic_plugins")  # 底层实现插件，管理类插件，请在加载时置于最顶层
    sys.path.append("./Plugins/Debug_plugins")  # 调试插件
    sys.path.append("./Plugins/Nonebot_plugins")  # nonebot社区插件
    sys.path.append("./Plugins/Normal_plugins")  # 普通功能插件
    sys.path.append("./Plugins/Personal_plugins")  # 私人插件
    sys.path.append("./Plugins/Market_plugins")  # 市场插件
    sys.path.append("./Plugins/AI_plugins")  # AI生成插件
    sys.path.append("./Plugins/Web_plugins")  # 后端插件
    sys.path.append("./Plugins/Zao_plugins")  # zao插件
    # 根据初始化配置选择插件目录配置文件进行初始化
    # 默认配置文件路径为./plugin.dev.json
    # 根据在.env中的环境设置，进行更新
    configDict = driver.config.dict()
    if "environment" not in configDict.keys():
        plugin_dir = "plugin.dev.json"
    else:
        environment = configDict["environment"]
        plugin_dir = "plugin." + environment + ".json"

    with open(plugin_dir, encoding="utf-8") as plg_dir:
        plugins = json.load(plg_dir)
        plugins = plugins["Plugin"]["Dir"]
        for plugin in plugins:
            time1 = time.time_ns()
            nonebot.load_plugin(plugin)
            time2 = time.time_ns()
            plugin_time = (time2 - time1) / 1000000000
            plugin_time = round(plugin_time, 3)
            logger.info(f"插件{plugin}加载用时{plugin_time}s")

    # 插件加载完毕后，加载meta.json
    # 加载测试环境配置文件
    metaDir = "Config/TestConfig"
    configInitFlag = False
    for plugin_name, plugin in _plugins.items():
        metaPath = os.path.join(metaDir, plugin_name, "Metadata.json")
        # json文件不存在，进行初始化
        if not os.path.isfile(metaPath) or configInitFlag:
            if plugin.metadata is None:
                # 不进行初始化
                logger.debug(f"插件{plugin_name}不存在metaData，不写入配置文件。")
            else:
                # 设置默认配置
                extra = plugin.metadata.extra
                jsonDict = {
                    "extra": extra
                }
                DirExist(os.path.join(metaDir, plugin_name))
                with open(file=metaPath, mode="w", encoding="utf-8") as metaFile:
                    metaFile.write(json.dumps(jsonDict, ensure_ascii=False, indent=4))
        # json文件存在，根据json文件修改metaData的extraInfo
        else:
            with open(file=metaPath, mode="r", encoding="utf-8") as metaFile:
                info = metaFile.read()
                info = json.loads(info)
                if info["extra"] is not None:
                    plugin.metadata.extra = info["extra"]
