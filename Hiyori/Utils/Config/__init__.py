"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/4-15:59
@Desc: 插件配置类 规范
@Ver : 1.0.0
"""
from abc import ABC, abstractmethod


class Config(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def dump(self):
        """导出配置到配置文件中"""
        pass

    @abstractmethod
    def load(self):
        """从配置文件中导入配置"""
        pass
