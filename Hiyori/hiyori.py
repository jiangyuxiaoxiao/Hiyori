"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:15
@Desc: 
@Ver : 1.0.0
"""
import nonebot
import json
import sys
import time
import os
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.plugin import _plugins
from datetime import datetime

from Utils.File import DirExist

# 程序开始时间
startTime = time.time_ns()

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

# 初始化nonebot
nonebot.init()
app = nonebot.get_asgi()

# 连接驱动
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

configDict = driver.config.dict()
if "save_log_level" not in configDict.keys():
    save_log_level = "ERROR"
else:
    save_log_level = configDict["save_log_level"]
if not os.path.isdir("Log"):
    os.makedirs("Log")
now = datetime.now().strftime("%Y-%m-%d")
logger.add(f"Log/Hiyori.log", level=save_log_level, rotation="1 days", retention="14 days")

# 根据初始化配置选择插件目录配置文件进行初始化
# 默认配置文件路径为./plugin.dev.json
# 根据在.env中的环境设置，进行更新
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
metaDir = "Config"
for plugin_name, plugin in _plugins.items():
    metaPath = os.path.join(metaDir, plugin_name, "Metadata.json")
    # meta不存在，不进行初始化
    if plugin.metadata is None:
        # 不进行初始化
        logger.debug(f"插件{plugin_name}不存在metaData，不写入配置文件。")
        continue
    # 插件配置
    plugin_extra = plugin.metadata.extra
    jsonDict = {
        "extra": plugin_extra,
        "WARNING": "请勿更改下划线开头的变量数值！",
        "_extra": plugin_extra
    }
    # json文件不存在，进行初始化
    if not os.path.isfile(metaPath):
        DirExist(os.path.join(metaDir, plugin_name))
        with open(file=metaPath, mode="w", encoding="utf-8") as metaFile:
            metaFile.write(json.dumps(jsonDict, ensure_ascii=False, indent=4))
    # json文件存在
    else:
        # 实现效果：
        # 若插件extra未更新，则以json文件为标准
        # 若插件extra更新，则以插件为准，并覆盖更新json文件所有字段
        with open(file=metaPath, mode="a+", encoding="utf-8") as metaFile:
            metaFile.seek(0)
            info = metaFile.read()
            info = json.loads(info)
            configInitFlag = False
            updateFlag = False
            if "extra" not in info or "_extra" not in info:
                configInitFlag = True
            else:
                config_extra = info["extra"]
                origin_extra = info["_extra"]
                # 比对插件的extra，与文件创建时的原始extra
                if origin_extra != plugin_extra:
                    updateFlag = True
                else:
                    plugin.metadata.extra = info["extra"]
            # 信息恢复
            if configInitFlag or updateFlag:
                infoMsg = f"插件{plugin_name}配置文件异常，正在恢复。" if configInitFlag else f"插件{plugin_name}配置已更新，重新写入配置文件。"
                logger.info(infoMsg)
                # 根据插件信息进行恢复
                info["extra"] = plugin.metadata.extra
                info["_extra"] = plugin.metadata.extra
                # 清空文件并重新写入
                metaFile.seek(0)
                metaFile.truncate()
                metaFile.write(json.dumps(jsonDict, ensure_ascii=False, indent=4))

# bot开始运行时间
endTime = time.time_ns()
Atri_time = (endTime - startTime) / 1000000000
Atri_time = round(Atri_time, 3)
plugin_number = len(_plugins.values())
logger.success(f"アトリは、高性能ですから！")
logger.success(f"启动用时{Atri_time}s，共加载插件{plugin_number}个。")
nonebot.run(app="__mp_main__:app")
