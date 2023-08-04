"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/3-18:06
@Desc: 重构物品类
@Ver : 1.0.0
"""
from Hiyori.Utils.Database.item import Item, DB_Item
from Hiyori.Utils.Database import DB_User
from .BasicFunction import 折扣系数计算


# 商品
class ShopItem:
    def __init__(self, name: str, description: str = "", price: float = 10000,
                 hasTarget: bool = False, need_attitude: int = 0, anonymous: bool = False):
        self.name = name  # 商品名
        self.description = description  # 商品描述
        self.price = price  # 商品价格，注意价格的最小单位为0.01，小于0.01的值将被抹去
        self.hasTarget = hasTarget  # 有作用对象
        self.need_attitude = need_attitude  # 购买有好感度需求
        self.anonymous = anonymous  # 隐式商品

    def beforePurchase(self):
        pass

    def Purchase(self, QQ: int, Num: int):
        """ 购买函数 """

        # 购买价格修正
        money = self.price * 折扣系数计算(QQ=QQ, ItemName=self.name) * Num
        DB_User.spendMoney(QQ=QQ, Money=money)

        # 花费

    def afterPurchase(self):
        pass

    def beforeUse(self):
        pass

    def Use(self):
        pass

    def afterUse(self):
        pass

    def dailyEffect(self):
        pass
