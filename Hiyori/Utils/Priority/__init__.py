"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:48
@Desc: Hiyori推荐优先级默认设置
@Ver : 1.0.0
"""
from enum import IntEnum


class Priority(IntEnum):
    P0 = 0  # 基础系统插件
    系统优先级 = 0

    P1 = 10  # 高优先级插件
    高优先级 = 10

    P2 = 20  # 普通插件
    普通优先级 = 20

    P3 = 30  # 泛用匹配插件
    低优先级 = 30
