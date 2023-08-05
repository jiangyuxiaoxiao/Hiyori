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
    botQQ = bot.self_id
    if botQQ not in multiBotConfig.priority:
        multiBotConfig.priority.append(botQQ)
        multiBotConfig.dump()
        logger.debug(f"【MultiBot_Support】QQBot:{botQQ}已连接，添加到Bot响应序列中")
    # 导入bot所在群聊
    multiBotConfig.groupSet[botQQ] = set()
    groupList = await bot.get_group_list()

    for groupInfo in groupList:
        multiBotConfig.groupSet[botQQ].add(str(groupInfo["group_id"]))
    logger.debug(f"【MultiBot_Support】QQBot:{botQQ}已连接，已注册Bot所在群聊")


# 在事件开始响应时检查规则，中断不响应bot的流程
@event_preprocessor
async def _(event: Event):
    if hasattr(event, "group_id"):
        GroupID: str = str(event.group_id)
        multiBotConfig.groupSet[str(event.self_id)].add(GroupID)  # 添加到set中
        bots = get_bots().keys()  # bot的QQ列表，str格式
        # 群组不在特殊规则中
        if GroupID not in multiBotConfig.rule.keys():
            # 遍历响应优先序列，按顺序找到第一个已开启且在本群聊中的QQ
            for botQQ in multiBotConfig.priority:
                # 对应Bot已开启 而且这个Bot在群聊中
                if (botQQ in bots) and (GroupID in multiBotConfig.groupSet[botQQ]):
                    if str(event.self_id) != botQQ:
                        raise IgnoredException("多Bot响应屏蔽")
                    else:
                        return
        else:
            # 特定规则指定的QQ
            ruleQQ = multiBotConfig.rule[GroupID]
            # 本bot与该群组响应规则不匹配，且响应规则的bot已开启
            if (int(ruleQQ) != event.self_id) and (ruleQQ in bots):
                raise IgnoredException("多Bot响应屏蔽")
            # 响应规则的bot未开启，则按照默认的优先序列，按顺序找到第一个已开启且在本群聊中的QQ
            elif ruleQQ not in bots:
                for botQQ in multiBotConfig.priority:
                    # 对应Bot已开启 而且这个Bot在群聊中
                    if (botQQ in bots) and (GroupID in multiBotConfig.groupSet[botQQ]):
                        if str(event.self_id) != botQQ:
                            raise IgnoredException("多Bot响应屏蔽")
                        else:
                            return


