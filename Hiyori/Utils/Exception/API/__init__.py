"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/28-15:10
@Desc: API异常
@Ver : 1.0.0
"""


class APIException(Exception):
    def __str__(self):
        return "APIException"

