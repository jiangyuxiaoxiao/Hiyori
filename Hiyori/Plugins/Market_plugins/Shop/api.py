"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/8-10:54
@Desc: 商店api
@Ver : 1.0.0
"""

from nonebot import get_asgi
from fastapi.responses import JSONResponse

from Hiyori.Utils.Shop import Shops
from Hiyori.Utils.API.Hiyori import HiyoriCode

app = get_asgi()


@app.get("/Plugins/Market_plugins/Shop/ShopInfo", response_class=JSONResponse)
async def info(shopName: str):
    info = {
        "code": HiyoriCode.OK,
        "info": []
    }
    if shopName != "all":
        if shopName not in Shops.shops.keys():
            info["code"] = HiyoriCode.ParamsOutOfRange
            return info
        else:
            allShops = [Shops.shops[shopName]]
    else:
        allShops = Shops.shops.values()
    for shop in allShops:
        shopInfo = {
            "name": shop.name,
            "description": shop.description,
            "items": []
        }
        for item in shop.items.values():
            shopInfo["items"].append(
                {
                    "name": item.name,
                    "description": item.description,
                    "price": item.price,
                    "need_attitude": item.need_attitude,
                    "hasTarget": item.hasTarget,
                    "anonymous": item.anonymous,
                }
            )
        info["info"].append(shopInfo)
    return info
