"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:36
@Desc: Hiyori现货市场
@Ver : 1.0.0
"""
import peewee

from .config import DB

Hiyori = peewee.SqliteDatabase(DB)


# 现货仓库表
class Spot(peewee.Model):
    QQ = peewee.IntegerField(index=True, null=False)
    SpotName = peewee.TextField(index=True, null=False)
    Quantity = peewee.IntegerField(default=0, null=False)
    History = peewee.TextField(default="", null=False)

    class Meta:
        database = Hiyori
        table_name = "Spot"
        primary_key = peewee.CompositeKey("QQ", "SpotName")


# 方法类
class DB_Spot:
    # 模块初始化函数
    @staticmethod
    def spotInit():
        """模块初始化函数，通常一次运行只调用一次。"""
        # 若表不存在，则先创建
        Spot.create_table(safe=True)

    @staticmethod
    def getUserSpotALL(QQ: int) -> list[Spot]:
        """
        按QQ号获取用户现货数据

        :param QQ: QQ号
        :return: 用户的现货列表
        """
        result = Spot.select().where(Spot.QQ == QQ)
        return result

    @staticmethod
    def getUserSpot(QQ: int, SpotName: str) -> Spot:
        """
        按QQ号与物品名获取对应物品数据，若不存在则先创建

        :param QQ: QQ号
        :param SpotName: 现货名称
        :return: 现货信息
        """
        result = Spot.select().where((Spot.QQ == QQ) & (Spot.SpotName == SpotName))
        if len(result) == 0:
            # 没有则创建对应记录
            return Spot.create(QQ=QQ, SpotName=SpotName, Quantity=0)
        else:
            return result[0]
