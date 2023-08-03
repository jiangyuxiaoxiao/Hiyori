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
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.plugin import _plugins

# 程序开始时间
startTime = time.time_ns()

# 插件目录加载进环境变量
sys.path.append("../")
sys.path.append("./Plugins/Basic_plugins")  # 底层实现插件，管理类插件，请在加载时置于最顶层
sys.path.append("./Plugins/Debug_plugins")  # 调试插件
sys.path.append("./Plugins/Nonebot_plugins")  # nonebot社区插件
sys.path.append("./Plugins/Normal_Plugins")  # 普通功能插件
sys.path.append("./Plugins/Personal_plugins")  # 私人插件
sys.path.append("./Plugins/Market_plugins")  # 市场插件
sys.path.append("./Plugins/AI_plugins")  # AI生成插件
sys.path.append("./Plugins/API_plugins")  # 弃用
sys.path.append("./Plugins/Web_plugins")  # 后端插件
sys.path.append("./Plugins/Zao_plugins")  # zao插件

# 初始化nonebot
nonebot.init()
app = nonebot.get_asgi()

# 连接驱动
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

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

# bot开始运行时间
endTime = time.time_ns()
Atri_time = (endTime - startTime) / 1000000000
Atri_time = round(Atri_time, 3)
plugin_number = len(_plugins.values())
logger.success(f"アトリは、高性能ですから！")
logger.success(f"启动用时{Atri_time}s，共加载插件{plugin_number}个。")
nonebot.run(app="__mp_main__:app")
