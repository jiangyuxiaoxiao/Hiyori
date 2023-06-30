"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:38
@Desc: 文件系统功能相关封装
@Ver : 1.0.0
"""
import os


# 判断路径是否存在，不存在则创建
# 对于多级路径，即使多级路径均不存在，也会逐级创建。
def DirExist(Dir: str) -> bool:
    """
    判断路径是否存在，不存在则创建。\n
    对于多级路径，即使多级路径均不存在，也会逐级创建。
    """
    if not os.path.isdir(Dir):
        os.makedirs(Dir)
        return False
    return True



