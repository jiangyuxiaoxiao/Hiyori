"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/8-11:56
@Desc: 商店模块
@Ver : 1.0.0
"""
from Hiyori.Utils.Shop import Shops, Shop
from .items import 中文翻译模块, 文言文翻译模块, 广东话翻译模块, 英语翻译模块, 韩语翻译模块, 德语翻译模块, 日语翻译模块, 法语翻译模块, 俄语翻译模块


def TranslateShopInit():
    TranslateShop = Shop(name="翻译模块商店", description="神秘模块商店", anonymous=True)
    TranslateShop.addItem(
        中文翻译模块(name="中文翻译模块", description="使用后可以切换中文翻译模组激活状态", price=2000, need_attitude=500, anonymous=True))
    TranslateShop.addItem(
        文言文翻译模块(name="文言文翻译模块", description="使用后可以切换文言文翻译模组激活状态", price=2000, need_attitude=500, anonymous=True))
    TranslateShop.addItem(
        广东话翻译模块(name="广东话翻译模块", description="使用后可以切换广东话翻译模组激活状态", price=2000, need_attitude=500, anonymous=True))
    TranslateShop.addItem(
        英语翻译模块(name="英语翻译模块", description="使用后可以切换英语翻译模组激活状态", price=2000, need_attitude=500, anonymous=True))
    TranslateShop.addItem(
        韩语翻译模块(name="韩语翻译模块", description="使用后可以切换韩语翻译模组激活状态", price=2000, need_attitude=500, anonymous=True))
    TranslateShop.addItem(
        德语翻译模块(name="德语翻译模块", description="使用后可以切换德语翻译模组激活状态", price=2000, need_attitude=500, anonymous=True))
    TranslateShop.addItem(
        日语翻译模块(name="日语翻译模块", description="使用后可以切换日语翻译模组激活状态", price=2000, need_attitude=500, anonymous=True))
    TranslateShop.addItem(
        法语翻译模块(name="法语翻译模块", description="使用后可以切换法语翻译模组激活状态", price=2000, need_attitude=500, anonymous=True))
    TranslateShop.addItem(
        俄语翻译模块(name="俄语翻译模块", description="使用后可以切换俄语翻译模组激活状态", price=2000, need_attitude=500, anonymous=True))
    Shops.addShop(TranslateShop)
