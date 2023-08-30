"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:44
@Desc: Hiyori权限级划分
@Ver : 1.0.0
"""
from nonebot.adapters import Bot, Event
from Hiyori.Utils.Database import DB_User
from nonebot.permission import Permission


def _HIYORI_OWNER(bot: Bot, event: Event) -> bool:
    """
    对应权限级Permission=0
    """
    if hasattr(event, "user_id"):
        QQ = event.user_id
        if DB_User.isOwner(QQ):
            return True
    return False


def _HIYORI_ADMIN(bot: Bot, event: Event) -> bool:
    """
    对应权限级Permission=0 or 1
    """
    if hasattr(event, "user_id"):
        QQ = event.user_id
        if DB_User.isAdmin(QQ):
            return True
    return False


HIYORI_OWNER = Permission(_HIYORI_OWNER)
HIYORI_ADMIN = Permission(_HIYORI_ADMIN)


