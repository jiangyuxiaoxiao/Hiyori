"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:45
@Desc: 商店功能封装
@Ver : 1.0.0
"""
from Hiyori.Utils.Database import DB_User, DB_Item


# 商品
class Item:
    def __init__(self, name: str, description: str = "", price: float = 10000, functions: dict[str, any] = None,
                 hasTarget: bool = False, need_attitude: int = 0, anonymous: bool = False):
        if functions is None:
            functions = dict()
        self.name = name  # 商品名
        self.description = description  # 商品描述
        self.price = price  # 商品价格，注意价格的最小单位为0.01，小于0.01的值将被抹去
        self.Functions = functions  # 商品传入函数
        self.hasTarget = hasTarget  # 有作用对象
        self.need_attitude = need_attitude  # 购买有好感度需求
        self.anonymous = anonymous  # 隐式商品


# 商店
class Shop:
    def __init__(self, name: str, description: str = "", anonymous: bool = False):
        self.name = name  # 商店名
        self.description = description  # 商店描述
        self.items: dict[str, Item] = dict()
        self.anonymous = anonymous  # 隐式商店

    # 添加商品
    def addItem(self, itemName: str, description: str = "", price: float = 10000, functions: dict[str, any] = None,
                hasTarget: bool = False, need_attitude: int = 0, anonymous: bool = False):
        self.items[itemName] = Item(name=itemName, description=description, price=price, functions=functions,
                                    hasTarget=hasTarget, need_attitude=need_attitude, anonymous=anonymous)

    """
    def buyItem(self, itemName: str, QQ: int, quantity: int = 1) -> str:
        item = self.items[itemName]
        # 检查钱够不够
        if not DB_User.spendMoney(QQ, quantity * item.price):
            return "托莉币不足"
        # 检查好感度
        User = DB_User.getUser(QQ)
        if User.Attitude < item.need_attitude:
            return "好感度不足"
        userItem = DB_Item.getUserItem(QQ=QQ, ItemName=itemName)
        userItem.Quantity += quantity
        userItem.save()
        return "购买成功"
    """


# 总商店
class Shops:
    shops: dict[str, Shop] = dict()
    items: dict[str, Item] = dict()

    # 添加商店
    @staticmethod
    def addShop(shop: Shop):
        Shops.shops[shop.name] = shop
        # 将物品添加进总物品表中
        for item in shop.items.values():
            Shops.items[item.name] = item
