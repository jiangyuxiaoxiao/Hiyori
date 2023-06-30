"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:49
@Desc: 获取现货价格
@Ver : 1.0.0
"""
import time

from playwright.async_api import async_playwright


async def getGoldInfo() -> dict:
    async with async_playwright() as playwright:
        OK = False
        result = {}
        # 使用Chromium浏览器
        browser = await playwright.chromium.launch()
        context = await browser.new_context()
        # 导航至目标网页
        page = await context.new_page()
        await page.goto("https://m.cngold.org/quote/gjs/gjhj_xhhj.html?key=au")
        # 使用XPath选择器获取元素
        # 金价
        xpath_selector = '//html//body//main//section[1]//div//ul[1]//li[1]'
        elements = page.locator(xpath_selector)
        result["price"] = await elements.text_content()
        if await elements.count() == 1:
            OK = True
        result["OK"] = OK
        # 走势图
        xpath_selector = '//html//body//main//section[3]//div//div[1]//div[2]//div[4]//div[1]//div[2]//div[1]//canvas[3]'
        elements = page.locator(xpath_selector)
        result["image"] = await elements.screenshot()
        # 价图
        selector = "#stock_info_container"
        elements = page.locator(selector)
        result["head_image"] = await elements.screenshot()
        # 关闭浏览器
        await browser.close()
        return result


async def getSilverInfo() -> dict:
    async with async_playwright() as playwright:
        OK = False
        result = {}
        # 使用Chromium浏览器
        browser = await playwright.chromium.launch()
        context = await browser.new_context()
        # 导航至目标网页
        page = await context.new_page()
        await page.goto("https://m.cngold.org/quote/gjs/gjhj_xhby.html?key=ag")
        # 使用XPath选择器获取元素
        # 银价
        xpath_selector = '//html//body//main//section[1]//div//ul[1]//li[1]'
        elements = page.locator(xpath_selector)
        result["price"] = await elements.text_content()
        if await elements.count() == 1:
            OK = True
        result["OK"] = OK
        # 走势图
        xpath_selector = "//html//body//main//section[3]//div//div[1]//div[2]//div[4]//div[1]//div[2]//div[1]//canvas[3]"
        elements = page.locator(xpath_selector)
        result["image"] = await elements.screenshot()
        # 价图
        selector = "#stock_info_container"
        elements = page.locator(selector)
        result["head_image"] = await elements.screenshot()
        # 关闭浏览器
        await browser.close()
        return result


async def getPalladiumInfo() -> dict:
    async with async_playwright() as playwright:
        OK = False
        result = {}
        # 使用Chromium浏览器
        browser = await playwright.chromium.launch()
        context = await browser.new_context()
        # 导航至目标网页
        page = await context.new_page()
        await page.goto("https://m.cngold.org/quote/gjs/gjhj_xhpd.html?key=pd")
        # 使用XPath选择器获取元素
        # 银价
        xpath_selector = '//html//body//main//section[1]//div//ul[1]//li[1]'
        elements = page.locator(xpath_selector)
        result["price"] = await elements.text_content()
        if await elements.count() == 1:
            OK = True
        result["OK"] = OK
        # 走势图
        xpath_selector = "//html//body//main//section[3]//div//div[1]//div[2]//div[4]//div[1]//div[2]//div[1]//canvas[3]"
        elements = page.locator(xpath_selector)
        result["image"] = await elements.screenshot()
        # 价图
        selector = "#stock_info_container"
        elements = page.locator(selector)
        result["head_image"] = await elements.screenshot()
        # 关闭浏览器
        await browser.close()
        return result


async def getPlatinumInfo() -> dict:
    async with async_playwright() as playwright:
        OK = False
        result = {}
        # 使用Chromium浏览器
        browser = await playwright.chromium.launch()
        context = await browser.new_context()
        # 导航至目标网页
        page = await context.new_page()
        await page.goto("https://m.cngold.org/quote/gjs/gjhj_xhpt.html?key=pt")
        # 使用XPath选择器获取元素
        # 银价
        xpath_selector = '//html//body//main//section[1]//div//ul[1]//li[1]'
        elements = page.locator(xpath_selector)
        result["price"] = await elements.text_content()
        if await elements.count() == 1:
            OK = True
        result["OK"] = OK
        # 走势图
        xpath_selector = "//html//body//main//section[3]//div//div[1]//div[2]//div[4]//div[1]//div[2]//div[1]//canvas[3]"
        elements = page.locator(xpath_selector)
        result["image"] = await elements.screenshot()
        # 价图
        selector = "#stock_info_container"
        elements = page.locator(selector)
        result["head_image"] = await elements.screenshot()
        # 关闭浏览器
        await browser.close()
        return result


