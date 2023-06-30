"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:35
@Desc: Hiyori数据库封装
@Ver : 1.0.0
"""
import time
from nonebot.log import logger

# 包内依赖
from .user import DB_User
from .item import DB_Item
from .slaveMarket import DB_slave
from .spot import DB_Spot
# 数据库初始化
startTime = time.time_ns()
logger.info("数据库初始化载入缓存")

# 读入用户数据
DB_User.userInit()
DB_Item.itemInit()
DB_slave.slaveInit()
DB_Spot.spotInit()
endTime = time.time_ns()
Time = round((endTime - startTime) / 1000000, 3)

logger.success("数据库加载用时{}ms".format(Time))