"""
@Author: Kasugano Sora
@Author-2: Zao
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/7/1-0:22
@LastDate: 2023/8/1-9:52
@Desc: 签到插件
@Ver : 1.0.0
"""
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Bot
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
from nonebot import get_driver
from nonebot.plugin import PluginMetadata
from nonebot.log import logger
from Hiyori.Utils.Database import DB_User, DB_Item
from Hiyori.Utils.Priority import Priority
from Hiyori.Utils.API.QQ import GetQQGrouperName, GetQQStrangerName
from Hiyori.Utils.Spider.WebShot import Web2ImgBytes
from .config import signInImages, Mode
import datetime
import requests
import random
import pathlib
import os

__plugin_meta__ = PluginMetadata(
    name="签到",  # 用于在菜单显示 用于插件开关
    description="不要忘了每日签到哦！连续签到有额外加成~",  # 用于在菜单中描述
    usage="#签到 【每日签到】\n"
          "#查看 【查看当前好感与金币】",
    extra={"CD_Weight": 0,  # 调用插件CD权重 不填的话不会触发权重插件
           "Group": "Daily",
           "Keep_On": False,
           "Type": "Normal_Plugin",
           }
)

# 预定义数值-收入
# 连续签到时收益提高
年收入: int = 43484  # 2023年城镇人均收入
收入福利系数: float = 0.3  # 上浮系数
日收入: int = int(年收入 * (1 + 收入福利系数) / 365)
收入波动幅度: int = int(日收入 * 0.2)  # 波动幅度
连续签到_收入奖励系数: float = 0.05  # 连续签到奖励
连续签到_最大收入奖励系数: float = 1.5  # 连续签到奖励上限
# 预定义数值-好感度
# 连续签到时收益提高
月好感度: int = 400
日好感度: int = int(月好感度 / 30)
好感度波动幅度: int = int(日好感度 * 0.2)  # 波动幅度
连续签到_好感度奖励系数: float = 0.05  # 连续签到奖励
连续签到_最大好感度奖励系数: float = 1.5  # 连续签到奖励上限

signIn = on_regex(r"^#?签到$", priority=Priority.普通优先级, block=False)
check = on_regex(r"^#查看$", priority=Priority.普通优先级, block=False)


@signIn.handle()
async def _(bot: Bot, event: MessageEvent):
    QQ = event.user_id
    User = DB_User.getUser(QQ)
    LastSignIn = str(User.SignInDate)
    Today = datetime.datetime.now()
    TodayStr = str(Today.year) + "-" + str(Today.month) + "-" + str(Today.day)
    ComboDay = 0
    # 未签到
    if LastSignIn == "":
        ComboDay = 0
    # 重复签到
    elif TodayStr == str(LastSignIn.split("@")[0]):
        if len(LastSignIn.split("@")) == 2:
            ComboDay = LastSignIn.split("@")[1]
            # Sora渲染
            if Mode.Sora:
                # 获取当前端口号
                conf = get_driver().config.dict()
                port = conf["port"]
                # 获取昵称
                if hasattr(event, "group_id"):
                    Name = await GetQQGrouperName(bot=bot, QQ=QQ, Group=event.group_id)
                else:
                    Name = await GetQQStrangerName(bot=bot, QQ=QQ)
                Ls = LastSignIn.split("@")[0]
                url = f"127.0.0.1:{port}/Sign/Sign.html?QQ={QQ}&&Name={Name}&&LastSignDate={Ls}" \
                      f"&&Gold={User.Money / 100}" \
                      f"&&Attitude={User.Attitude}&&HasSign=true&&SignCombo={ComboDay}"
                image = await Web2ImgBytes(url=url, width=800)
                msg = MessageSegment.at(QQ) + MessageSegment.image(image)
                await signIn.send(msg)
            else:
                message = MessageSegment.at(event.user_id) + MessageSegment.text(f"你已经签到过了哦\n"
                                                                                 f"当前存款{User.Money / 100}妃爱币\n"
                                                                                 f"当前妃爱对你的好感度为{User.Attitude}\n"
                                                                                 f"已连续签到{ComboDay}天")
                await signIn.send(message)
        else:
            logger.error(f"签到记录出错，记录信息{LastSignIn}，QQ={event.user_id}")
        return
    else:
        # 获取连续签到天数
        if len(LastSignIn.split("@")) != 2:
            logger.error(f"签到记录出错，记录信息{LastSignIn}，QQ={event.user_id}")
            return
        ComboDay = LastSignIn.split("@")[1]
        if not ComboDay.isdigit():
            logger.error(f"签到记录出错，记录信息{LastSignIn}，QQ={event.user_id}")
            return
        # 判断签到是否连续
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        yesterdayStr = str(yesterday.year) + "-" + str(yesterday.month) + "-" + str(yesterday.day)
        if yesterdayStr == LastSignIn.split("@")[0]:
            ComboDay = int(ComboDay)
        else:
            # 提取物品数量
            亚托莉断签保护卡 = DB_Item.getUserItem(QQ=event.user_id, ItemName="亚托莉断签保护卡")
            芳乃断签保护卡 = DB_Item.getUserItem(QQ=event.user_id, ItemName="芳乃断签保护卡")
            妃爱断签保护卡 = DB_Item.getUserItem(QQ=event.user_id, ItemName="妃爱断签保护卡")
            # 判断断签卡
            "数据库日期存储格式示范 2023-6-11@2"
            LastSignInStr = LastSignIn.split("@")[0]
            LastSignInStrs = LastSignInStr.split("-")
            try:
                Year = int(LastSignInStrs[0])
                Month = int(LastSignInStrs[1])
                Day = int(LastSignInStrs[2])
                LastDay = datetime.date(Year, Month, Day)
            except Exception:
                LastDay = yesterday
            ComboDay = int(ComboDay)
            # 当断签不超过1天
            if yesterday - LastDay <= datetime.timedelta(days=1):
                if 亚托莉断签保护卡.Quantity >= 1:
                    亚托莉断签保护卡.Quantity -= 1
                    亚托莉断签保护卡.save()
                elif 芳乃断签保护卡.Quantity >= 1:
                    芳乃断签保护卡.Quantity -= 1
                    芳乃断签保护卡.save()
                elif 妃爱断签保护卡.Quantity >= 1:
                    妃爱断签保护卡.Quantity -= 1
                    妃爱断签保护卡.save()
                else:
                    ComboDay = 0
            # 当断签不超过5天
            elif yesterday - LastDay <= datetime.timedelta(days=5):
                if 芳乃断签保护卡.Quantity >= 1:
                    芳乃断签保护卡.Quantity -= 1
                    芳乃断签保护卡.save()
                elif 妃爱断签保护卡.Quantity >= 1:
                    妃爱断签保护卡.Quantity -= 1
                    妃爱断签保护卡.save()
                else:
                    ComboDay = 0
            # 断签超过5天
            else:
                if 妃爱断签保护卡.Quantity >= 1:
                    妃爱断签保护卡.Quantity -= 1
                    妃爱断签保护卡.save()
                else:
                    ComboDay = 0
    AddMoney = int(random.randint(日收入 - 收入波动幅度, 日收入 + 收入波动幅度) * (1 + 收入福利系数) * min(
        (1 + 连续签到_收入奖励系数 * ComboDay),
        1 + 连续签到_最大收入奖励系数))
    AddAttitude = int(random.randint(日好感度 - 好感度波动幅度, 日好感度 + 好感度波动幅度) * min(
        (1 + 连续签到_好感度奖励系数 * ComboDay),
        (1 + 连续签到_最大好感度奖励系数)
    ))
    ComboDay = ComboDay + 1
    User.Money = User.Money + AddMoney * 100
    User.Attitude = User.Attitude + AddAttitude
    User.SignInDate = TodayStr + "@" + str(ComboDay)
    DB_User.updateUser(User)

    # 图片渲染
    if Mode.Zao:
        # 枣子渲染
        Images = len(signInImages)
        Image = random.randint(0, Images - 1)
        Image = signInImages[Image]
        image_path_b = os.path.abspath(f"./Src/Image/{Image}")
        image_path_a = f"http://q1.qlogo.cn/g?b=qq&nk={QQ}&s=640"
        positions_a = [(100, 100)]  # 图片A的位置
        positions_text = [(420, 190), (130, 530), (110, 410), (130, 450), (130, 490), (10, 680), (130, 570)]  # 文字的位置
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        texts = [f"Accumulative check-in for {ComboDay} days", f"当前好感: {User.Attitude}", "今日签到~", f"好感度 + {AddAttitude}", f"妃爱币 + {AddMoney}",
                 f"妃爱@2023", f"时间: {now}"]
        font_path = f"./Data/fonts/FZSJ-QINGCRJ.ttf"
        font_size = 36
        font_color = (211, 64, 33)
        resize = (200, 200)
        ImagePath = overlay_images_with_text(image_path_b, image_path_a, positions_a, positions_text, texts, font_path, font_size, font_color, QQ, resize)
        ImagePath = os.path.abspath(ImagePath)
        message = MessageSegment.at(event.user_id)
        ImagePath = pathlib.Path(ImagePath).as_uri()
        message = message + MessageSegment.image(ImagePath)
        await signIn.send(message)
    else:
        # 获取当前端口号
        conf = get_driver().config.dict()
        port = conf["port"]
        # 获取昵称
        if hasattr(event, "group_id"):
            Name = await GetQQGrouperName(bot=bot, QQ=QQ, Group=event.group_id)
        else:
            Name = await GetQQStrangerName(bot=bot, QQ=QQ)
        # 处理最后签到日期
        Ls = User.SignInDate.split("@")[0]
        url = f"127.0.0.1:{port}/Sign/Sign.html?QQ={QQ}&&Name={Name}&&LastSignDate={Ls}" \
              f"&&AddGold={AddMoney}&&AddAttitude={AddAttitude}&&Gold={User.Money/100}" \
              f"&&Attitude={User.Attitude}&&HasSign=false&&SignCombo={{ComboDay}}"
        image = await Web2ImgBytes(url=url,width=800)
        msg = MessageSegment.at(QQ) + MessageSegment.image(image)
        await signIn.send(msg)


@check.handle()
async def _(event: MessageEvent):
    QQ = event.user_id
    User = DB_User.getUser(QQ)
    LastSignIn = str(User.SignInDate)
    ComboDay = 0
    # 未签到
    if LastSignIn == "":
        ComboDay = 0
    else:
        ComboDay = LastSignIn.split("@")[1]
        if not ComboDay.isdigit():
            ComboDay = 0
        else:
            ComboDay = int(ComboDay)
    message = MessageSegment.at(event.user_id) + MessageSegment.text(f"你的存款为{User.Money / 100}妃爱币\n"
                                                                     f"妃爱对你的好感度为{User.Attitude}\n"
                                                                     f"已连续签到{ComboDay}天")
    await check.send(message)
    return


def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))


def overlay_images_with_text(image_path_b, image_url_a, positions_a, positions_text, texts, font_path, font_size, font_color, QQ, resize=None):
    img_b = Image.open(image_path_b)

    img_a = download_image(image_url_a)

    if resize:
        img_a = img_a.resize(resize, resample=Image.LANCZOS)

    overlay = Image.new("RGBA", img_b.size, (255, 255, 255, 128))

    img_a = crop_to_circle(img_a)
    img_a = add_transparency_around_circle(img_a, 50)

    for position_a in positions_a:
        overlay.paste(img_a, position_a, img_a)

    draw = ImageDraw.Draw(overlay)
    font = ImageFont.truetype(font_path, font_size) if font_path else None
    for position_text, text in zip(positions_text, texts):
        draw.text(position_text, text, font=font, fill=font_color)

    img_b = Image.alpha_composite(img_b.convert("RGBA"), overlay)
    img_b_path = f"./Data/SignIn/{QQ}.png"

    img_b.save(img_b_path, format="PNG", optimize=True)
    return img_b_path


def crop_to_circle(img):
    size = img.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    result = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    result.putalpha(mask)
    return result


def add_transparency_around_circle(img, alpha_radius):
    alpha = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(alpha)
    size = min(img.size)
    draw.ellipse((0, 0, size, size), fill=255, outline=0)
    alpha = alpha.resize(img.size, Image.LANCZOS)
    img.putalpha(alpha)
    return img
