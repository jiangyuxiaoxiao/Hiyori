"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:54
@Desc: 将网页转换为二进制截图
@Ver : 1.0.0
"""
from playwright.async_api import async_playwright


async def Web2ImgBytes(url: str, width=2160) -> bytes:
    """
    将对应网页截屏为图片

    :param width: 截取宽度
    :param url: 网址
    :return: 图片bytes
    """
    async with async_playwright() as playwright:
        chromium = playwright.chromium
        browser = await chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": 10}, screen={"width": width, "height": 10})
        await page.goto(url)
        screenshot_bytes = await page.screenshot(full_page=True)
        await browser.close()
    return screenshot_bytes