"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/09/28-08:55
@Desc: 百川2-7B 本地api对接
@Ver : 1.0.0
"""
import aiohttp
from collections import deque
from .config import baiChuanConfig
from Hiyori.Utils.Message.Forward_Message import Nodes


class BaiChuanChatter:
    def __init__(self, self_id: int, user_id: int, maxLength: int = baiChuanConfig.maxLength, user_name: str = "用户", self_name: str = "妃爱",
                 prompts: list[str] = None):
        """

        :param maxLength: 最长对话轮数，按队列顺序先进先出进行删除。当maxLength=0时不进行删除
        """
        self.message = deque()
        self.maxLength = maxLength
        self.user_id = user_id
        self.user_name = user_name
        self.self_id = self_id
        self.self_name = self_name
        self.prompts = prompts

    async def ask(self, msg: str) -> str:
        if not isinstance(msg, str):
            raise TypeError
        if msg == "":
            raise ValueError("请勿输入空对话")
        if self.maxLength != 0:
            if len(self.message) > self.maxLength * 2:
                self.message.popleft()
                self.message.popleft()
        sendMsg = []
        if self.prompts is not None:
            for prompt in self.prompts:
                sendMsg.append({"role": "user", "content": prompt})
        # sendMsg = [{"role": "user", "content": f"你叫{self.self_name}，是我的可爱的妹妹。"}] + list(self.message)
        sendMsg = list(self.message)
        sendMsg.append({"role": "user", "content": msg})
        url = f"{baiChuanConfig.host}:{baiChuanConfig.port}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"history": sendMsg}) as response:
                response = await response.text()
                response = response.strip('"')
                response = response.replace('\\"', '\"')
                response = response.replace("\\n", "\n")
                # 添加历史记录
                self.message.append({"role": "user", "content": msg})
                self.message.append({'role': 'assistant', 'content': response})
                return response

    def clear(self):
        self.message.clear()

    def getHistory(self) -> Nodes:
        """
        返回会话转发结点
        """
        msgs = list(self.message)
        node = Nodes()
        for msg in msgs:
            if msg["role"] == "user":
                node += Nodes(qID=self.user_id, name=self.user_name, content=msg["content"])
            else:
                node += Nodes(qID=self.self_id, name=self.self_name, content=msg["content"])
        return node
