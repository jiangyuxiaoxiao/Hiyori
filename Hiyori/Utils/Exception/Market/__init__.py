"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/3-18:27
@Desc: 市场插件用异常
@Ver : 1.0.0
"""


class MarketException(BaseException):
    """市场基类异常"""

    def __str__(self):
        return ""


class MoneyNotEnoughException(MarketException):
    """金钱不够异常"""

    def __init__(self, own: float = 0, need: float = 0):
        self.ExceptInfo = f"金币不够，当前金币{own}，需要{need}。"

    def __str__(self):
        return self.ExceptInfo


class AttitudeNotEnoughException(MarketException):
    """好感度不够异常"""

    def __init__(self, now: int = 0, need: int = 0):
        self.ExceptInfo = f"好感度不够，当前{now}，需要{need}。"

    def __str__(self):
        return self.ExceptInfo


class NoTargetException(MarketException):
    """缺少使用对象异常"""

    def __init__(self):
        self.ExceptInfo = f"需要指定使用对象"

    def __str__(self):
        return self.ExceptInfo


class ItemNotEnoughException(MarketException):
    """物品数量不足"""

    def __init__(self, now: int = 0, need: int = 0):
        self.ExceptInfo = f"物品数量不足，当前{now}个物品，需要{need}。"

    def __str__(self):
        return self.ExceptInfo


class ItemNumNotCorrectException(MarketException):
    """物品数量不正确"""

    def __init__(self):
        self.ExceptInfo = f"物品使用数量不正确"

    def __str__(self):
        return self.ExceptInfo


class TypeErrorException(MarketException):
    """触发时依赖注入错误"""

    def __init__(self):
        self.ExceptInfo = f"触发时依赖注入错误"

    def __str__(self):
        return self.ExceptInfo


class UsageNotCorrectException(MarketException):
    """物品用法不正确"""

    def __init__(self):
        self.ExceptInfo = f"物品用法不正确"

    def __str__(self):
        return self.ExceptInfo


class UniqueItemException(MarketException):
    """唯一物品不可重复购买"""

    def __init__(self):
        self.ExceptInfo = f"唯一物品不可重复购买。"

    def __str__(self):
        return self.ExceptInfo
