"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/1-0:00
@Desc: 打工事件
@Ver : 1.0.0
"""
import random
from abc import ABC, abstractmethod
from Hiyori.Utils.Database.slaveMarket import Slave
from .Utils import SlaveUtils


class Job(ABC):
    name = "JobName"

    @staticmethod
    def Enable(slave: Slave) -> bool:
        """
        判断是否胜任工作
        """
        return True

    @staticmethod
    @abstractmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        """
        执行工作，并返回执行结果以及获取的收入（单位：元）。
        """
        pass


class 黑煤窑(Job):
    name = "去黑煤窑挖煤"

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        体质 = SlaveUtils.获取现代世界观属性(slave)[2]
        if 体质 <= 60:
            time = random.randint(1, 3)
            return f"【{slaveName}】去黑煤窑挖煤，因为体质虚弱，才下矿{time}小时就累得晕倒了，没有获取到报酬。", 0
        if 体质 <= 80:
            income = random.randint(5, 10)
            return f"【{slaveName}】去黑煤窑挖煤，但是力气太小，被工头克扣了工钱。获得收入{income}妃爱币。", income
        if 体质 <= 120:
            income = random.randint(10, 20)
            return f"【{slaveName}】去黑煤窑挖煤，获得收入{income}妃爱币。", income
        if 体质 <= 140:
            income = random.randint(20, 40)
            return f"【{slaveName}】去黑煤窑挖煤，【{slaveName}】在矿里大干22小时，回来的时候脸都成碳了。获得收入{income}妃爱币", income
        else:
            income = random.randint(40, 80)
            return f"【{slaveName}】去黑煤窑挖煤，因为看工头不爽把工头暴揍了一顿，获得了煤老板的赏识。煤老板提拔【{slaveName}】当贴身保镖。获得收入{income}妃爱币", income


class 小传单(Job):
    name = "发小传单"

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        颜值 = SlaveUtils.获取现代世界观属性(slave)[0]
        if 颜值 <= 60:
            income = random.randint(1, 5)
            return f"【{slaveName}】去在大街上发小传单，因为长得太丑路人纷纷避让，【{slaveName}】没有完成任务。获得收入{income}妃爱币。", income
        if 颜值 <= 120:
            income = random.randint(10, 20)
            return f"【{slaveName}】去在大街上发小传单，【{slaveName}】在大街上发了一天的小传单。获得收入{income}妃爱币。", income
        if 颜值 <= 140:
            income = random.randint(20, 40)
            return f"【{slaveName}】去在大街上发小传单，【{slaveName}】超额完成了任务。获得收入{income}妃爱币", income
        else:
            income = random.randint(40, 80)
            return f"【{slaveName}】去在大街上发小传单，因为长得实在太可爱，路人纷纷跑来抢传单把路都堵死了。获得收入{income}妃爱币", income


class 打灰(Job):
    name = "工地打灰"

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        属性 = SlaveUtils.获取现代世界观属性(slave)
        颜值 = 属性[0]
        智力 = 属性[1]
        体质 = 属性[2]
        if 体质 <= 60:
            return f"【{slaveName}】替跑路的土木老哥打灰，但是力气太小无法胜任工作，没有获取到报酬。", 0
        if 智力 <= 60:
            return f"【{slaveName}】替跑路的土木老哥打灰，因为没有听懂工头的要求添加错了石灰粉的比例，差点造成严重的生产事故。没有获取到报酬。", 0
        if 体质 <= 80:
            income = random.randint(5, 10)
            return f"【{slaveName}】替跑路的土木老哥打灰，但是力气太小没有完成指标，被工头克扣了工钱。获得收入{income}妃爱币。", income
        if 体质 <= 120:
            income = random.randint(10, 20)
            return f"【{slaveName}】替跑路的土木老哥打灰，获得收入{income}妃爱币。", income
        if 体质 <= 140:
            income = random.randint(20, 40)
            return f"【{slaveName}】替跑路的土木老哥打灰，【{slaveName}】一人顶俩超额完成了任务。获得收入{income}妃爱币。", income
        else:
            income = random.randint(40, 80)
            return f"【{slaveName}】替跑路的土木老哥打灰，力大无穷的【{slaveName}】很快完成了任务然后跑去搬砖1000趟。获得收入{income}妃爱币", income


class 飞饼(Job):
    name = "摆摊卖鸡哥飞饼"

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        income = random.randint(10, 20)
        return f"【{slaveName}】在美食街出售鸡你太美飞饼，虽然把饼甩飞了，但是围观群众纷纷购买鸡哥飞饼。获得收入{income}妃爱币。", income


class B站审核(Job):
    name = "皮站审核"

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        income = random.randint(10, 20)
        time = random.randint(5, 20)
        return f"【{slaveName}】替B站审核观看了土豆旋转{time}小时。获得收入{income}妃爱币。", income


class 代课(Job):
    name = "帮大学生代课"

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        属性 = SlaveUtils.获取现代世界观属性(slave)
        颜值 = 属性[0]
        智力 = 属性[1]
        体质 = 属性[2]
        if 颜值 >= 140:
            income = random.randint(40, 80)
            return f"【{slaveName}】帮大学生小王代课，因为长得太好看被老师一眼发现是代课的。但是小王不仅没有责怪反而对【{slaveName}】穷追猛舔，获得收入{income}妃爱币。", income
        result = random.randint(1, 3)
        if result == 1:
            income = random.randint(10, 20)
            return f"【{slaveName}】帮大学生听了一天的专业课，获得收入{income}妃爱币。", income
        else:
            if 智力 <= 60:
                return f"【{slaveName}】帮大学生代课，因为被老师点名时没有听懂问题而暴露。没有获取到报酬", 0
            if 智力 <= 120:
                income = random.randint(10, 20)
                return f"【{slaveName}】帮大学生代课，被老师点名回答问题，好在【{slaveName}】灵机一动蒙混过关。获得收入{income}妃爱币。", income
            if 智力 <= 140:
                income = random.randint(20, 40)
                return f"【{slaveName}】帮大学生代课，被老师点名回答问题，【{slaveName}】正确回答了问题。获得收入{income}妃爱币。", income
            else:
                income = random.randint(40, 80)
                return f"【{slaveName}】帮大学生代课，被老师点名回答问题，【{slaveName}】回答了问题后还觉得不过瘾直接跑上讲台开始讲课。老师感动地说道你的这门课免修直接一百昏。获得收入{income}妃爱币。", income


class 不要笑挑战(Job):
    name = "不要笑挑战"

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        income = random.randint(10, 20)
        return f"【{slaveName}】参加了网红主播的不要笑挑战。获得收入{income}妃爱币。", income


class 洗盘子(Job):
    name = "跑路洗盘子"

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        income = random.randint(10, 20)
        return f"【{slaveName}】偷渡到美国在中餐馆洗盘子。获得收入{income}妃爱币。", income


class 闲鱼(Job):
    name = "当某鱼卖家"

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        属性 = SlaveUtils.获取现代世界观属性(slave)
        颜值 = 属性[0]
        智力 = 属性[1]
        体质 = 属性[2]
        if 颜值 >= 140:
            income = random.randint(40, 80)
            return f"【{slaveName}】在闲鱼上出售自己的原味胖次，供不应求。获得收入{income}妃爱币。", income
        if 颜值 >= 120:
            income = random.randint(20, 40)
            return f"【{slaveName}】在闲鱼上出售自己的原味白丝，刚上架就被变态老哥买走了。获得收入{income}妃爱币。", income
        if 智力 >= 140:
            income = random.randint(40, 80)
            return f"【{slaveName}】在闲鱼上出售自己开发的蓝色药丸，供不应求。获得收入{income}妃爱币。", income
        if 智力 >= 80:
            income = random.randint(10, 20)
            return f"【{slaveName}】在闲鱼上倒卖二手物品。获得收入{income}妃爱币。", income
        else:
            return f"【{slaveName}】在闲鱼上卖东西，忙了一天啥也没卖出去。", 0


class 横店(Job):
    name = "当群演"

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        属性 = SlaveUtils.获取现代世界观属性(slave)
        颜值 = 属性[0]
        智力 = 属性[1]
        体质 = 属性[2]

        if 颜值 >= 160:
            income = random.randint(200, 400)
            return f"【{slaveName}】去横店当群演，路过选角现场时被导演一眼相中拉来演女主。获得收入{income}妃爱币。", income
        if 颜值 >= 140:
            income = random.randint(60, 120)
            return f"【{slaveName}】去横店当女配，获得收入{income}妃爱币。", income
        if 颜值 >= 120:
            income = random.randint(30, 60)
            return f"【{slaveName}】去横店当群演，获得收入{income}妃爱币。", income
        if 体质 > 120:
            income = random.randint(15, 30)
            return f"【{slaveName}】去横店当八路群演，手撕了20次太君导演才说咔。获得收入{income}妃爱币。", income
        else:
            income = random.randint(10, 15)
            return f"【{slaveName}】去横店当太君群演，被八路手撕了20次导演才说咔。获得收入{income}妃爱币。", income


class 漫展(Job):
    name = "去漫展"

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        属性 = SlaveUtils.获取现代世界观属性(slave)
        颜值 = 属性[0]
        智力 = 属性[1]
        体质 = 属性[2]
        if 颜值 >= 140:
            income = random.randint(40, 80)
            name = ["独角兽", "伊莉雅", "小草神", "樱岛麻衣", "穹妹", "妃爱", "朱雀院椿"]
            return f"【{slaveName}】去漫展cos了{random.choice(name)}，路人纷纷围观拍摄。获得收入{income}妃爱币。", income
        if 智力 >= 130:
            income = random.randint(20, 40)
            return f"【{slaveName}】参加漫展，帮著名画师毛玉牛乳兜售新作。获得收入{income}妃爱币。", income
        if 颜值 >= 120:
            income = random.randint(20, 40)
            return f"【{slaveName}】去漫展出cos，获得收入{income}妃爱币。", income
        if 体质 >= 140:
            income = random.randint(40, 80)
            return f"【{slaveName}】去漫展cos了dark兄贵，获得收入{income}妃爱币。", income
        if 智力 >= 80:
            income = random.randint(10, 20)
            return f"【{slaveName}】去漫展帮忙摆摊，获得收入{income}妃爱币。", income
        else:
            return f"【{slaveName}】去漫展玩了一天，没有获取到报酬", 0


class 猫咖(Job):
    name = "去猫咖打工"

    @staticmethod
    def Enable(slave: Slave) -> bool:
        ExtraInfo = SlaveUtils.GetExtraInfo(slave)
        if "现代世界观_人物标签" in ExtraInfo.keys():
            if "猫娘" in ExtraInfo["现代世界观_人物标签"]:
                return True
        return False

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        属性 = SlaveUtils.获取现代世界观属性(slave)
        颜值 = 属性[0]
        if 颜值 >= 160:
            income = random.randint(160, 320)
        elif 颜值 >= 140:
            income = random.randint(80, 160)
        elif 颜值 >= 120:
            income = random.randint(40, 80)
        else:
            income = random.randint(20, 40)
        msgs = (
            "教了客人喵喵语", "被客人摸了摸耳朵", "被客人偷偷摸了尾巴", "被客人抱抱", "为客人推荐了店里的招牌喵喵咖啡",
            "与神秘的白丝美少女贴贴")
        return f"可爱的猫娘【{slaveName}】去猫咖打工，{random.choice(msgs)}。获得收入{income}妃爱币。", income


class 魔物讨伐(Job):
    name = "讨伐魔物"

    @staticmethod
    def Enable(slave: Slave) -> bool:
        ExtraInfo = SlaveUtils.GetExtraInfo(slave)
        if "现代世界观_人物标签" in ExtraInfo.keys():
            if "魔法少女" in ExtraInfo["现代世界观_人物标签"]:
                return True
        return False

    @staticmethod
    def Execute(slave: Slave, slaveName: str) -> (str, int):
        属性 = SlaveUtils.获取现代世界观属性(slave)
        体质 = 属性[2]
        if 体质 >= 160:
            income = random.randint(240, 480) + 100
        elif 体质 >= 140:
            income = random.randint(120, 240) + 50
        elif 体质 >= 120:
            income = random.randint(60, 120) + 20
        else:
            income = random.randint(30, 60)
        events = (
            "不小心被神秘的触手怪打败了，在触手巢里被滑腻的触手反复调教❤，好不容易才逃脱出来", "击败了强大的触手魔物",
            "讨伐了史莱姆", "讨伐了强大的魔女", "讨伐了哥布林强盗，解救了商队",
            "被史莱姆打败，差点被玩坏了，浑身上下黏黏的湿透了")
        return f"魔法少女【{slaveName}】出门讨伐魔物，{random.choice(events)}。获得收入{income}妃爱币。", income


Jobs: list = [黑煤窑, 小传单, 打灰, 飞饼, B站审核, 代课, 不要笑挑战, 洗盘子, 闲鱼, 横店, 漫展, 猫咖, 魔物讨伐]
