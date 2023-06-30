"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:55
@Desc: 群友技能
@Ver : 1.0.0
"""
from Hiyori.Utils.Database.slaveMarket import Slave
from Hiyori.Utils.Database import DB_User, DB_slave
from .Utils import SlaveUtils
from .workEvent import Jobs, Job
import datetime
import random


def ExecuteSkill(slave: Slave, skillName: str, slaveName: str, ownerName: str) -> str:
    # 检查是否拥有对应技能
    if skillName not in Skills.NormalSkills:
        slaveSkills = SlaveUtils.GetSkillInfo(slave)
        if (skillName not in slaveSkills) or (skillName not in Skills.SpecialSkills):
            return f"你的群友{slaveName}没有这个技能"
    result = eval(skillName + f"(slave,\"{slaveName}\",\"{ownerName}\")")
    return result


class Skills:
    NormalSkills: list = ["派去打黑工", "打工"]
    SpecialSkills: list = ["女装", "给我变"]


def 派去打黑工(slave: Slave, slaveName: str, ownerName: str) -> str:
    """
    需要在Extra字段中保存数据，数据格式如下\n
    "派去打黑工":{
        "lastTime": time
    }

    :param ownerName: 主人名
    :param slaveName: 奴隶名
    :param slave: 奴隶
    :return: 执行结果
    """
    Extra = SlaveUtils.GetExtraInfo(slave)
    Today = datetime.datetime.now()
    TodayStr = str(Today.year) + "-" + str(Today.month) + "-" + str(Today.day)

    # 检查是否已执行
    if "派去打黑工" not in Extra.keys():
        Extra["派去打黑工"] = dict()
        Extra["派去打黑工"]["lastTime"] = TodayStr + "@" + str(slave.Owner)
        SlaveUtils.SaveExtraInfo(slave, Extra)
    else:
        DayStr = Extra["派去打黑工"]["lastTime"]
        Owners = DayStr.split("@")
        if str(slave.Owner) in Owners and (TodayStr == Owners[0]):
            return f"{slaveName}今天已经打过黑工了，放过他吧"
        else:
            if TodayStr != Owners[0]:
                Extra["派去打黑工"]["lastTime"] = TodayStr + "@" + str(slave.Owner)
            else:
                Extra["派去打黑工"]["lastTime"] += "@" + str(slave.Owner)
            SlaveUtils.SaveExtraInfo(slave, Extra)
    EnableJobs: list = []
    for job in Jobs:
        if job.Enable(slave):
            EnableJobs.append(job)
    job = random.choice(EnableJobs)
    result, income = job.Execute(slave, slaveName)
    Owner = DB_User.getUser(slave.Owner)
    Owner.Money += income * 100
    DB_User.updateUser(Owner)
    return result


def 打工(slave: Slave, slaveName: str, ownerName: str) -> str:
    """
    需要在Extra字段中保存数据，数据格式如下\n
    "派去打黑工":{
        "lastTime": time
    }
    本函数即派去打黑工的兼容同名函数

    :param ownerName: 主人名
    :param slaveName: 奴隶名
    :param slave: 奴隶
    :return: 执行结果
    """
    return 派去打黑工(slave, slaveName, ownerName)


def 自由打工(slave: Slave, slaveName: str, job: Job) -> str:
    """
    需要在Extra字段中保存数据，数据格式如下\n
    "派去打黑工":{
        "lastTime": time
    }
    本函数为派去打黑工的拓展改写，

    :param owner:
    :param job: 工作
    :param slave: 用户
    :param slaveName: 用户名
    :return: 执行结果
    """
    Extra = SlaveUtils.GetExtraInfo(slave)
    Today = datetime.datetime.now()
    TodayStr = str(Today.year) + "-" + str(Today.month) + "-" + str(Today.day)

    # 检查是否已执行
    if "派去打黑工" not in Extra.keys():
        Extra["派去打黑工"] = dict()
        Extra["派去打黑工"]["lastTime"] = TodayStr + "@" + str(slave.Owner)
        SlaveUtils.SaveExtraInfo(slave, Extra)
    else:
        DayStr = Extra["派去打黑工"]["lastTime"]
        Owners = DayStr.split("@")
        if str(slave.QQ) in Owners and (TodayStr == Owners[0]):
            return f"你今天已经打过黑工了。"
        else:
            if TodayStr != Owners[0]:
                Extra["派去打黑工"]["lastTime"] = TodayStr + "@" + str(slave.QQ)
            else:
                Extra["派去打黑工"]["lastTime"] += "@" + str(slave.QQ)
            SlaveUtils.SaveExtraInfo(slave, Extra)
    if job.Enable(slave):
        result, income = job.Execute(slave, slaveName)
        User = DB_User.getUser(slave.QQ)
        User.Money += income * 100
        DB_User.updateUser(User)
        return result
    else:
        return "暂时不能胜任这份工作哦"
