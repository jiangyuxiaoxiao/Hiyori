"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/1-0:19
@Desc: 数据库存储
@Ver : 1.0.0
"""
from pathlib import Path
from os import path
import peewee

db_path = Path().absolute() / "Data" / "BlackHistory" / "ChatRecord.db"
db_path.parent.mkdir(exist_ok=True, parents=True)
db = peewee.SqliteDatabase(db_path)


# 聊天数据表
class ChatRecord(peewee.Model):
    ID = peewee.AutoField(primary_key=True, null=False)
    MessageID = peewee.IntegerField(default=None, null=True)
    ForwardMessageID = peewee.TextField(default=None, null=True)
    QQ = peewee.IntegerField(null=False)
    GroupID = peewee.IntegerField(null=False)
    DeleteFlag = peewee.BooleanField(default=False)

    class Meta:
        database = db
        table_name = "ChatRecord"


if not path.exists(db_path):
    db.connect()
    db.create_tables([ChatRecord])
    db.close()
