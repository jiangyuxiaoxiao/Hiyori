"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:51
@Desc: QQ服务封装
@Ver : 1.0.0
"""
import httpx
from nonebot.adapters.onebot.v11 import Bot
from Hiyori.Utils.Database import DB_User
from typing import Optional


async def GetQQGrouperName(bot: Bot, QQ: int, Group: int, no_cache: bool = False) -> str:
    """
    获取Bot所在QQ群内群员姓名，若用户设置了昵称则返回昵称，否则返回群内名称。若设置了群名片则返回群名片，否则返回QQ昵称。

    :param bot: onebot实例
    :param QQ: QQ号
    :param Group: 群号
    :param no_cache: 是否使用缓存
    :return: 名称
    """
    # 设置了昵称则直接返回
    User = DB_User.getUser(QQ=QQ)
    if User.NickName != "":
        return User.NickName
    Info = await bot.get_group_member_info(group_id=Group, user_id=QQ, no_cache=no_cache)
    if Info["card"] == "":
        return Info["nickname"]
    else:
        return Info["card"]


async def GetQQStrangerName(bot: Bot, QQ: int, no_cache: bool = False) -> str:
    """
    获取陌生人姓名

    :param bot: onebot实例
    :param QQ: QQ号
    :param no_cache: 是否使用缓存
    :return:
    """
    # 设置了昵称则直接返回
    Info = await bot.get_stranger_info(user_id=QQ, no_cache=no_cache)
    return Info["nickname"]


async def GetQQAvatarB64(qq: int) -> Optional[bytes]:
    """
    说明:
        快捷获取用户头像的Base64编码
    参数:
        :param qq: qq号
    """
    url = f"http://q1.qlogo.cn/g?b=qq&nk={qq}&s=160"
    async with httpx.AsyncClient() as client:
        for _ in range(3):
            try:
                return (await client.get(url)).content
            except TimeoutError:
                pass
    return None


async def GetQQAvatarUrl(QQ: int, Size: int = 640) -> str:
    """
    获取QQ头像Url，默认大小640*640。

    :param QQ: QQ号
    :param Size: 枚举整数，可取值：100、640
    :return: Url
    """
    return f"https://q1.qlogo.cn/g?b=qq&nk={QQ}&s={Size}"


def GetGroupAvatarUrl(Group: int, Size: int = 640) -> str:
    """
    获取群头像Url，默认大小640*640。

    :param Group: 群号
    :param Size: 枚举整数，可取值：100、640
    :return Url: 群头像url
    """
    return f"https://p.qlogo.cn/gh/{Group}/{Group}/{Size}"


async def GetGroupName(bot: Bot, Group: int) -> str:
    """
    获取群名
    :param bot: bot实例
    :param Group: 群号
    :return 群名
    """
    groupInfo = await bot.get_group_info(group_id=Group)
    return groupInfo["group_name"]
