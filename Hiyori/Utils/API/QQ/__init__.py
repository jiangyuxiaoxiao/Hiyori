"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:51
@Desc: QQ服务封装
@Ver : 1.0.0
"""
from nonebot.adapters.onebot.v11 import Bot
from Hiyori.Utils.Database import DB_User


async def GetQQGrouperName(bot: Bot, QQ: int, Group: int, no_cache: bool = False) -> str:
    """
    获取Bot所在QQ群内群员姓名

    :param bot:
    :param QQ:
    :param Group:
    :param no_cache: 是否使用缓存
    :return:
    """
    # 设置了昵称则直接返回
    User = DB_User.getUser(QQ=QQ)
    if User.NickName != "":
        return User.NickName
    Info = await bot.get_group_member_info(group_id=Group, user_id=QQ, no_cache=no_cache)
    if QQ == 2327382838:
        return "魔法少女落漪漓"
    else:
        if Info["card"] == "":
            return Info["nickname"]
        else:
            return Info["card"]


async def GetQQStrangerName(bot: Bot, QQ: int, no_cache: bool = False) -> str:
    """
    获取陌生人姓名

    :param bot:
    :param QQ:
    :param no_cache: 是否使用缓存
    :return:
    """
    # 设置了昵称则直接返回
    Info = await bot.get_stranger_info(user_id=QQ, no_cache=no_cache)
    return Info["nickname"]

