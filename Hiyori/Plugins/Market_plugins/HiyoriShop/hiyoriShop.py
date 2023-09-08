"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:44
@Desc: 
@Ver : 1.0.0
"""
from Hiyori.Utils.Shop import Shops, Shop, Item

from .item import 白银会员卡, 神秘模块抽奖券


def HiyoriShopInit():
    hiyoriShop = Shop(name="妃爱商店", description="妃爱小卖部")
    hiyoriShop.addItem(白银会员卡(name="白银会员卡", description="白银会员卡，购买部分物品享受9折优惠，使用该物品来查看相关说明", price=0, need_attitude=1000))
    hiyoriShop.addItem(Item(name="亚托莉断签保护卡",
                            description="高性能萝卜籽！断签保护卡，当断签时间不超过1天时自动消耗。注意，若断签后已经签过到则无法恢复，且断签的时间跨度无法叠加。",
                            price=100, need_attitude=200))
    hiyoriShop.addItem(Item(name="芳乃断签保护卡",
                            description="神社祈福！断签保护卡，当断签时间不超过5天时自动消耗。",
                            price=500, need_attitude=500))
    hiyoriShop.addItem(Item(name="穹妹断签保护卡",
                            description="妹妹赛高！断签保护卡，断签时自动消耗。",
                            price=2000, need_attitude=1500))
    hiyoriShop.addItem(神秘模块抽奖券(name="神秘模块抽奖券", description="使用后抽取神秘模块", price=1000))
    Shops.addShop(hiyoriShop)
