"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:36
@Desc: Hiyori群友市场
@Ver : 1.0.0
"""
import peewee

from .config import DB

Hiyori = peewee.SqliteDatabase(DB)


# 买卖市场个人信息表
class Slave(peewee.Model):
    QQ = peewee.IntegerField(index=True, null=False)
    Group = peewee.IntegerField(index=True, null=False)
    Price = peewee.IntegerField(default=100, null=False)
    Owner = peewee.IntegerField(default=0, null=False)
    Skill = peewee.TextField(default="{}", null=False)
    Experience = peewee.TextField(default="", null=False)
    PurchaseTime = peewee.IntegerField(default=0, null=False)
    LastPurchase = peewee.TextField(default="", null=False)
    Extra = peewee.TextField(default="{}", null=False)

    class Meta:
        database = Hiyori
        table_name = "Slave"
        primary_key = peewee.CompositeKey("QQ", "Group")


# 方法类
class DB_slave:
    # 模块初始化函数
    @staticmethod
    def slaveInit():
        Slave.create_table(safe=True)

    # 获取个人信息
    @staticmethod
    def getUser(QQ: int, GroupID: int) -> Slave:
        """
        获取个人信息

        :param GroupID: 群号
        :param QQ: QQ号
        :return: 买卖市场个人信息
        """
        result = Slave.select().where((Slave.QQ == QQ) & (Slave.Group == GroupID))
        if len(result) == 0:
            # 没有则创建记录
            return Slave.create(QQ=QQ, Group=GroupID)
        return result[0]

    # 获取群内所有信息
    @staticmethod
    def getAllUsers(GroupID: int) -> list[Slave]:
        """
        获取群内所有信息

        :param GroupID: 群号
        :return: 群内所有信息列表
        """
        return Slave.select().order_by(Slave.Price.desc()).where(Slave.Group == GroupID)[:]

    # 获取对应主人的所有奴隶信息
    @staticmethod
    def getSlaves(QQ: int, GroupID: int) -> list[Slave]:
        """
        获取对应主人的所有奴隶信息

        :param QQ: QQ号
        :param GroupID: 群号
        :return: 所属奴隶列表
        """
        result = Slave.select().order_by(Slave.Price.desc()).where((Slave.Owner == QQ) & (Slave.Group == GroupID))
        return result[:]
