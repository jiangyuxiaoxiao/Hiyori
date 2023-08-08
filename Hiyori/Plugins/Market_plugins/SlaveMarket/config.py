"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:51
@Desc: 
@Ver : 1.0.0
"""
"""
群友市场相关Config
"""


class SlaveConfig:
    # 奴隶每次转让价格上涨
    AddPrice = 20
    # 本人获取金币系数
    SlaveIncome = 0.1
    # 奴隶主获取金币系数
    OwnerIncome = 1
    # 每天购买上限
    MaxDailyPurchase = 5
    # 奴隶金币上限
    MaxSlaveIncome = 200
    # 购物车目录
    CartFile = "./Data/SlaveMarket/ShoppingCart.json"
    CartDir = "./Data/SlaveMarket/ShoppingCart"
