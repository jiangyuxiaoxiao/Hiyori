"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:46
@Desc: 商店物品通用功能函数
@Ver : 1.0.0
"""
from Hiyori.Utils.Database import DB_Item


def 唯一物品(QQ: int, GroupID: int, Quantity: int, **kwargs) -> (bool, str):
    if "ItemName" not in kwargs.keys():
        return False, "【error】未传入物品名"
    ItemName = kwargs["ItemName"]
    Item = DB_Item.getUserItem(QQ=QQ, ItemName=ItemName)
    if Item.Quantity != 0:
        return False, "唯一性物品不能重复购买"
    if Quantity != 1:
        return False, "唯一性物品不能购买多个"
    return True, ""
