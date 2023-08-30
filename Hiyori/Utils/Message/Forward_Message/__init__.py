"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:43
@Desc: 多条消息转发结点
@Ver : 1.0.0
"""
from nonebot.adapters.onebot.v11 import Bot


class Nodes:
    def __init__(self, msgID: int = 0, qID: int = 0, name: str = "", content: str = ""):
        """
        初始化函数

        :param msgID: 消息ID，当填写了消息ID后不用填后面的参数
        :param qID: 发送者QQ
        :param name: 发送者名字
        :param content: 发送内容
        """
        if qID == 0 and msgID == 0:
            self.nodes: list = []
        elif qID == 0:
            self.nodes: list = [{
                "type": "node",
                "data": {
                    "id": msgID
                }
            }]
        else:
            self.nodes: list = [{
                "type": "node",
                "data": {
                    "name": name,
                    "uin": qID,
                    "content": content
                }
            }]

    def __add__(self, other):
        if other is None:
            return self
        if isinstance(other, Nodes):
            self.nodes = self.nodes + other.nodes
        else:
            raise Exception
        return self

    def msg(self):
        """
        获取存储的消息
        """
        return self.nodes

    def clear(self):
        self.nodes = []
        return

    async def send_private_forward_msg(self, bot: Bot, QQ: int):
        """ 发送私聊转发消息"""

        await bot.call_api("send_private_forward_msg", user_id=QQ, messages=self.nodes)

    async def send_group_forward_msg(self, bot: Bot, GroupID: int):
        """ 发送群聊转发消息"""

        await bot.call_api("send_group_forward_msg", group_id=GroupID, messages=self.nodes)
