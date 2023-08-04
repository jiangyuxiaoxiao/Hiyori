"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/4-8:05
@Desc: 多bot连接支持 基于hook实现
@Ver : 1.0.0
"""
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.message import event_preprocessor
from nonebot.log import logger
from nonebot import get_bots
from nonebot.exception import IgnoredException

from .config import multiBotConfig

driver = get_driver()


# 在bot连接时检查配置文件，不存在则添加规则
@driver.on_bot_connect
async def _(bot: Bot):
    QQ = bot.self_id
    if QQ not in multiBotConfig.priority:
        multiBotConfig.priority.append(QQ)
        multiBotConfig.dump()
        logger.debug(f"QQBot:{QQ}已连接，添加到Bot响应序列中")


# 在事件开始响应时检查规则，中断不响应bot的流程
@event_preprocessor
async def _(event: Event):
    if hasattr(event, "group_id"):
        GroupID: str = str(event.group_id)
        bots = get_bots().keys()  # bot的QQ列表，str格式
        # 群组不在特殊规则中
        if GroupID not in multiBotConfig.rule.keys():
            # 遍历响应优先序列，按顺序找到第一个已开启的QQ
            for QQ in multiBotConfig.priority:
                # 对应QQ已开启
                if QQ in bots:
                    if str(event.self_id) != QQ:
                        raise IgnoredException("多Bot响应屏蔽")
                    else:
                        return
        else:
            # 本bot与该群组响应规则不匹配，且响应规则的bot已开启
            ruleID = multiBotConfig.rule[GroupID]
            if (int(ruleID) != event.self_id) and (ruleID in bots):
                raise IgnoredException("多Bot响应屏蔽")
