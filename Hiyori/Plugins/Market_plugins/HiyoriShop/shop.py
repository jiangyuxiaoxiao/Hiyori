"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:44
@Desc: 
@Ver : 1.0.0
"""
from Hiyori.Utils.Shop import Shops, Shop
from Hiyori.Utils.Shop.BasicFunction import *
from .item import 白银会员卡


def HiyoriShopInit():
    hiyoriShop = Shop(name="妃爱", description="妃爱小卖部")
    hiyoriShop.addItem(itemName="白银会员卡",
                       description="白银会员卡，购买部分物品享受9折优惠，使用该物品来查看相关说明", price=0,
                       need_attitude=1000,
                       functions={"购买前触发函数": 唯一物品, "使用时触发函数": 白银会员卡})
    hiyoriShop.addItem(itemName="亚托莉断签保护卡",
                       description="高性能萝卜籽！断签保护卡，当断签时间不超过1天时自动消耗。注意，若断签后已经签过到则无法恢复，且断签的时间跨度无法叠加。",
                       price=100,
                       need_attitude=200, functions={})
    hiyoriShop.addItem(itemName="芳乃断签保护卡",
                       description="神社祈福！断签保护卡，当断签时间不超过5天时自动消耗。", price=500,
                       need_attitude=500, functions={})
    hiyoriShop.addItem(itemName="妃爱断签保护卡",
                       description="妹妹赛高！断签保护卡，断签时自动消耗。", price=2000,
                       need_attitude=1500, functions={})
    Shops.addShop(hiyoriShop)
