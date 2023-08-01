"""
@Author: Kasugano Sora
@Author2: Zao
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:54
@LastUpdate: 2023/8/1-21:47
@Desc: 将网页转换为二进制截图
@Ver : 1.0.0
"""
from playwright.async_api import async_playwright


async def Web2ImgBytes(url: str, Path: str = "", width: int = 2160) -> bytes:
    """
    将对应网页截屏为图片，当传入了Path参数时，会同时将文件保存到本地

    :param Path: 图片保存路径
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
        if Path != "":
            with open(Path, "wb") as f:
                f.write(screenshot_bytes)
            await browser.close()
    return screenshot_bytes
