import aiohttp
from nonebot.plugin import on_regex
from nonebot.plugin import on_keyword
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent
from pydantic import BaseModel
from nonebot.plugin import PluginMetadata
from Hiyori.Utils.Priority import Priority


class Config(BaseModel):
    custom: str = ""


ygo = on_regex(pattern="^#小程序查价\ ", priority=Priority.普通优先级)
ygoinner = on_regex(pattern="^#单卡查价\ ", priority=Priority.普通优先级)
ygorat = on_regex(pattern="^#稀有度\ ", priority=Priority.普通优先级)
ygosearch = on_regex(pattern="^#查价\ ", priority=Priority.普通优先级)
glocarduser = {}
ygohelp = on_keyword(['/ygohelp', '/帮助'], priority=Priority.普通优先级)

__plugin_meta__ = PluginMetadata(
    name="游戏王查价",
    description="获取集换社卡价",
    usage="#小程序查价 卡名 【查询多张卡片】\n"
          "#单卡查价 卡名 【精确单卡查价】\n"
          "#查价 卡名【根据罕贵查价】",
    extra={
        "CD_Weight": 2,
        "example": "#小程序查价 灰流丽",
        "version": "0.3.9",
        "Keep_On": False,
        "Type": "Normal_Plugin",
    },
)


@ygohelp.handle()
async def ygohelpMethod(bot: Bot, event: Event):
    await bot.send(event=event, message="使用“下划线[#]+指令”来开始使用"
                                        "\n当前可使用功能有：\n"
                                        "查询多张卡片[#小程序查价+卡名]\n"
                                        "精确单卡查价[#单卡查价+卡名]\n"
                                        "根据罕贵查价[#查价+卡名]\n")


@ygosearch.handle()
async def ygoratMethod(bot: Bot, event: Event):
    key = str(event.message).strip()[3:].strip()
    datas = await maintotal(key)
    msg = None
    rarity = ''
    global glocarduser
    glocarduser[str(event.user_id)] = datas['data']
    total = str(datas['total'])
    for data in datas['data']:
        rarity = rarity + data['rarity'] + ' '
    msg = Message('当前存在的稀有度有' + rarity)
    msg += Message('总计查询到' + total + '张卡片，请继续输入"#稀有度 罕贵"进行精确查价。')
    for data in datas['data']:
        msg += MessageSegment.image(data['image_url'])
    if isinstance(event, GroupMessageEvent):
        await send_forward_msg_group(bot, event, "黑猫卡牌", msg if msg else ["没有此关键字的卡片"])
    elif isinstance(event, PrivateMessageEvent):
        await send_forward_msg_person(bot, event, "黑猫卡牌", msg if msg else ["没有此关键字的卡片"])


@ygorat.handle()
async def ygoratMethod(bot: Bot, event: Event):
    key = str(event.message).strip()[4:].strip()
    msg = None
    card = glocarduser[str(event.user_id)]
    datas = await mainrarity(card[0]['name_cn'], key)
    if datas['data']:
        for data in datas['data']:
            htmls = await maininfo(data['id'])
            for html in htmls['data']:
                msg += (Message('卖家名:' + html['seller_username'] + '\n'
                                + '卖家id:' + str(html['seller_user_id']) + '\n'
                                + '罕贵:' + data['rarity'] + '\n'
                                + '数量:' + str(html['quantity']) + '\n'
                                + '价格:' + data['min_price'])
                        + MessageSegment.image(html['card_version_image']))
            if isinstance(event, GroupMessageEvent):
                await send_forward_msg_group(bot, event, "黑猫卡牌", msg if msg else ["没有此关键字的卡片"])
            elif isinstance(event, PrivateMessageEvent):
                await send_forward_msg_person(bot, event, "黑猫卡牌", msg if msg else ["没有此关键字的卡片"])
            msg = None
    else:
        await bot.send(event=event, message="没有该罕贵的卡片")


@ygoinner.handle()
async def ygoinnerMethod(bot: Bot, event: Event):
    # 切割字符串
    key = str(event.message).strip()[5:].strip()
    msg = None
    solocard = await main(key)
    cardid = None
    if solocard[0] != None:
        cardid = solocard[0]['id']
        cardrat = solocard[0]['rarity']
    datas = await maininfo(cardid)
    for data in datas['data']:
        msg += (Message(
            '卖家名:' + data['seller_username'] + '\n' + '卖家id:' + str(data['seller_user_id']) + '\n' + '数量:' + str(
                data['quantity']) + '\n' + '价格:' + data['min_price']) + MessageSegment.image(
            data['card_version_image']))
    if isinstance(event, GroupMessageEvent):
        await send_forward_msg_group(bot, event, "黑猫卡牌", msg if msg else ["没有此关键字的卡片"])
    elif isinstance(event, PrivateMessageEvent):
        await send_forward_msg_person(bot, event, "黑猫卡牌", msg if msg else ["没有此关键字的卡片"])


@ygo.handle()
async def ygoMethod(bot: Bot, event: Event):
    # 切割字符串
    key = str(event.message).strip()[6:].strip()
    datas = await main(key)
    msg = None
    for data in datas:
        msg += (Message(data['name_cn'] + '\n' + '卡片id:' + str(data['id']) + '\n' + '卡片序号:' + data[
            'number'] + '\n' + '罕贵度:' + data['rarity'] + '\n' + '当前最低价:' + data[
                            'min_price'] + '\n') + MessageSegment.image(data['image_url']))
    if isinstance(event, GroupMessageEvent):
        await send_forward_msg_group(bot, event, "黑猫卡牌", msg if msg else ["没有此关键字的卡片"])
    elif isinstance(event, PrivateMessageEvent):
        await send_forward_msg_person(bot, event, "黑猫卡牌", msg if msg else ["没有此关键字的卡片"])


async def fetch(session, url, headers):
    async with session.get(url=url, headers=headers) as response:
        return await response.json()


async def main(key):
    async with aiohttp.ClientSession() as session:
        url = f"https://api.jihuanshe.com/api/market/search/match-product?keyword={key}&game_key=ygo&game_sub_key=ocg&page=1&token="
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'referer': 'https://api.jihuanshe.com/',
        }
        html = await fetch(session, url, headers)
        total = html['total']
        per_page = html['per_page']
        froms = html['from']
        tos = html['from']
        datas = html['data']
        return datas


async def maintotal(key):
    async with aiohttp.ClientSession() as session:
        url = f"https://api.jihuanshe.com/api/market/search/match-product?keyword={key}&game_key=ygo&game_sub_key=ocg&page=1&token="
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'referer': 'https://api.jihuanshe.com/',
        }
        html = await fetch(session, url, headers)
        return html


async def mainrarity(key, rarity):
    async with aiohttp.ClientSession() as session:
        url = f"https://api.jihuanshe.com/api/market/search/match-product?keyword={key}&game_key=ygo&game_sub_key=ocg&rarity={rarity}&page=1&token="
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'referer': 'https://api.jihuanshe.com/',
        }
        html = await fetch(session, url, headers)
        return html


async def maininfo(key):
    async with aiohttp.ClientSession() as session:
        url = f"https://api.jihuanshe.com/api/market/card-versions/products?card_version_id={key}&condition=1&page=1&game_key=ygo&game_sub_key=ocg&token="
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'referer': 'https://api.jihuanshe.com/',
        }
        html = await fetch(session, url, headers)
        return html


async def maintotal(key):
    async with aiohttp.ClientSession() as session:
        url = f"https://api.jihuanshe.com/api/market/search/match-product?keyword={key}&game_key=ygo&game_sub_key=ocg&page=1&token="
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'referer': 'https://api.jihuanshe.com/',
        }
        html = await fetch(session, url, headers)
        return html


# 合并消息
async def send_forward_msg_group(
        bot: Bot,
        event: GroupMessageEvent,
        name: str,
        msgs: [],
):
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": 3227262094, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    await bot.call_api(
        "send_group_forward_msg", group_id=event.group_id, messages=messages
    )


# 合并单独消息
async def send_forward_msg_person(
        bot: Bot,
        event: PrivateMessageEvent,
        name: str,
        msgs: [],
):
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": 3227262094, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    await bot.call_api(
        "send_private_forward_msg", user_id=event.user_id, messages=messages
    )
