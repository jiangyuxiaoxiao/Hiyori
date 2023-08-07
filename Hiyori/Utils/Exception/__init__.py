"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/2-10:24
@Desc: 自定义异常
@Ver : 1.0.0
"""
from .Market import MarketException


class ConfigException(BaseException):
    """异常，配置文件未正确配置"""

    def __init__(self, path: str = ""):
        self.info = f"路径 {path} 的配置文件不存在或未正确配置"

    def __str__(self):
        return self.info
