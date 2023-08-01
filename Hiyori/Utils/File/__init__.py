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
    对于多级路径，即使多级路径均不存在，也会逐级创建。\n
    此处需填入文件夹路径，对于文件路径，例如 /Dir/to/file.txt，会将file.txt解释为一个文件夹名
    """
    if not os.path.isdir(Dir):
        os.makedirs(Dir)
        return False
    return True


def JsonFileExist(Path: str) -> bool:
    """
    判断json文件是否存在，不存在则初始化创建\n
    需要json文件所在的文件夹存在，否则报错\n

    :param Path: Json文件路径名，例如 /Dir/to/json/path/file.json
    :return: 存在则返回true，实际使用中并不关心返回值
    """
    if os.path.exists(Path):
        return True
    else:
        with open(Path, mode="w", encoding="utf-8") as file:
            file.write("{}")
        return False
