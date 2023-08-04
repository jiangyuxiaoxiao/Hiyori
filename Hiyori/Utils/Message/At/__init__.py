"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/4-10:11
@Desc: 获取消息中被@的qq号
@Ver : 1.0.0
"""
import re


def GetAtQQ(message: str) -> list[int]:
    """注：不匹配艾特全体成员"""
    result = []
    matchList: list[str] = re.findall(r"\[CQ:at,qq=[0-9]+]", string=message)
    for element in matchList:
        element = element.replace("[CQ:at,qq=", "")
        element = element.replace("]", "")
        if element.isdigit():
            result.append(int(element))
    return result
