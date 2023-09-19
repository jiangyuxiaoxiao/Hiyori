"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:35
@Desc: Hiyori数据库封装
@Ver : 1.0.0
"""
import time
import sqlite3
from nonebot.log import logger

# 包内依赖
from .user import DB_User
from .item import DB_Item
from .slaveMarket import DB_slave
from .spot import DB_Spot
from .config import DB, path, MsgDB
from .message import DB_Message
from .hook import updateUser
# Hiyori API 调用
from Hiyori.Utils.File import DirExist

# 数据库初始化
startTime = time.time_ns()
logger.info("数据库初始化载入缓存")

Exist = DirExist(path)  # 若不存在文件夹路径则创建
if not Exist:
    logger.info("检查到数据库/Database/Hiyori.db不存在，正在创建数据库。")
conn = sqlite3.connect(database=DB)  # 若不存在数据库文件则创建
conn.close()
conn = sqlite3.connect(database=MsgDB)  # 若不存在数据库文件则创建
conn.close()
# 读入用户数据
DB_User.userInit()
DB_Item.itemInit()
DB_slave.slaveInit()
DB_Spot.spotInit()
DB_Message.messageInit()
endTime = time.time_ns()
Time = round((endTime - startTime) / 1000000, 3)

logger.success("数据库加载用时{}ms".format(Time))
