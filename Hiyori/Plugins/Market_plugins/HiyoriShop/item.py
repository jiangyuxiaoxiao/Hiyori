"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:43
@Desc: 妃爱商店物品功能实现
@Ver : 1.0.0
"""
from Hiyori.Utils.Database import DB_User


def 白银会员卡(QQ: int, GroupID: int, Quantity: int, **kwargs) -> (bool, str):
    return True, "持有该会员卡在以下商店享受九折优惠：\n" \
                 "1.群友商店\n" \
                 "2.妃爱小卖部"
