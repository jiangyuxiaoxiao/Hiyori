"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:56
@Desc: 工具函数
@Ver : 1.0.0
"""
import json
import numpy
import scipy
import warnings
from datetime import datetime

from Hiyori.Utils.Database.slaveMarket import Slave, DB_slave
from Hiyori.Utils.File import DirExist, JsonFileExist
from .config import SlaveConfig


def 正态修正(均值: float, 标准差: float, 原值: float, 变化倍数: float) -> float:
    warnings.warn("2.0 使用属性计算函数，现已弃用", DeprecationWarning)
    if 变化倍数 >= 1:
        原排名比例 = 1 - scipy.stats.norm.cdf(原值, loc=均值, scale=标准差)
        新排名比例 = 原排名比例 / 变化倍数
        新值 = scipy.stats.norm.ppf(1 - 新排名比例, loc=均值, scale=标准差)
        return 新值
    else:
        原排名反向比例 = scipy.stats.norm.cdf(原值, loc=均值, scale=标准差)
        新排名反向比例 = 原排名反向比例 * 变化倍数
        新值 = scipy.stats.norm.ppf(新排名反向比例, loc=均值, scale=标准差)
        return 新值


class SlaveUtils:
    # 获取全部额外信息，补全所有字段
    @staticmethod
    def GetAllExtraInfo(slave: Slave) -> dict[any, any]:
        SlaveUtils.默认字段补全(slave)
        return SlaveUtils.GetExtraInfo(slave)

    # 获取额外信息
    @staticmethod
    def GetExtraInfo(slave: Slave) -> dict[any, any]:
        result = json.loads(str(slave.Extra))
        return result

    # 保存额外信息
    @staticmethod
    def SaveExtraInfo(slave: Slave, ExtraInfoDict: dict[any, any]):
        slave.Extra = json.dumps(ExtraInfoDict, ensure_ascii=False)
        slave.save()
        return

    # 获取技能信息
    @staticmethod
    def GetSkillInfo(slave: Slave) -> list:
        result = json.loads(str(slave.Skill))
        if "skills" not in result.keys():
            result["skills"] = []
            slave.Skill = json.dumps(result, ensure_ascii=False)
            slave.save()
        return result["skills"]

    # 保存技能信息
    @staticmethod
    def SaveSkillInfo(slave: Slave, SkillInfoList: list):
        result = json.loads(str(slave.Skill))
        result["skills"] = SkillInfoList
        slave.Skill = json.dumps(result, ensure_ascii=False)
        slave.save()
        return

    # 打印人物信息
    @staticmethod
    def PrintPersonInfo(slave: Slave) -> str:
        # 现代世界观相关
        attribute = SlaveUtils.获取现代世界观属性(slave)
        result = f"颜值{attribute[0]} 智力{attribute[1]} 体质{attribute[2]}"
        # 人物标签相关
        Extra = SlaveUtils.GetExtraInfo(slave)
        if "现代世界观_人物标签" in Extra.keys():
            if len(Extra["现代世界观_人物标签"]) != 0:
                result += f"<br> 特性："
                for tag in Extra["现代世界观_人物标签"]:
                    result += f"【{tag}】 "
        return result

    # 获取现代世界观属性
    @staticmethod
    def 获取现代世界观属性(slave: Slave) -> list:
        """
        更新 迁移到3.2版本 并提供了老版本的转换方式
        获取对应人物的现代世界观属性，若无则进行生成。

        :param slave: 对应人物实例
        :return: 属性字典[颜值, 智力, 体质]
        """
        ExtraInfo = SlaveUtils.GetExtraInfo(slave)
        # 字段补充1
        if "现代世界观_通常属性" not in ExtraInfo.keys():
            # 随机生成人物属性值
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
                "version": 3.2
            }
            SlaveUtils.SaveExtraInfo(slave, ExtraInfo)
        # 字段补充2
        if "现代世界观_BUFF" not in ExtraInfo.keys():
            ExtraInfo["现代世界观_BUFF"] = {
                "颜值": 0,
                "智力": 0,
                "体质": 0,
                "version": 3.2
            }
            SlaveUtils.SaveExtraInfo(slave, ExtraInfo)
        # 字段修正
        if ExtraInfo["现代世界观_通常属性"]["version"] != 3.2:
            ExtraInfo["现代世界观_通常属性"]["version"] = 3.2
            ExtraInfo["现代世界观_BUFF"]["version"] = 3.2
            ExtraInfo["现代世界观_BUFF"]["颜值"] = 0
            ExtraInfo["现代世界观_BUFF"]["体质"] = 0
            ExtraInfo["现代世界观_BUFF"]["颜值"] = 0
            # 检索标签
            if "现代世界观_人物标签" not in ExtraInfo.keys():
                ExtraInfo["现代世界观_人物标签"] = []
            else:
                tags = ExtraInfo["现代世界观_人物标签"]
                for tag in tags:
                    match tag:
                        case "猫娘":
                            ExtraInfo["现代世界观_BUFF"]["颜值"] = int(ExtraInfo["现代世界观_BUFF"]["颜值"] + 30)
                            ExtraInfo["现代世界观_BUFF"]["体质"] = int(ExtraInfo["现代世界观_BUFF"]["体质"] - 15)
                        case "魔法少女":
                            ExtraInfo["现代世界观_BUFF"]["体质"] = int(ExtraInfo["现代世界观_BUFF"]["体质"] + 40)
                        case "白丝jiojio":
                            ExtraInfo["现代世界观_BUFF"]["颜值"] = int(ExtraInfo["现代世界观_BUFF"]["颜值"] + 20)
            SlaveUtils.SaveExtraInfo(slave, ExtraInfo)

        return [int(ExtraInfo["现代世界观_通常属性"]["颜值"] + ExtraInfo["现代世界观_BUFF"]["颜值"]),
                int(ExtraInfo["现代世界观_通常属性"]["智力"] + ExtraInfo["现代世界观_BUFF"]["智力"]),
                int(ExtraInfo["现代世界观_通常属性"]["体质"] + ExtraInfo["现代世界观_BUFF"]["体质"])]

    # 默认字段补全
    @staticmethod
    def 默认字段补全(slave: Slave):
        # 补全现代世界观属性
        SlaveUtils.获取现代世界观属性(slave=slave)

    # 获取结婚对象
    @staticmethod
    def 结婚对象(slave: Slave) -> int:
        """
        若无结婚对象返回0，否则返回对应QQ号

        :param slave:
        :return:
        """
        slaveInfo = SlaveUtils.GetExtraInfo(slave)
        if "结婚状态" not in slaveInfo.keys():
            slaveInfo["结婚状态"] = "未婚"
            SlaveUtils.SaveExtraInfo(slave, slaveInfo)
            return 0
        else:
            # 已婚状态的格式为 "已婚 QQ" 中间用空格区分
            结婚状态: str = slaveInfo["结婚状态"]
            if not 结婚状态.startswith("已婚"):
                return 0
            if 结婚状态.split(" ")[1].isdigit():
                return int(结婚状态.split(" ")[1])
            return 0

    @staticmethod
    def 项圈状态(QQ: int, GroupID: int) -> (bool, str):
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


class CartUtils:
    # 用于购物车读取写入
    @staticmethod
    def ReadInfo() -> dict[str, dict[str, list[int]]]:
        DirExist(SlaveConfig.CartDir)
        JsonFileExist(SlaveConfig.CartFile)
        with open(file=SlaveConfig.CartFile, mode="r+", encoding="utf-8") as file:
            info = file.read()
            return json.loads(info)

    @staticmethod
    def WriteInfo(info: dict[str, dict[str, list[int]]]):
        DirExist(SlaveConfig.CartDir)
        JsonFileExist(SlaveConfig.CartFile)
        with open(file=SlaveConfig.CartFile, mode="w+", encoding="utf-8") as file:
            info = json.dumps(info, indent=2, ensure_ascii=False)
            file.write(info)
            return
