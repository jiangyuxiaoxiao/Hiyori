"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/1-0:20
@Desc: 撤回检查
@Ver : 1.0.0
"""
from nonebot.adapters.onebot.v11 import GroupRecallNoticeEvent, MessageSegment, Bot
from nonebot import on_notice
from nonebot.log import logger
from Hiyori.Utils.Priority import Priority
import random
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="撤回检查！",
    description="偷偷发女装照片，不料被妃爱当场抓住！",
    usage="撤回消息时概率触发",
    extra={
        "CD_Weight": 0,
        "permission": "普通权限",
        "example": "",
        "Keep_On": False,
        "Type": "Auto_Plugin",
    },
)
概率 = 20  # 100/1000
recallChecker = on_notice(priority=Priority.低优先级, block=False)


@recallChecker.handle()
async def _(bot: Bot, event: GroupRecallNoticeEvent):
    global 概率
    result = random.randint(1, 1000)
    if result < 概率:
        logger.debug(f"撤回随机数【{result}】判定成功")
        QQ = event.operator_id
        GroupID = event.group_id
        MemberInfo = await bot.get_group_member_info(group_id=GroupID, user_id=QQ, no_cache=True)
        if "nickname" in MemberInfo.keys():
            Nickname = MemberInfo["nickname"]
        else:
            Nickname = ""
        message = MessageSegment.text("刚刚，") + MessageSegment.at(QQ) + "撤回了自己的女装照片。"
        await recallChecker.send(message)
        await bot.call_api("send_group_forward_msg", **{"group_id": GroupID, "messages": [
            {
                "type": "node",
                "data": {
                    "name": Nickname,
                    "uin": str(QQ),
                    "content": "[照片已撤回]"
                }
            }]})
    else:
        logger.debug(f"撤回随机数【{result}】判定失败")
