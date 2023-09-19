"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/30-22:22
@Desc: 时间相关包
@Ver : 1.0.0
"""


def printTimeInfo(nsTime: int, roundNum: int = 3) -> str:
    """根据纳秒时间打印时间信息"""
    if nsTime < 10 ** 3:
        time = f"{nsTime}ns"
    elif nsTime < 10 ** 6:
        time = f"{round(nsTime / (10 ** 3), roundNum)}μs"
    elif nsTime < 10 ** 9:
        time = f"{round(nsTime / (10 ** 6), roundNum)}ms"
    elif nsTime < 60 * (10 ** 9):
        time = f"{round(nsTime / (10 ** 9), roundNum)}s"
    elif nsTime < 3600 * (10 ** 9):
        minute = int(nsTime / (60 * (10 ** 9)))
        second = round((nsTime - minute * 60 * (10 ** 9)) / (10 ** 9), roundNum)
        time = f"{minute}min{second}s"
    else:
        hour = int(nsTime / (3600 * (10 ** 9)))
        minute = int((nsTime - hour * 3600 * (10 ** 9)) / (60 * (10 ** 9)))
        time = f"{hour}h{minute}min"
    return time


