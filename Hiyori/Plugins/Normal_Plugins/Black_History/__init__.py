"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/1-0:18
@Desc: 群友黑历史【不稳定会掉图】
@Ver : 1.0.0
"""
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, GROUP_ADMIN, GROUP_OWNER, MessageSegment
from nonebot.permission import SUPERUSER
from Hiyori.Utils.Permissions import Hiyori_OWNER, Hiyori_ADMIN
from nonebot.typing import T_State
from Hiyori.Utils.Message.Forward_Message import Nodes
from nonebot.plugin import PluginMetadata
from Hiyori.Utils.Priority import Priority
from .database import ChatRecord
import re
import random

__plugin_meta__ = PluginMetadata(
    name="群友黑历史",  # 用于在菜单显示 用于插件开关
    description="记录群友黑历史的小本本！",  # 用于在菜单中描述
    usage="#上传黑历史【回复要上传的黑历史消息】\n"
          "#上传多段黑历史@群友 然后转发相应的聊天记录\n"
          "#黑历史\n"
          "#黑历史@群友",
    extra={"CD_Weight": 1,  # 调用插件CD权重 不填的话不会触发权重插件
           "example": "#吃什么",
           "Group": "Daily",
           "version": "1.0",
           "Keep_On": False,
           "Type": "Normal_Plugin",
           }
)

UploadHistory = on_regex("^#上传黑历史", priority=Priority.普通优先级, block=False)
UploadMultipleHistory = on_regex("^#上传多段黑历史", priority=Priority.普通优先级, block=False)
GetHistory = on_regex("^#黑历史", priority=Priority.普通优先级, block=False)


# 上传黑历史
@UploadHistory.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    # noinspection PyBroadException
    message = str(event.raw_message)
    # 匿名上传
    if message == "#上传黑历史":
        return
    # 指定QQ号上传
    else:
        try:
            pattern = re.compile("\\[CQ:reply,id=-?[0-9]*]")
            record = re.findall(pattern=pattern, string=message)
            if len(record) == 0:
                await UploadHistory.finish("格式错误")
                return
            record = record[0]
            GroupID = event.group_id
            MessageID = record.replace("[CQ:reply,id=", "")
            MessageID = MessageID.replace("]", "")
            MessageID = int(MessageID)
            replyMsg = await bot.get_msg(message_id=MessageID)
            QQ = replyMsg["sender"]["user_id"]
            newChatRecord = ChatRecord.create(MessageID=MessageID, ForwardMessageID=None, QQ=QQ, GroupID=GroupID)
            newChatRecord.save()
        except Exception as e:
            await UploadHistory.send("上传失败")
            raise e
        await UploadHistory.finish("上传成功")
        return


# 上传黑历史——匿名
@UploadHistory.receive("")
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        GroupID = event.group_id
        MessageID = event.message_id
        newChatRecord = ChatRecord.create(MessageID=MessageID, ForwardMessageID=None, QQ=0, GroupID=GroupID)
        newChatRecord.save()
    except Exception as e:
        await UploadHistory.send("上传失败")
        raise e
    await UploadHistory.send("上传成功")
    return


# 上传多段黑历史
@UploadMultipleHistory.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    message = str(event.raw_message)
    message = message.replace("#上传多段黑历史", "").strip()
    if message == "":
        state["HiyoriDict_QQ"] = 1
        return
    message = message.replace("[CQ:at,qq=", "")
    message = message.replace("]", "")
    if message.isdigit():
        state["HiyoriDict_QQ"] = int(message)
    else:
        await UploadMultipleHistory.finish("输入格式不正确")
    return


@UploadMultipleHistory.receive("")
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    # noinspection PyBroadException
    try:
        message = str(event.raw_message)
        if message.startswith("[CQ:forward,id="):
            message = message.replace("[CQ:forward,id=", "")
            GroupID = event.group_id
            ID = message.replace("]", "").strip()
            # forwardMsgs = await bot.get_forward_msg(id=ID)
            newChatRecord = ChatRecord.create(MessageID=None, ForwardMessageID=ID, QQ=state["HiyoriDict_QQ"],
                                              GroupID=GroupID)
            newChatRecord.save()
        else:
            await UploadMultipleHistory.send("上传失败")
            return
    except Exception as e:
        await UploadMultipleHistory.send("上传失败")
        raise e
    await UploadHistory.send("上传成功")


# 获取黑历史
@GetHistory.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    # noinspection PyBroadException
    try:
        GroupID = event.group_id
        message = str(event.message)
        message = message.replace("#黑历史", "").strip()
        message = message.replace("[CQ:at,qq=", "")
        message = message.replace("]", "")
        message = message.strip()
        if message.isdigit():
            QQ = int(message)
            result = ChatRecord.select().where(ChatRecord.QQ == QQ, ChatRecord.DeleteFlag == False)
        else:
            result = ChatRecord.select().where(ChatRecord.GroupID == GroupID, ChatRecord.DeleteFlag == False)

        RecordNums = len(result)
        if RecordNums == 0:
            await GetHistory.send("黑历史记录不存在")
            return
        RandomNum = random.randint(0, RecordNums - 1)
        MessageID = result[RandomNum].MessageID
        ForwardMessageID = result[RandomNum].ForwardMessageID
        if MessageID is not None:
            message = Nodes(msgID=MessageID)
            await bot.send_group_forward_msg(group_id=event.group_id, messages=message.msg())
            return
        elif ForwardMessageID is not None:
            message = MessageSegment.forward(id_=ForwardMessageID)
            await GetHistory.send(message)
        else:
            ID = result[RandomNum].ID
            await GetHistory.send(f"数据库记录出错，记录ID={ID}")
    except Exception as e:
        await UploadHistory.send("发送失败")
        raise e
