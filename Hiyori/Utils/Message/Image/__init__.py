"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/8/1-21:40
@Desc: 提取消息中的所有图片链接
@Ver : 1.0.0
"""
import asyncio
import pathlib
import base64
import os
import json
import uuid
from io import BytesIO
from pathlib import Path
from PIL.ImageFont import FreeTypeFont
import imagehash
from imagehash import ImageHash
from typing import List, Literal, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from nonebot.adapters.onebot.v11 import Message, MessageSegment

FONT_PATH = Path() / "Data" / "fonts"

ModeType = Literal[
    "1", "CMYK", "F", "HSV", "I", "L", "LAB", "P", "RGB", "RGBA", "RGBX", "YCbCr"
]

def get_img_hash(image_file: Union[str, Path]) -> ImageHash:
    """
    说明:
        获取图片的hash值
    参数:
        :param image_file: 图片文件路径
    """
    with open(image_file, "rb") as fp:
        hash_value = imagehash.average_hash(Image.open(fp))
    return hash_value


def face(id_: int) -> MessageSegment:
    """
    说明:
        生成一个 MessageSegment.face 消息
    参数:
        :param id_: 表情id
    """
    return MessageSegment.face(id_)

def get_message_img(data: Union[str, Message]) -> List[str]:
    """
    说明:
        获取消息中所有的 图片 的链接
    参数:
        :param data: event.json()
    """
    img_list = []
    if isinstance(data, str):
        event = json.loads(data)
        if data and (message := event.get("message")):
            for msg in message:
                if msg["type"] == "image":
                    img_list.append(msg["data"]["url"])
    else:
        for seg in data["image"]:
            img_list.append(seg.data["url"])
    return img_list


def ImageMessage(Path: str = None,b64: Optional[str] = None,) -> MessageSegment:
    """
    将图片的路径以及图片base64编码转换为OneBot v11标准的MessageSegment

    :param Path: 图片路径，支持绝对路径与相对路径 b64:图片的base64编码
    :return: MessageSegment
    """
    if b64:
        file = b64 if b64.startswith("base64://") else ("base64://" + b64)
        return MessageSegment.image(file)
    else:
        Path = os.path.abspath(Path)
        Path = pathlib.Path(Path).as_uri()
        return MessageSegment.image(Path)


class BuildImage:
    """
    快捷生成图片与操作图片的工具类
    """

    def __init__(
        self,
        w: int,
        h: int,
        paste_image_width: int = 0,
        paste_image_height: int = 0,
        paste_space: int = 0,
        color: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]] = None,
        image_mode: ModeType = "RGBA",
        font_size: int = 10,
        background: Union[Optional[str], BytesIO, Path] = None,
        font: str = "yz.ttf",
        ratio: float = 1,
        is_alpha: bool = False,
        plain_text: Optional[str] = None,
        font_color: Optional[Union[str, Tuple[int, int, int]]] = None,
        **kwargs,
    ):
        """
        参数:
            :param w: 自定义图片的宽度，w=0时为图片原本宽度
            :param h: 自定义图片的高度，h=0时为图片原本高度
            :param paste_image_width: 当图片做为背景图时，设置贴图的宽度，用于贴图自动换行
            :param paste_image_height: 当图片做为背景图时，设置贴图的高度，用于贴图自动换行
            :param paste_space: 自动贴图间隔
            :param color: 生成图片的颜色
            :param image_mode: 图片的类型
            :param font_size: 文字大小
            :param background: 打开图片的路径
            :param font: 字体，默认在 resource/ttf/ 路径下
            :param ratio: 倍率压缩
            :param is_alpha: 是否背景透明
            :param plain_text: 纯文字文本
        """
        self.w = int(w)
        self.h = int(h)
        self.paste_image_width = int(paste_image_width)
        self.paste_image_height = int(paste_image_height)
        self.paste_space = int(paste_space)
        self._current_w = 0
        self._current_h = 0
        self.uid = uuid.uuid1()
        self.font_name = font
        self.font_size = font_size
        self.font = ImageFont.truetype(str(FONT_PATH / font), int(font_size))
        if not plain_text and not color:
            color = (255, 255, 255)
        self.background = background
        if not background:
            if plain_text:
                if not color:
                    color = (255, 255, 255, 0)
                ttf_w, ttf_h = self.getsize(str(plain_text))
                self.w = self.w if self.w > ttf_w else ttf_w
                self.h = self.h if self.h > ttf_h else ttf_h
            self.markImg = Image.new(image_mode, (self.w, self.h), color)
            self.markImg.convert(image_mode)
        else:
            if not w and not h:
                self.markImg = Image.open(background)
                w, h = self.markImg.size
                if ratio and ratio > 0 and ratio != 1:
                    self.w = int(ratio * w)
                    self.h = int(ratio * h)
                    self.markImg = self.markImg.resize(
                        (self.w, self.h), Image.ANTIALIAS
                    )
                else:
                    self.w = w
                    self.h = h
            else:
                self.markImg = Image.open(background).resize(
                    (self.w, self.h), Image.ANTIALIAS
                )
        if is_alpha:
            try:
                if array := self.markImg.load():
                    for i in range(w):
                        for j in range(h):
                            pos = array[i, j]
                            is_edit = sum([1 for x in pos[0:3] if x > 240]) == 3
                            if is_edit:
                                array[i, j] = (255, 255, 255, 0)
            except Exception as e:
                print(f"背景透明化发生错误..{type(e)}：{e}")
        self.draw = ImageDraw.Draw(self.markImg)
        self.size = self.w, self.h
        if plain_text:
            fill = font_color if font_color else (0, 0, 0)
            self.text((0, 0), str(plain_text), fill)
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            self.loop = asyncio.get_event_loop()

    @classmethod
    def load_font(cls, font: str, font_size: Optional[int]) -> FreeTypeFont:
        """
        说明:
            加载字体
        参数:
            :param font: 字体名称
            :param font_size: 字体大小
        """
        return ImageFont.truetype(str(FONT_PATH / font), font_size)

    async def apaste(
        self,
        img: "BuildImage" or Image,
        pos: Optional[Tuple[int, int]] = None,
        alpha: bool = False,
        center_type: Optional[Literal["center", "by_height", "by_width"]] = None,
        allow_negative: bool = False,
    ):
        """
        说明:
            异步 贴图
        参数:
            :param img: 已打开的图片文件，可以为 BuildImage 或 Image
            :param pos: 贴图位置（左上角）
            :param alpha: 图片背景是否为透明
            :param center_type: 居中类型，可能的值 center: 完全居中，by_width: 水平居中，by_height: 垂直居中
            :param allow_negative: 允许使用负数作为坐标且不超出图片范围，从右侧开始计算
        """
        await self.loop.run_in_executor(
            None, self.paste, img, pos, alpha, center_type, allow_negative
        )

    def paste(
        self,
        img: "BuildImage",
        pos: Optional[Tuple[int, int]] = None,
        alpha: bool = False,
        center_type: Optional[Literal["center", "by_height", "by_width"]] = None,
        allow_negative: bool = False,
    ):
        """
        说明:
            贴图
        参数:
            :param img: 已打开的图片文件，可以为 BuildImage 或 Image
            :param pos: 贴图位置（左上角）
            :param alpha: 图片背景是否为透明
            :param center_type: 居中类型，可能的值 center: 完全居中，by_width: 水平居中，by_height: 垂直居中
            :param allow_negative: 允许使用负数作为坐标且不超出图片范围，从右侧开始计算
        """
        if center_type:
            if center_type not in ["center", "by_height", "by_width"]:
                raise ValueError(
                    "center_type must be 'center', 'by_width' or 'by_height'"
                )
            width, height = 0, 0
            if not pos:
                pos = (0, 0)
            if center_type == "center":
                width = int((self.w - img.w) / 2)
                height = int((self.h - img.h) / 2)
            elif center_type == "by_width":
                width = int((self.w - img.w) / 2)
                height = pos[1]
            elif center_type == "by_height":
                width = pos[0]
                height = int((self.h - img.h) / 2)
            pos = (width, height)
        if pos and allow_negative:
            if pos[0] < 0:
                pos = (self.w + pos[0], pos[1])
            if pos[1] < 0:
                pos = (pos[0], self.h + pos[1])
        if isinstance(img, BuildImage):
            img = img.markImg
        if self._current_w >= self.w:
            self._current_w = 0
            self._current_h += self.paste_image_height + self.paste_space
        if not pos:
            pos = (self._current_w, self._current_h)
        if alpha:
            try:
                self.markImg.paste(img, pos, img)
            except ValueError:
                img = img.convert("RGBA")
                self.markImg.paste(img, pos, img)
        else:
            self.markImg.paste(img, pos)
        self._current_w += self.paste_image_width + self.paste_space

    @classmethod
    def get_text_size(cls, msg: str, font: str, font_size: int) -> Tuple[int, int]:
        """
        说明:
            获取文字在该图片 font_size 下所需要的空间
        参数:
            :param msg: 文字内容
            :param font: 字体
            :param font_size: 字体大小
        """
        font_ = cls.load_font(font, font_size)
        return font_.getsize(msg)

    def getsize(self, msg: str) -> Tuple[int, int]:
        """
        说明:
            获取文字在该图片 font_size 下所需要的空间
        参数:
            :param msg: 文字内容
        """
        return self.font.getsize(msg)

    async def apoint(
        self, pos: Tuple[int, int], fill: Optional[Tuple[int, int, int]] = None
    ):
        """
        说明:
            异步 绘制多个或单独的像素
        参数:
            :param pos: 坐标
            :param fill: 填错颜色
        """
        await self.loop.run_in_executor(None, self.point, pos, fill)

    def point(self, pos: Tuple[int, int], fill: Optional[Tuple[int, int, int]] = None):
        """
        说明:
            绘制多个或单独的像素
        参数:
            :param pos: 坐标
            :param fill: 填错颜色
        """
        self.draw.point(pos, fill=fill)

    async def aellipse(
        self,
        pos: Tuple[int, int, int, int],
        fill: Optional[Tuple[int, int, int]] = None,
        outline: Optional[Tuple[int, int, int]] = None,
        width: int = 1,
    ):
        """
        说明:
            异步 绘制圆
        参数:
            :param pos: 坐标范围
            :param fill: 填充颜色
            :param outline: 描线颜色
            :param width: 描线宽度
        """
        await self.loop.run_in_executor(None, self.ellipse, pos, fill, outline, width)

    def ellipse(
        self,
        pos: Tuple[int, int, int, int],
        fill: Optional[Tuple[int, int, int]] = None,
        outline: Optional[Tuple[int, int, int]] = None,
        width: int = 1,
    ):
        """
        说明:
            绘制圆
        参数:
            :param pos: 坐标范围
            :param fill: 填充颜色
            :param outline: 描线颜色
            :param width: 描线宽度
        """
        self.draw.ellipse(pos, fill, outline, width)

    async def atext(
        self,
        pos: Union[Tuple[int, int], Tuple[float, float]],
        text: str,
        fill: Union[str, Tuple[int, int, int]] = (0, 0, 0),
        center_type: Optional[Literal["center", "by_height", "by_width"]] = None,
        font: Optional[Union[FreeTypeFont, str]] = None,
        font_size: Optional[int] = None,
        **kwargs,
    ):
        """
        说明:
            异步 在图片上添加文字
        参数:
            :param pos: 文字位置
            :param text: 文字内容
            :param fill: 文字颜色
            :param center_type: 居中类型，可能的值 center: 完全居中，by_width: 水平居中，by_height: 垂直居中
            :param font: 字体
            :param font_size: 字体大小
        """
        await self.loop.run_in_executor(
            None, self.text, pos, text, fill, center_type, font, font_size, **kwargs
        )

    def text(
        self,
        pos: Union[Tuple[int, int], Tuple[float, float]],
        text: str,
        fill: Union[str, Tuple[int, int, int]] = (0, 0, 0),
        center_type: Optional[Literal["center", "by_height", "by_width"]] = None,
        font: Optional[Union[FreeTypeFont, str]] = None,
        font_size: Optional[int] = None,
        **kwargs,
    ):
        """
        说明:
            在图片上添加文字
        参数:
            :param pos: 文字位置(使用center_type中的center后会失效,使用by_width后x失效,使用by_height后y失效)
            :param text: 文字内容
            :param fill: 文字颜色
            :param center_type: 居中类型，可能的值 center: 完全居中，by_width: 水平居中，by_height: 垂直居中
            :param font: 字体
            :param font_size: 字体大小
        """
        if center_type:
            if center_type not in ["center", "by_height", "by_width"]:
                raise ValueError(
                    "center_type must be 'center', 'by_width' or 'by_height'"
                )
            w, h = self.w, self.h
            longgest_text = ""
            sentence = text.split("\n")
            for x in sentence:
                longgest_text = x if len(x) > len(longgest_text) else longgest_text
            ttf_w, ttf_h = self.getsize(longgest_text)
            ttf_h = ttf_h * len(sentence)
            if center_type == "center":
                w = int((w - ttf_w) / 2)
                h = int((h - ttf_h) / 2)
            elif center_type == "by_width":
                w = int((w - ttf_w) / 2)
                h = pos[1]
            elif center_type == "by_height":
                h = int((h - ttf_h) / 2)
                w = pos[0]
            pos = (w, h)
        if font:
            if isinstance(font, str):
                font = self.load_font(font, font_size)
        elif font_size:
            font = self.load_font(self.font_name, font_size)
        self.draw.text(pos, text, fill=fill, font=font or self.font, **kwargs)

    async def asave(self, path: Optional[Union[str, Path]] = None):
        """
        说明:
            异步 保存图片
        参数:
            :param path: 图片路径
        """
        await self.loop.run_in_executor(None, self.save, path)

    def save(self, path: Optional[Union[str, Path]] = None):
        """
        说明:
            保存图片
        参数:
            :param path: 图片路径
        """
        self.markImg.save(path or self.background)  # type: ignore

    def show(self):
        """
        说明:
            显示图片
        """
        self.markImg.show()

    async def aresize(self, ratio: float = 0, w: int = 0, h: int = 0):
        """
        说明:
            异步 压缩图片
        参数:
            :param ratio: 压缩倍率
            :param w: 压缩图片宽度至 w
            :param h: 压缩图片高度至 h
        """
        await self.loop.run_in_executor(None, self.resize, ratio, w, h)

    def resize(self, ratio: float = 0, w: int = 0, h: int = 0):
        """
        说明:
            压缩图片
        参数:
            :param ratio: 压缩倍率
            :param w: 压缩图片宽度至 w
            :param h: 压缩图片高度至 h
        """
        if not w and not h and not ratio:
            raise Exception("缺少参数...")
        if not w and not h and ratio:
            w = int(self.w * ratio)
            h = int(self.h * ratio)
        self.markImg = self.markImg.resize((w, h), Image.ANTIALIAS)
        self.w, self.h = self.markImg.size
        self.size = self.w, self.h
        self.draw = ImageDraw.Draw(self.markImg)

    async def acrop(self, box: Tuple[int, int, int, int]):
        """
        说明:
            异步 裁剪图片
        参数:
            :param box: 左上角坐标，右下角坐标 (left, upper, right, lower)
        """
        await self.loop.run_in_executor(None, self.crop, box)

    def crop(self, box: Tuple[int, int, int, int]):
        """
        说明:
            裁剪图片
        参数:
            :param box: 左上角坐标，右下角坐标 (left, upper, right, lower)
        """
        self.markImg = self.markImg.crop(box)
        self.w, self.h = self.markImg.size
        self.size = self.w, self.h
        self.draw = ImageDraw.Draw(self.markImg)

    def check_font_size(self, word: str) -> bool:
        """
        说明:
            检查文本所需宽度是否大于图片宽度
        参数:
            :param word: 文本内容
        """
        return self.font.getsize(word)[0] > self.w

    async def atransparent(self, alpha_ratio: float = 1, n: int = 0):
        """
        说明:
            异步 图片透明化
        参数:
            :param alpha_ratio: 透明化程度
            :param n: 透明化大小内边距
        """
        await self.loop.run_in_executor(None, self.transparent, alpha_ratio, n)

    def transparent(self, alpha_ratio: float = 1, n: int = 0):
        """
        说明:
            图片透明化
        参数:
            :param alpha_ratio: 透明化程度
            :param n: 透明化大小内边距
        """
        self.markImg = self.markImg.convert("RGBA")
        x, y = self.markImg.size
        for i in range(n, x - n):
            for k in range(n, y - n):
                color = self.markImg.getpixel((i, k))
                color = color[:-1] + (int(100 * alpha_ratio),)
                self.markImg.putpixel((i, k), color)
        self.draw = ImageDraw.Draw(self.markImg)

    def pic2bs4(self) -> str:
        """
        说明:
            BuildImage 转 base64
        """
        buf = BytesIO()
        self.markImg.save(buf, format="PNG")
        base64_str = base64.b64encode(buf.getvalue()).decode()
        return "base64://" + base64_str

    def convert(self, type_: ModeType):
        """
        说明:
            修改图片类型
        参数:
            :param type_: 类型
        """
        self.markImg = self.markImg.convert(type_)

    async def arectangle(
        self,
        xy: Tuple[int, int, int, int],
        fill: Optional[Tuple[int, int, int]] = None,
        outline: Optional[str] = None,
        width: int = 1,
    ):
        """
        说明:
            异步 画框
        参数:
            :param xy: 坐标
            :param fill: 填充颜色
            :param outline: 轮廓颜色
            :param width: 线宽
        """
        await self.loop.run_in_executor(None, self.rectangle, xy, fill, outline, width)

    def rectangle(
        self,
        xy: Tuple[int, int, int, int],
        fill: Optional[Tuple[int, int, int]] = None,
        outline: Optional[str] = None,
        width: int = 1,
    ):
        """
        说明:
            画框
        参数:
            :param xy: 坐标
            :param fill: 填充颜色
            :param outline: 轮廓颜色
            :param width: 线宽
        """
        self.draw.rectangle(xy, fill, outline, width)

    async def apolygon(
        self,
        xy: List[Tuple[int, int]],
        fill: Tuple[int, int, int] = (0, 0, 0),
        outline: int = 1,
    ):
        """
        说明:
            异步 画多边形
        参数:
            :param xy: 坐标
            :param fill: 颜色
            :param outline: 线宽
        """
        await self.loop.run_in_executor(None, self.polygon, xy, fill, outline)

    def polygon(
        self,
        xy: List[Tuple[int, int]],
        fill: Tuple[int, int, int] = (0, 0, 0),
        outline: int = 1,
    ):
        """
        说明:
            画多边形
        参数:
            :param xy: 坐标
            :param fill: 颜色
            :param outline: 线宽
        """
        self.draw.polygon(xy, fill, outline)

    async def aline(
        self,
        xy: Tuple[int, int, int, int],
        fill: Optional[Union[str, Tuple[int, int, int]]] = None,
        width: int = 1,
    ):
        """
        说明:
            异步 画线
        参数:
            :param xy: 坐标
            :param fill: 填充
            :param width: 线宽
        """
        await self.loop.run_in_executor(None, self.line, xy, fill, width)

    def line(
        self,
        xy: Tuple[int, int, int, int],
        fill: Optional[Union[Tuple[int, int, int], str]] = None,
        width: int = 1,
    ):
        """
        说明:
            画线
        参数:
            :param xy: 坐标
            :param fill: 填充
            :param width: 线宽
        """
        self.draw.line(xy, fill, width)

    async def acircle(self):
        """
        说明:
            异步 将 BuildImage 图片变为圆形
        """
        await self.loop.run_in_executor(None, self.circle)

    def circle(self):
        """
        说明:
            使图像变圆
        """
        self.markImg.convert("RGBA")
        size = self.markImg.size
        r2 = min(size[0], size[1])
        if size[0] != size[1]:
            self.markImg = self.markImg.resize((r2, r2), Image.ANTIALIAS)
        width = 1
        antialias = 4
        ellipse_box = [0, 0, r2 - 2, r2 - 2]
        mask = Image.new(
            size=[int(dim * antialias) for dim in self.markImg.size],
            mode="L",
            color="black",
        )
        draw = ImageDraw.Draw(mask)
        for offset, fill in (width / -2.0, "black"), (width / 2.0, "white"):
            left, top = [(value + offset) * antialias for value in ellipse_box[:2]]
            right, bottom = [(value - offset) * antialias for value in ellipse_box[2:]]
            draw.ellipse([left, top, right, bottom], fill=fill)
        mask = mask.resize(self.markImg.size, Image.LANCZOS)
        try:
            self.markImg.putalpha(mask)
        except ValueError:
            pass

    async def acircle_corner(
        self,
        radii: int = 30,
        point_list: List[Literal["lt", "rt", "lb", "rb"]] = ["lt", "rt", "lb", "rb"],
    ):
        """
        说明:
            异步 矩形四角变圆
        参数:
            :param radii: 半径
            :param point_list: 需要变化的角
        """
        await self.loop.run_in_executor(None, self.circle_corner, radii, point_list)

    def circle_corner(
        self,
        radii: int = 30,
        point_list: List[Literal["lt", "rt", "lb", "rb"]] = ["lt", "rt", "lb", "rb"],
    ):
        """
        说明:
            矩形四角变圆
        参数:
            :param radii: 半径
            :param point_list: 需要变化的角
        """
        # 画圆（用于分离4个角）
        img = self.markImg.convert("RGBA")
        alpha = img.split()[-1]
        circle = Image.new("L", (radii * 2, radii * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 黑色方形内切白色圆形
        w, h = img.size
        if "lt" in point_list:
            alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))
        if "rt" in point_list:
            alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))
        if "lb" in point_list:
            alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))
        if "rb" in point_list:
            alpha.paste(
                circle.crop((radii, radii, radii * 2, radii * 2)),
                (w - radii, h - radii),
            )
        img.putalpha(alpha)
        self.markImg = img
        self.draw = ImageDraw.Draw(self.markImg)

    async def arotate(self, angle: int, expand: bool = False):
        """
        说明:
            异步 旋转图片
        参数:
            :param angle: 角度
            :param expand: 放大图片适应角度
        """
        await self.loop.run_in_executor(None, self.rotate, angle, expand)

    def rotate(self, angle: int, expand: bool = False):
        """
        说明:
            旋转图片
        参数:
            :param angle: 角度
            :param expand: 放大图片适应角度
        """
        self.markImg = self.markImg.rotate(angle, expand=expand)

    async def atranspose(self, angle: Literal[0, 1, 2, 3, 4, 5, 6]):
        """
        说明:
            异步 旋转图片(包括边框)
        参数:
            :param angle: 角度
        """
        await self.loop.run_in_executor(None, self.transpose, angle)

    def transpose(self, angle: Literal[0, 1, 2, 3, 4, 5, 6]):
        """
        说明:
            旋转图片(包括边框)
        参数:
            :param angle: 角度
        """
        self.markImg.transpose(angle)

    async def afilter(self, filter_: str, aud: Optional[int] = None):
        """
        说明:
            异步 图片变化
        参数:
            :param filter_: 变化效果
            :param aud: 利率
        """
        await self.loop.run_in_executor(None, self.filter, filter_, aud)

    def filter(self, filter_: str, aud: Optional[int] = None):
        """
        说明:
            图片变化
        参数:
            :param filter_: 变化效果
            :param aud: 利率
        """
        _x = None
        if filter_ == "GaussianBlur":  # 高斯模糊
            _x = ImageFilter.GaussianBlur
        elif filter_ == "EDGE_ENHANCE":  # 锐化效果
            _x = ImageFilter.EDGE_ENHANCE
        elif filter_ == "BLUR":  # 模糊效果
            _x = ImageFilter.BLUR
        elif filter_ == "CONTOUR":  # 铅笔滤镜
            _x = ImageFilter.CONTOUR
        elif filter_ == "FIND_EDGES":  # 边缘检测
            _x = ImageFilter.FIND_EDGES
        if _x:
            if aud:
                self.markImg = self.markImg.filter(_x(aud))
            else:
                self.markImg = self.markImg.filter(_x)
        self.draw = ImageDraw.Draw(self.markImg)

    async def areplace_color_tran(
        self,
        src_color: Union[
            Tuple[int, int, int], Tuple[Tuple[int, int, int], Tuple[int, int, int]]
        ],
        replace_color: Tuple[int, int, int],
    ):
        """
        说明:
            异步 颜色替换
        参数:
            :param src_color: 目标颜色，或者使用列表，设置阈值
            :param replace_color: 替换颜色
        """
        self.loop.run_in_executor(
            None, self.replace_color_tran, src_color, replace_color
        )

    def replace_color_tran(
        self,
        src_color: Union[
            Tuple[int, int, int], Tuple[Tuple[int, int, int], Tuple[int, int, int]]
        ],
        replace_color: Tuple[int, int, int],
    ):
        """
        说明:
            颜色替换
        参数:
            :param src_color: 目标颜色，或者使用元祖，设置阈值
            :param replace_color: 替换颜色
        """
        if isinstance(src_color, tuple):
            start_ = src_color[0]
            end_ = src_color[1]
        else:
            start_ = src_color
            end_ = None
        for i in range(self.w):
            for j in range(self.h):
                r, g, b = self.markImg.getpixel((i, j))
                if not end_:
                    if r == start_[0] and g == start_[1] and b == start_[2]:
                        self.markImg.putpixel((i, j), replace_color)
                else:
                    if (
                        start_[0] <= r <= end_[0]
                        and start_[1] <= g <= end_[1]
                        and start_[2] <= b <= end_[2]
                    ):
                        self.markImg.putpixel((i, j), replace_color)

    #
    def getchannel(self, type_):
        self.markImg = self.markImg.getchannel(type_)
