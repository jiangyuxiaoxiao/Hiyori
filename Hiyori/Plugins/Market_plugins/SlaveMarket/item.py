"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:54
@Desc: 群友市场物品功能实现
@Ver : 1.0.0
"""
import time
from nonebot.adapters.onebot.v11 import Bot, Message
from Hiyori.Utils.Database import DB_User, DB_slave, DB_Item
from Hiyori.Utils.API.QQ import GetQQGrouperName, GetQQStrangerName
from .Utils import SlaveUtils
import numpy
from datetime import datetime, timedelta


def 重开模拟器(QQ: int, GroupID: int, Quantity: int, **kwargs) -> (bool, str):
    Item = DB_Item.getUserItem(QQ=QQ, ItemName="重开模拟器")
    # 商品的数量检查在本函数调用前完成，保险起见再检查一次
    if Item.Quantity < 1:
        return False, "当前你的重开模拟器数量不足。"
    # 逻辑检查 一次只能使用一个重开模拟器
    if Quantity != 1:
        return False, "一次只能使用一个重开模拟器。"
    slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
    SlaveUtils.获取现代世界观属性(slave)
    ExtraInfo = SlaveUtils.GetExtraInfo(slave)
    if "现代世界观_通常属性" not in ExtraInfo.keys():
        return False, "当前你的人物还未生成，不能使用重开模拟器。"
    else:
        attributes = numpy.random.normal(loc=100, size=3, scale=20)
        for index in range(0, 3):
            if attributes[index] < 0:
                attributes[index] = 0
            if attributes[index] > 200:
                attributes[index] = 200
        ExtraInfo["现代世界观_通常属性"] = {
            "颜值": int(attributes[0]),
            "智力": int(attributes[1]),
            "体质": int(attributes[2]),
            "version": 2.0
        }
        Item.Quantity -= 1
        Item.save()
        SlaveUtils.SaveExtraInfo(slave, ExtraInfo)
        return True, f"重开成功，当前基础属性为 颜值{int(attributes[0])} 智力{int(attributes[1])} 体质{int(attributes[2])}。"


def 世界线演算装置(QQ: int, GroupID: int, Quantity: int, **kwargs) -> (bool, str):
    start = time.time_ns()
    Item = DB_Item.getUserItem(QQ=QQ, ItemName="重开模拟器")
    Item2 = DB_Item.getUserItem(QQ=QQ, ItemName="世界线演算装置")
    if Item.Quantity < 1:
        return False, "当前你的重开模拟器数量不足。"
    if Item2.Quantity < 1:
        return False, "当前你的世界线演算装置数量不足。"
    # 逻辑检查 一次只能使用一个世界线演算装置
    if Quantity != 1:
        return False, "一次只能使用一个世界线演算装置。"
    # 若不存在属性则进行生成
    slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
    SlaveUtils.获取现代世界观属性(slave)
    ExtraInfo = SlaveUtils.GetExtraInfo(slave)
    # 消耗所有重开模拟器取最大值进行生成
    number = Item.Quantity
    Item.Quantity = 0
    Item.save()
    Item2.Quantity -= 1
    Item2.save()
    颜值 = ExtraInfo["现代世界观_通常属性"]["颜值"]
    智力 = ExtraInfo["现代世界观_通常属性"]["智力"]
    体质 = ExtraInfo["现代世界观_通常属性"]["体质"]
    attributes = numpy.random.normal(loc=100, size=(number, 3), scale=20)
    Max = numpy.max(attributes, axis=0)
    颜值 = int(max(颜值, Max[0]))
    智力 = int(max(智力, Max[1]))
    体质 = int(max(体质, Max[2]))
    ExtraInfo["现代世界观_通常属性"]["颜值"] = 颜值
    ExtraInfo["现代世界观_通常属性"]["智力"] = 智力
    ExtraInfo["现代世界观_通常属性"]["体质"] = 体质
    end = time.time_ns()
    t = end - start
    if t > 1000000000:
        timeStr = f"用时{round(t / 1000000000, 3)}s"
    elif t > 1000000:
        timeStr = f"用时{round(t / 1000000, 3)}ms"
    else:
        timeStr = f"用时{round(t / 1000, 3)}us"
    SlaveUtils.SaveExtraInfo(slave, ExtraInfo)
    return True, f"世界线演算成功，{timeStr}，消耗重开模拟器{number}个。当前基础属性为 颜值{颜值} 智力{智力} 体质{体质}。"


def 猫娘变身器(QQ: int, GroupID: int, Quantity: int, **kwargs) -> (bool, str):
    Item = DB_Item.getUserItem(QQ=QQ, ItemName="猫娘变身器")
    # 商品的数量检查在本函数调用前完成，保险起见再检查一次
    if Item.Quantity < 1:
        return False, "猫娘变身器数量不足。"
    # 逻辑检查 一次只能使用一个猫娘变身器
    if Quantity != 1:
        return False, "一次只能使用一个猫娘变身器哦。"
    slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
    ExtraInfo = SlaveUtils.GetExtraInfo(slave)
    # 添加标签
    if "现代世界观_人物标签" not in ExtraInfo.keys():
        ExtraInfo["现代世界观_人物标签"] = ["猫娘"]
    else:
        if "猫娘" in ExtraInfo["现代世界观_人物标签"]:
            return False, "【{UserName}】已经是猫娘了哦。"
        ExtraInfo["现代世界观_人物标签"].append("猫娘")
    # 添加buff
    if "现代世界观_BUFF" not in ExtraInfo.keys():
        ExtraInfo["现代世界观_BUFF"] = {
            "颜值": 2.0,
            "智力": 1.0,
            "体质": 0.7
        }
    else:
        ExtraInfo["现代世界观_BUFF"]["颜值"] *= 2.0
        ExtraInfo["现代世界观_BUFF"]["体质"] *= 0.7
    SlaveUtils.SaveExtraInfo(slave, ExtraInfo)
    # 修改物品数量
    Item.Quantity -= 1
    Item.save()
    # 添加技能
    SkillInfo = SlaveUtils.GetSkillInfo(slave=slave)
    if "给我变" not in SkillInfo:
        SkillInfo.append("给我变")
    SlaveUtils.SaveSkillInfo(slave=slave, SkillInfoList=SkillInfo)
    return True, "一道光闪过，【{UserName}】变成了一只的猫娘，【{UserName}】看起来更可爱更娇弱了。"


def 白丝连裤袜(QQ: int, GroupID: int, Quantity: int, **kwargs) -> (bool, str):
    Item = DB_Item.getUserItem(QQ=QQ, ItemName="白丝连裤袜")
    # 商品的数量检查在本函数调用前完成，保险起见再检查一次
    if Item.Quantity < 1:
        return False, "你还没有白丝哦。"
    # 逻辑检查 一次只能使用一个白丝
    if Quantity != 1:
        return False, "一次只能穿一双白丝哦。"
    slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
    ExtraInfo = SlaveUtils.GetExtraInfo(slave)
    # 添加标签
    if "现代世界观_人物标签" not in ExtraInfo.keys():
        ExtraInfo["现代世界观_人物标签"] = ["白丝jiojio"]
    else:
        if "白丝jiojio" in ExtraInfo["现代世界观_人物标签"]:
            return False, "【{UserName}】已经穿上白丝了哦。"
        ExtraInfo["现代世界观_人物标签"].append("白丝jiojio")
    # 添加buff
    if "现代世界观_BUFF" not in ExtraInfo.keys():
        ExtraInfo["现代世界观_BUFF"] = {
            "颜值": 1.5,
            "智力": 1.0,
            "体质": 1.0
        }
    else:
        ExtraInfo["现代世界观_BUFF"]["颜值"] *= 1.5
    SlaveUtils.SaveExtraInfo(slave, ExtraInfo)
    # 修改物品数量
    Item.Quantity -= 1
    Item.save()
    return True, "【{UserName}】四处张望发现没人后，偷偷从包里摸出来一双白丝，轻轻展开，拉到膝盖处，再慢慢拉上大腿。" \
                 "细腻丝滑的袜子包裹摩擦着【{UserName}】的双腿，她的脸颊逐渐泛起一层淡淡的粉红色。。。"


def 灵魂宝石(QQ: int, GroupID: int, Quantity: int, **kwargs) -> (bool, str):
    Item = DB_Item.getUserItem(QQ=QQ, ItemName="灵魂宝石")
    # 商品的数量检查在本函数调用前完成，保险起见再检查一次
    if Item.Quantity < 1:
        return False, "你没有灵魂宝石。"
    # 逻辑检查 一次只能使用一个灵魂宝石
    if Quantity != 1:
        return False, "只能使用一个灵魂宝石。"
    slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
    ExtraInfo = SlaveUtils.GetExtraInfo(slave)
    # 添加标签
    if "现代世界观_人物标签" not in ExtraInfo.keys():
        ExtraInfo["现代世界观_人物标签"] = ["魔法少女"]
    else:
        if "魔法少女" in ExtraInfo["现代世界观_人物标签"]:
            return False, "【{UserName}】已经是魔法少女了。"
        ExtraInfo["现代世界观_人物标签"].append("魔法少女")
    # 添加buff
    if "现代世界观_BUFF" not in ExtraInfo.keys():
        ExtraInfo["现代世界观_BUFF"] = {
            "颜值": 1.0,
            "智力": 1.0,
            "体质": 3.0
        }
    else:
        ExtraInfo["现代世界观_BUFF"]["体质"] *= 3.0
    SlaveUtils.SaveExtraInfo(slave, ExtraInfo)
    # 添加技能
    SkillInfo = SlaveUtils.GetSkillInfo(slave=slave)
    if "魔女狩猎" not in SkillInfo:
        SkillInfo.append("魔女狩猎")
    SlaveUtils.SaveSkillInfo(slave=slave, SkillInfoList=SkillInfo)
    return True, "【{UserName}】与名为丘比的神秘生物签订了魔法契约获得了强大的力量。然而，奇迹与魔法并不是免费的，" \
                 "祈求希望的同时也会散布同样分量的绝望。。。"


def 粉色项圈(QQ: int, GroupID: int, Quantity: int, **kwargs) -> (bool, str):
    if "target" not in kwargs.keys():
        return False, "请指定对象哦"
    target = kwargs["target"]
    Item = DB_Item.getUserItem(QQ=QQ, ItemName="粉色项圈")
    # 商品的数量检查在本函数调用前完成，保险起见再检查一次
    if Item.Quantity < Quantity:
        return False, "你的粉色项圈个数不够哦"

    slave = DB_slave.getUser(QQ=target, GroupID=GroupID)
    # 逻辑检查 非老婆或非本人。若指定对象为本人则将slave重定向为自己
    if target == 0:
        slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
    elif SlaveUtils.结婚对象(slave) != QQ:
        return False, "不能对你或你老婆以外的人使用哦"
    slaveInfo = SlaveUtils.GetExtraInfo(slave)
    Today = datetime.now()
    if "签约期" not in slaveInfo:
        DeadLine = Today + timedelta(days=Quantity)
    else:
        OldDeadLine = datetime.strptime(slaveInfo["签约期"], "%Y-%m-%d %H:%M:%S")
        DeadLine = max(OldDeadLine, Today) + timedelta(days=Quantity)
    slaveInfo["签约期"] = DeadLine.strftime("%Y-%m-%d %H:%M:%S")
    SlaveUtils.SaveExtraInfo(slave=slave, ExtraInfoDict=slaveInfo)
    Item.Quantity -= Quantity
    Item.save()
    timeStr = DeadLine.strftime("%Y年%m月%d日%H时 %M:%S")
    if target == 0:
        return True, "{UserName}为自己带上了粉色项圈，直到" + timeStr + "前有效~"
    else:
        return True, "{UserName}为{TargetName}带上了粉色项圈，直到" + timeStr + "前有效~"


def 项圈状态查询(QQ: int, GroupID: int) -> (bool, str):
    """
    查询用户当前是否被项圈束缚

    :param QQ: 用户QQ
    :param GroupID: 用户群组
    :return: 是否被束缚 True: 被束缚 （返回截止日期） False: 未被束缚
    """
    slave = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
    slaveInfo = SlaveUtils.GetExtraInfo(slave)
    if "签约期" not in slaveInfo:
        return False, ""
    else:
        Today = datetime.now()
        DeadLine = datetime.strptime(slaveInfo["签约期"], "%Y-%m-%d %H:%M:%S")
        if Today > DeadLine:
            return False, ""
        else:
            return True, DeadLine.strftime("%Y年%m月%d日%H时 %M:%S")


def 结婚戒指(QQ: int, GroupID: int, Quantity: int, **kwargs) -> (bool, str):
    if "target" not in kwargs.keys():
        return False, "请指定对象哦"
    target = kwargs["target"]
    Item = DB_Item.getUserItem(QQ=QQ, ItemName="结婚戒指")
    # 商品的数量检查在本函数调用前完成，保险起见再检查一次
    if Item.Quantity < 1:
        return False, "你的结婚戒指个数不够哦"
    if Quantity != 1:
        return False, "只能使用一个结婚戒指哦"
    if target == 0:
        return False, "请指定对象哦"
    # 检查双方状态
    求婚者 = DB_slave.getUser(QQ=QQ, GroupID=GroupID)
    求婚者状态 = SlaveUtils.GetExtraInfo(求婚者)
    被求婚者 = DB_slave.getUser(QQ=target, GroupID=GroupID)
    被求婚者状态 = SlaveUtils.GetExtraInfo(被求婚者)
    if "结婚状态" not in 求婚者状态.keys():
        求婚者状态["结婚状态"] = "未婚"
        SlaveUtils.SaveExtraInfo(求婚者, 求婚者状态)
    if "结婚状态" not in 被求婚者状态.keys():
        被求婚者状态["结婚状态"] = "未婚"
        SlaveUtils.SaveExtraInfo(被求婚者, 被求婚者状态)
    # 获取状态
    求婚者结婚状态: str = 求婚者状态["结婚状态"]
    被求婚者结婚状态: str = 被求婚者状态["结婚状态"]
    # 检查已婚
    if 求婚者结婚状态.startswith("已婚"):
        return False, "爬，你已经结过婚了"
    if 被求婚者结婚状态.startswith("已婚"):
        return False, "{TargetName}已结婚了哦"
    # 检查求婚
    if 被求婚者结婚状态.startswith("求婚"):
        求婚目标 = 被求婚者结婚状态.split(" ")[1]
        if 求婚目标 == str(QQ):
            # 双方互相指定，成功结婚
            # 保存结婚状态
            求婚者状态["结婚状态"] = f"已婚 {target}"
            被求婚者状态["结婚状态"] = f"已婚 {QQ}"
            SlaveUtils.SaveExtraInfo(求婚者, 求婚者状态)
            SlaveUtils.SaveExtraInfo(被求婚者, 被求婚者状态)
            bot: Bot = kwargs["bot"]
            # 处理结婚动作
            # - 取消当前主人
            求婚者.Owner = 0
            被求婚者.Owner = 0
            求婚者.save()
            被求婚者.save()
            # 发送结婚结果
            return True, "恭喜{UserName}与{TargetName}结婚成功~"
    求婚者状态["结婚状态"] = f"求婚 {target}"
    SlaveUtils.SaveExtraInfo(求婚者, 求婚者状态)
    return True, "求婚成功，请等待{TargetName}的回应吧！"
