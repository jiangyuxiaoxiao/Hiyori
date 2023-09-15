"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/13-14:49
@Desc: 消息数据库存储
@Ver : 1.0.0
"""
import peewee
import aiohttp
import json
import base64

import nonebot.adapters.onebot.v11 as onebotV11
from nonebot.adapters.onebot.v11 import MessageSegment

from .config import MsgDB

MessageDB = peewee.SqliteDatabase(MsgDB)


# 消息表
class Message(peewee.Model):
    MessageID = peewee.IntegerField(primary_key=True)
    QQ = peewee.IntegerField(null=False)
    GroupID = peewee.IntegerField(default=0, null=False)
    Messages = peewee.TextField(default="{[]}")

    class Meta:
        database = MessageDB
        table_name = "Message"


# 消息封装方法类
class DB_Message:
    # 模块初始化函数
    @staticmethod
    def messageInit():
        """模块初始化函数，通常一次运行只调用一次。"""
        # 若表不存在，则先创建
        Message.create_table(safe=True)

    @staticmethod
    async def _downloadFile2Base64(url: str) -> str | None:
        """下载文件并保存为base64字符串"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        encoded = base64.b64encode(data)
                        return encoded.decode('utf-8')
                    return None
        except Exception:
            return None

    @staticmethod
    async def saveMessageByID(message_id: int, bot: onebotV11.Bot):
        msgInfo = await bot.get_msg(message_id=int(message_id))
        gid = msgInfo["group_id"] if "group_id" in msgInfo else 0
        await DB_Message.saveMessage(message=msgInfo["message"], bot=bot, message_id=message_id, group_id=gid, user_id=msgInfo["sender"]["user_id"])

    @staticmethod
    async def saveMessage(message: onebotV11.Message, bot: onebotV11.Bot, message_id: int, group_id: int | None, user_id: int):
        """指定保存消息到本地。消息将被持久化存储，包括图片、音频等"""
        # 仅当消息不存在时进行存储
        msg = Message.select().where(Message.MessageID == message_id)
        if len(msg) != 0:
            return
        GroupID = group_id if group_id else 0
        msgData = []
        for segment in message:
            if isinstance(segment, dict):
                data = segment["data"]
                segment_type = segment["type"]
            else:
                data = segment.data
                segment_type = segment.type
            match segment_type:
                case "text":
                    msgData.append({"type": segment_type, "data": data["text"]})
                case "image":
                    url = data["url"]
                    image = await DB_Message._downloadFile2Base64(url)
                    if image:
                        image = "base64://" + image
                        msgData.append({"type": segment_type, "data": image})
                case "at":
                    msgData.append({"type": segment_type, "data": data["qq"]})
                case "face":
                    msgData.append({"type": segment_type, "data": data["id"]})
                case "video":
                    url = data["url"]
                    video = await DB_Message._downloadFile2Base64(url)
                    if video:
                        video = "base64://" + video
                        msgData.append({"type": segment_type, "data": video})
                case "record":
                    url = data["url"]
                    record = await DB_Message._downloadFile2Base64(url)
                    if record:
                        record = "base64://" + record
                        msgData.append({"type": segment_type, "data": record})
                case "reply":
                    # 对于回复类消息，应递归存储指定id的消息
                    id = int(data["id"])
                    await DB_Message.saveMessageByID(message_id=id, bot=bot)
                    msgData.append({"type": segment_type, "data": data["id"]})
                case "json":
                    msgData.append({"type": segment_type, "data": data})
                case _:
                    msgData.append({"type": segment_type, "data": data})
        Message.create(MessageID=message_id, QQ=user_id, GroupID=GroupID, Messages=json.dumps(msgData, ensure_ascii=False, indent=2))

    @staticmethod
    async def getMessage(MessageID: int) -> onebotV11.Message | None:
        """根据消息id构造对应消息"""
        result = Message.select().where(Message.MessageID == MessageID)
        if len(result) == 0:
            return None
        msg: Message = result[0]
        segments: list[dict[str, any]] = json.loads(str(msg.Messages))
        returnMessage = None
        for segment in segments:
            segment_type = segment["type"]
            match segment_type:
                case "text":
                    returnMessage += MessageSegment.text(segment["data"])
                case "image":
                    returnMessage += MessageSegment.image(segment["data"])
                case "at":
                    returnMessage += MessageSegment.at(segment["data"])
                case "face":
                    returnMessage += MessageSegment.face(segment["data"])
                case "video":
                    returnMessage += MessageSegment.video(segment["data"])
                case "record":
                    returnMessage += MessageSegment.record(segment["data"])
                case "reply":
                    returnMessage += MessageSegment.reply(segment["data"])
                case "json":
                    returnMessage += MessageSegment.json(segment["data"])
                case _:
                    returnMessage += MessageSegment.json(segment["data"])
        return returnMessage
