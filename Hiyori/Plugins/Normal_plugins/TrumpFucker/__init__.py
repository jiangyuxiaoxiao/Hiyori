"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/1-0:26
@Desc: 群聊记录制作
@Ver : 1.0.0
"""
from nonebot import on_regex
from nonebot.params import Received
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.exception import RejectedException
from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.Message.Forward_Message import Nodes

__plugin_meta__ = PluginMetadata(
    name="特朗普被狗日了",  # 用于在菜单显示 用于插件开关
    description="QQ聊天记录生成",  # 用于在菜单中描述
    usage="输入#特朗普被狗日了或#伪造聊天记录 开启互动对话\n"
          "仅可在群聊中使用",
    extra={"CD_Weight": 0,  # 调用插件CD权重 不填的话不会触发权重插件
           "example": "",
           "Group": "Daily",
           "version": "1.0",
           "Keep_On": False,
           "Type": "Normal_Plugin",
           }
)

FakeMessage = on_regex(r"(^#特朗普被狗日了$)|(^#伪造聊天记录$)", priority=Priority.普通优先级, block=True)
ForwardMessages: dict[int, Nodes] = dict()
UserCount: dict[int, int] = dict()


@FakeMessage.handle()
async def _(event: GroupMessageEvent):
    global ForwardMessages, UserCount
    QQ = event.user_id
    ForwardMessages[QQ] = Nodes()
    UserCount[QQ] = 0
    await FakeMessage.send("请用@用户+消息或者QQ号+空格+消息的方式设置聊天记录发送者及发送内容\n"
                           "若未输入用户则默认为自己\n"
                           "例如@奥观海 特朗普被狗日了\n"
                           "@希拉里 真的吗？\n"
                           "@奥观海 真的。\n"
                           "注意，@对应人的消息会自带一个空格，因此无需补充空格\n"
                           "聊天记录最长不超过99条\n"
                           "请开始逐条输入聊天\n"
                           "输入END或者end结束聊天记录制作")


@FakeMessage.receive("")
async def _(bot: Bot, event: GroupMessageEvent = Received("")):
    global ForwardMessages, UserCount
    GroupID = event.group_id
    message = event.raw_message
    # 捕获RejectException外的异常，通知用户流程终止。
    try:
        if message == "END" or message == "end":
            QQ = event.user_id
            await ForwardMessages[QQ].send_group_forward_msg(bot=bot, GroupID=GroupID)
            # await bot.call_api("send_group_forward_msg", **{"group_id": GroupID, "messages": UserInfo[QQ].msg()})
        else:
            # QQ号获取
            messages = message.split(" ", 1)
            QQ = 0
            # 未填QQ号。默认自己发送
            if len(messages) == 1:
                QQ = event.user_id
                message = messages[0]
            else:
                message = messages[1]
                # 直接发送QQ号
                if messages[0].isdigit():
                    QQ = int(messages[0])
                # @形式发送
                else:
                    messages[0] = messages[0].replace("[CQ:at,qq=", "")
                    messages[0] = messages[0].replace("]", "")
                    if messages[0].isdigit():
                        QQ = int(messages[0])
                    else:
                        await FakeMessage.reject("请输入正确的QQ号")
            # 消息收集 若群中不存在，则调用get_stranger_info
            GroupMembers = await bot.get_group_member_list(group_id=GroupID)
            Name = ""
            # 遍历查找群中是否存在对应用户
            for GroupMember in GroupMembers:
                if GroupMember["user_id"] == QQ:
                    if GroupMember["card"] != "":
                        Name = GroupMember["card"]
                    else:
                        Name = GroupMember["nickname"]
                    break
            # 群中不存在则调用api get_stranger_info
            if Name == "":
                Info = await bot.get_stranger_info(user_id=QQ, no_cache=False)
                if "nickname" in Info.keys():
                    Name = Info["nickname"]
                else:
                    Name = ""
            if event.user_id not in ForwardMessages.keys():
                ForwardMessages[event.user_id] = Nodes()
            ForwardMessages[event.user_id] = ForwardMessages[event.user_id] + Nodes(qID=QQ, name=Name, content=message)
            UserCount[event.user_id] = UserCount[event.user_id] + 1
            if UserCount[event.user_id] >= 99:
                GroupID = event.group_id
                await bot.call_api("send_group_forward_msg", **{"group_id": GroupID, "messages": ForwardMessages[QQ].msg()})
            else:
                await FakeMessage.reject()
    except Exception as e:
        if isinstance(e, RejectedException):
            raise RejectedException
        else:
            await FakeMessage.send("API调用异常，对话流程已终结")
