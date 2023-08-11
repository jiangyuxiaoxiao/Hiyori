"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/11-12:21
@Desc: 事件响应器辅助模块
@Ver : 1.0.0
"""
import time
from functools import wraps
from nonebot.log import logger
from nonebot.matcher import Matcher


# 打印插件用时
def logPluginExecuteTime(handleFunc):
    """
    事件响应装饰器，给一个插件的事件响应添加计时功能，日志打印插件执行耗时。\n
    请在@handler.handle()的内侧添加此装饰器。\n
    例如：\n
    @sora.handle() \n
    @logPluginExecuteTime \n
    async def _(matcher:Matcher, ...) \n
    **请注意，当添加此装饰器后，不要使用await handler.send()来发送消息，请改用await matcher.send()**

    """

    @wraps(handleFunc)
    async def wrapper(*args, **kwargs):
        startTimer = time.time_ns()
        result = await handleFunc(*args, **kwargs)
        endTimer = time.time_ns()
        timeResult = endTimer - startTimer
        if timeResult > 10 ** 9:
            timeStr = f"{round(timeResult / (10 ** 9), 3)}s"
        elif timeResult > 10 ** 6:
            timeStr = f"{round(timeResult / (10 ** 6), 3)}ms"
        else:
            timeStr = f"{round(timeResult / (10 ** 3), 3)}us"
        if "matcher" in kwargs:
            matcher: Matcher = kwargs["matcher"]
            name = matcher.plugin_name
            timeStr = f"插件{name}用时" + timeStr
        else:
            timeStr = "用时：" + timeStr
        logger.info(timeStr)
        return result

    return wrapper
