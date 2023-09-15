"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:35
@Desc: Hiyori背包
@Ver : 1.0.0
"""
import peewee

from .config import DB

Hiyori = peewee.SqliteDatabase(DB)


# 用户物品表
class Item(peewee.Model):
    QQ = peewee.IntegerField(index=True, null=False)
    Item = peewee.TextField(index=True, null=False)
    Quantity = peewee.IntegerField(default=0, null=False)
    # Decimal表示物品的小数点位数，存放时均以整数存放。实际数值除以具体位数
    Decimal = peewee.IntegerField(default=0, null=False)

    class Meta:
        database = Hiyori
        table_name = "Item"
        primary_key = peewee.CompositeKey("QQ", "Item")


# 方法类
class DB_Item:
    # 模块初始化函数
    @staticmethod
    def itemInit():
        """模块初始化函数，通常一次运行只调用一次。"""
        # 若表不存在，则先创建
        Item.create_table(safe=True)

    @staticmethod
    def getUserItemALL(QQ: int) -> list[Item]:
        """
        按QQ号获取用户物品数据

        :param QQ: QQ号
        :return: 用户的物品列表
        """
        result = Item.select().where(Item.QQ == QQ)
        return result

    @staticmethod
    def getUserItem(QQ: int, ItemName: str) -> Item:
        """
        按QQ号与物品名获取对应物品数据，若不存在则先创建

        :param QQ: QQ号
        :param ItemName: 物品名称
        :return: 物品
        """
        result = Item.select().where((Item.QQ == QQ) & (Item.Item == ItemName))
        if len(result) == 0:
            # 没有则创建对应记录
            return Item.create(QQ=QQ, Item=ItemName, Quantity=0)
        else:
            return result[0]

    @staticmethod
    def hasItem(QQ: int, ItemName: str) -> bool:
        """
        判断用户是否持有对应物品，若持有则返回True

        :param QQ: QQ号
        :param ItemName: 物品名称
        :return: 是否持有
        """
        item = DB_Item.getUserItem(QQ, ItemName)
        if item.Quantity == 0:
            return False
        return True
