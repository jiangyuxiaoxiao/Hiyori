"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:37
@Desc: Hiyori用户
@Ver : 1.0.0
"""
import time

import peewee
from nonebot import get_driver
from nonebot.log import logger
from nonebot import get_bots
from nonebot.adapters.onebot.v11 import Bot
import sys

from .config import DB

Hiyori = peewee.SqliteDatabase(DB)


# 用户数据表
class User(peewee.Model):
    QQ = peewee.IntegerField(primary_key=True, index=True, null=False)
    Name = peewee.TextField(default="")
    NickName = peewee.TextField(default="")
    Permission = peewee.IntegerField(default=2, null=False,
                                     constraints=[peewee.Check('Permission IN (0,1,2,3)')])
    Attitude = peewee.IntegerField(default=0, index=True, null=False)
    Money = peewee.IntegerField(default=0, null=False,
                                constraints=[peewee.Check('Money >= 0')])
    CD = peewee.IntegerField(default=10, null=False,
                             constraints=[peewee.Check('CD >= 0')])
    SignInDate = peewee.TextField(default="")

    class Meta:
        database = Hiyori
        table_name = "User"


# 群组数据表
class Group(peewee.Model):
    GroupID = peewee.IntegerField(primary_key=True, index=True, null=False)
    GroupName = peewee.TextField(default="")
    Permission = peewee.IntegerField(default=3, null=False,
                                     constraints=[peewee.Check('Permission IN (0,1,2,3)')])
    Status = peewee.TextField(default="on", null=False)
    CD = peewee.IntegerField(default=30, null=False,
                             constraints=[peewee.Check('CD >= 0')])

    class Meta:
        database = Hiyori
        table_name = "Group"


Users_Memory: dict[int, User] = dict()
Groups_Memory: dict[int, Group] = dict()


# 方法类
class DB_User:
    # 模块初始化函数
    @staticmethod
    def userInit():
        superusers = get_driver().config.superusers
        """模块初始化函数，通常一次运行只调用一次。"""
        # 载入全局变量
        global Users_Memory, Groups_Memory
        # 避免重复加载 先清空
        Users_Memory.clear()
        Groups_Memory.clear()
        # 若表不存在，则先创建
        User.create_table(safe=True)
        Group.create_table(safe=True)
        # 获取全部数据
        usersInfo = User.select()
        groupsInfo = Group.select()
        # 将所有信息存入内存
        for userInfo in usersInfo:
            Users_Memory[userInfo.QQ] = userInfo
        for groupInfo in groupsInfo:
            Groups_Memory[groupInfo.GroupID] = groupInfo
        # 超管权限同步
        for superuser in superusers:
            if superuser.isdigit():
                user = DB_User.getUser(int(superuser))
                if user.Permission != 0:
                    user.Permission = 0
                    DB_User.updateUser(user)
                    logger.success(f"根据SUPERUSER配置信息，已将用户{superuser}提升为HIYORI_OWNER")

        Memory = sys.getsizeof(Users_Memory) + sys.getsizeof(Groups_Memory)
        Memory = round(Memory / (1024 * 1024), 3)
        logger.success(
            "已载入{}条用户信息, {}条群组信息, 占用内存{}MB".format(len(Users_Memory), len(Groups_Memory), Memory))

    # 刷新全部用户
    # 遍历全部群与好友，将更新数据存入数据库与内存
    # 对于数据库与内存而言皆为增量更新，当有用户被移除时（退群，删好友）并不会移除对应的数据
    @staticmethod
    async def refreshAll():
        """从QQ服务器拉取刷新全部用户进数据库与内存。载入方式为增量载入，不会删除数据库中已删除的值，只进行更新或者添加"""
        # 载入全局变量
        global Users_Memory, Groups_Memory
        startTime = time.time_ns()
        userInsertCount = userUpdateCount = 0
        groupInsertCount = groupUpdateCount = 0
        bots: dict[str, Bot] = get_bots()
        for bot in bots.values():
            updateGroups: set = set()
            # 获取群列表
            groups = await bot.call_api("get_group_list", **{"no_cache": True})
            for group in groups:
                # group_id 群号
                GroupID = group["group_id"]
                # 跳过重复加载项
                if GroupID in updateGroups:
                    continue
                else:
                    updateGroups.add(GroupID)
                # group_name 群名
                GroupName = group["group_name"]
                # 群更新
                if GroupID not in Groups_Memory:
                    groupInsertCount = groupInsertCount + 1
                    # 更新数据库与内存
                    Groups_Memory[GroupID] = Group.create(GroupID=GroupID, GroupName=GroupName)
                else:
                    # 检查群名是否变更
                    if Groups_Memory[GroupID].GroupName != GroupName:
                        groupUpdateCount = groupUpdateCount + 1
                        Groups_Memory[GroupID].GroupName = GroupName
                        Groups_Memory[GroupID].save()
                # 群用户更新
                groupMembers = await bot.call_api("get_group_member_list", **{"group_id": GroupID, "no_cache": True})
                with Hiyori.atomic():
                    for groupMember in groupMembers:
                        QQ = groupMember["user_id"]
                        Name = groupMember["nickname"]
                        if QQ not in Users_Memory:
                            userInsertCount = userInsertCount + 1
                            # 更新数据库与内存
                            Users_Memory[QQ] = User.create(QQ=QQ, Name=Name)
                        else:
                            # 检查用户名是否变更
                            if Users_Memory[QQ].Name != Name:
                                userUpdateCount = userUpdateCount + 1
                                Users_Memory[QQ].Name = Name
                                Users_Memory[QQ].save()
            # 获取好友列表
            users = await bot.get_friend_list()
            with Hiyori.atomic():
                for user in users:
                    QQ = user["user_id"]
                    Name = user["nickname"]
                    if QQ not in Users_Memory:
                        userInsertCount = userInsertCount + 1
                        # 更新数据库与内存
                        Users_Memory[QQ] = User.create(QQ=QQ, Name=Name)
                    else:
                        # 检查用户名是否变更
                        if Users_Memory[QQ].Name != Name:
                            userUpdateCount = userUpdateCount + 1
                            Users_Memory[QQ].Name = Name
                            Users_Memory[QQ].save()
        # 输出统计信息
        endTime = time.time_ns()
        Time = (endTime - startTime) / 1000000
        Memory = round(sys.getsizeof(Users_Memory) / (1024 * 1024), 3)
        logger.success("已更新所有用户信息，新加载用户数{}, 新加载群组数{}, 更新用户数{}, 更新群组数{}, 用时{}ms, 总占用内存{}MB"
                       .format(userInsertCount, groupInsertCount, userUpdateCount, groupUpdateCount, Time, Memory))

    # 重新载入数据库
    @staticmethod
    def reload():
        """重新载入数据库，将数据库重新载入内存中。载入方式为增量载入，不会删除数据库中已删除的值，只进行更新或者添加"""
        # 载入全局变量
        global Users_Memory, Groups_Memory
        startTime = time.time_ns()
        # 获取全部数据
        usersInfo = User.select()
        groupsInfo = Group.select()
        # 将所有信息存入内存
        for userInfo in usersInfo:
            Users_Memory[userInfo.QQ] = userInfo
        for groupInfo in groupsInfo:
            Groups_Memory[groupInfo.GroupID] = groupInfo

        Memory = sys.getsizeof(Users_Memory) + sys.getsizeof(Groups_Memory)
        Memory = round(Memory / (1024 * 1024), 3)
        endTime = time.time_ns()
        Time = round((endTime - startTime) / 1000000, 3)
        logger.success(
            "已重新载入{}条用户信息, {}条群组信息, 用时{}ms, 占用内存{}MB".format(len(Users_Memory), len(Groups_Memory),
                                                                                  Time, Memory))

    # 检查数据库中是否存在对应用户，不存在则更新对应用户
    @staticmethod
    def userExist(QQ: int):
        """检查数据库中是否存在对应用户，不存在则更新写入对应用户"""
        # 载入全局变量
        global Users_Memory
        if QQ not in Users_Memory:
            result = User.select().where(User.QQ == QQ)
            if len(result) == 0:
                Users_Memory[QQ] = User.create(QQ=QQ)

    # 检查数据库中是否存在对应群组，不存在则更新对应群组
    @staticmethod
    def groupExist(GroupID: int):
        """检查数据库中是否存在对应群组，不存在则更新写入对应群组"""
        # 载入全局变量
        global Groups_Memory
        if GroupID not in Groups_Memory:
            result = Group.select().where(Group.GroupID == GroupID)
            if len(result) == 0:
                Groups_Memory[GroupID] = Group.create(GroupID=GroupID)

    # 检查数据库中是否存在对应用户，不存在也不更新
    @staticmethod
    def hasUser(QQ: int) -> bool:
        """检查数据库中是否存在对应用户，不存在不进行更新"""
        # 载入全局变量
        global Users_Memory
        if QQ not in Users_Memory:
            result = User.select().where(User.QQ == QQ)
            if len(result) == 0:
                return False
        return True

    # 检查数据库中是否存在对应群组，不存在也不更新
    @staticmethod
    def hasGroup(GroupID: int) -> bool:
        """检查数据库中是否存在对应群组，不存在不进行更新"""
        # 载入全局变量
        global Groups_Memory
        if GroupID not in Groups_Memory:
            result = Group.select().where(Group.GroupID == GroupID)
            if len(result) == 0:
                return False
        return True

    # 获取用户
    @staticmethod
    def getUser(QQ: int) -> User:
        """获取用户，不存在则会先创建对应用户"""
        # 载入全局变量
        global Users_Memory
        DB_User.userExist(QQ)
        return Users_Memory[QQ]

    # 获取全部用户内存字典
    @staticmethod
    def getAllUsers() -> dict:
        """返回用户内存字典"""
        return Users_Memory

    # 获取群组
    @staticmethod
    def getGroup(GroupID: int) -> Group:
        """获取群组，不存在则会先创建对应群组"""
        # 载入全局变量
        global Groups_Memory
        DB_User.groupExist(GroupID)
        return Groups_Memory[GroupID]

    # 获取全部群组内存字典
    @staticmethod
    def getAllGroups() -> dict:
        """返回群组内存字典"""
        return Groups_Memory

    # 更新用户
    @staticmethod
    def updateUser(user: User):
        """更新用户 (内存与数据库都会更新)"""
        # 载入全局变量
        global Users_Memory
        Users_Memory[user.QQ] = user
        user.save()

    # 更新群组
    @staticmethod
    def updateGroup(group: Group):
        """更新群组 (内存与数据库都会更新)"""
        # 载入全局变量
        global Groups_Memory
        Groups_Memory[group.GroupID] = group
        group.save()

    # 是主人
    @staticmethod
    def isOwner(QQ: int) -> bool:
        """Permission=0"""
        # 载入全局变量
        global Users_Memory
        DB_User.userExist(QQ)
        if Users_Memory[QQ].Permission == 0:
            return True
        return False

    # 是管理员 (权限大于等于1)
    @staticmethod
    def isAdmin(QQ: int) -> bool:
        """Permission=0或1"""
        # 载入全局变量
        global Users_Memory
        DB_User.userExist(QQ)
        if Users_Memory[QQ].Permission in (0, 1):
            return True
        return False

    # 货币消费
    @staticmethod
    def spendMoney(QQ: int, Money: float) -> bool:
        """
        消费对应账户的金币，不成功则返回False。金币的最小单位为0.01，小于0.01的将被抹去

        :param QQ: QQ号
        :param Money: 消费金额
        :return: 是否成功消费
        """

        user = DB_User.getUser(QQ=QQ)
        if user.Money < Money * 100:
            return False
        else:
            user.Money = int(user.Money - Money * 100)
            DB_User.updateUser(user)
            return True

    @staticmethod
    def banGroup(GroupID: int):
        """封禁对应群聊"""
        g = DB_User.getGroup(GroupID)
        g.Permission = 3
        DB_User.updateGroup(g)

    @staticmethod
    def banUser(QQ: int):
        """封禁对应用户"""
        u = DB_User.getUser(QQ)
        u.Permission = 3
        DB_User.updateUser(u)
