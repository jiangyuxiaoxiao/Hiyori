"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/12-17:05
@Desc: 数据库配置设置
@Ver : 1.0.0
"""
import nonebot

# 数据库默认路径
config = nonebot.get_driver().config
env = config.environment
path = "./Data/Database"
DB = "./Data/Database/Hiyori.db" if env != "test" else "./Data/Database/Hiyori-test.db"
MsgDB = "./Data/Database/Hiyori-Message.db" if env != "test" else "./Data/Database/Hiyori-Message-test.db"
