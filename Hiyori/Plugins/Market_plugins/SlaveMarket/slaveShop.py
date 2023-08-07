"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-23:56
@Desc: 群友商店
@Ver : 1.0.0
"""
from Hiyori.Utils.Shop import Shops, Shop
from .item import *
from Hiyori.Utils.Shop.BasicFunction import 唯一物品


def SlaveShopInit():
    slaveShop = Shop(name="群友", description="出售群友市场相关的商品")
    slaveShop.addItem(itemName="猫娘变身器",
                      description="消耗品，神秘的粉色开关，隐隐约约飘出巧克力与香子兰的香气。使用后变成可爱的猫娘，颜值提升，体质下降。",
                      price=1000, functions={"使用时触发函数": 猫娘变身器})
    slaveShop.addItem(itemName="白丝连裤袜", description="消耗品，香香的白丝，穿上后颜值提高。", price=2000,
                      functions={"使用时触发函数": 白丝连裤袜})
    slaveShop.addItem(itemName="重开模拟器", description="消耗品，使用后重新随机现代世界观的三维属性【颜值,智力,体质】。",
                      price=200, functions={"使用时触发函数": 重开模拟器})
    slaveShop.addItem(itemName="灵魂宝石", description="唯一性物品，可以签订契约成为魔法少女，提高自身的体质。",
                      price=4000, need_attitude=400,
                      functions={"使用时触发函数": 灵魂宝石, "购买前触发函数": 唯一物品})
    slaveShop.addItem(itemName="世界线演算装置",
                      description="消耗品，使用后消耗背包所有的重开模拟器进行世界线演算后进入最优分支。",
                      price=2000, functions={"使用时触发函数": 世界线演算装置}, need_attitude=200)
    slaveShop.addItem(itemName="粉色项圈",
                      description="消耗品，对你自己或者你老婆使用可以获得神秘效果，可重复使用，每个项圈有效期一天。当不指定人时视为对自己使用",
                      price=200, functions={"使用时触发函数": 粉色项圈}, hasTarget=True, need_attitude=800)
    slaveShop.addItem(itemName="结婚戒指", description="双人互相指定时结婚",
                      price=10000, functions={"购买前触发函数": 唯一物品, "使用时触发函数": 结婚戒指}, hasTarget=True, need_attitude=1000)
    Shops.addShop(slaveShop)
