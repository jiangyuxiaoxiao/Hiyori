"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/3-18:27
@Desc: 市场插件用异常
@Ver : 1.0.0
"""


class MarketException(Exception):
    """市场基类异常"""
    pass


class MoneyNotEnoughException(MarketException):
    """金钱不够异常"""

    def __init__(self, own: float, need: float):
        self.ExceptInfo = f"金币不够，当前金币{own}，需要{need}。"

    def __str__(self):
        return self.ExceptInfo

