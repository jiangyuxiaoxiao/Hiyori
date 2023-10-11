"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/6/30-22:38
@Desc: 文件系统功能相关封装
@Ver : 1.0.0
"""
import os
import json
from nonebot.log import logger


# 判断路径是否存在，不存在则创建
# 对于多级路径，即使多级路径均不存在，也会逐级创建。
def DirExist(Dir: str, logEnable: bool = False, logInfo: str = "") -> bool:
    """
    判断路径是否存在，不存在则创建。\n
    对于多级路径，即使多级路径均不存在，也会逐级创建。\n
    此处需填入文件夹路径，对于文件路径，例如 /Dir/to/file.txt，会将file.txt解释为一个文件夹名

    :param logInfo: 日志内容，若为空则输出默认内容
    :param Dir: 路径名
    :param logEnable: 创建文件夹是否输出日志，默认不输出
    :return:存在则返回true，实际使用中并不关心返回值
    """
    if not os.path.isdir(Dir):
        os.makedirs(Dir)
        # 输出日志
        if logEnable:
            if logInfo == "":
                logInfo = f"路径 {Dir} 不存在，已创建"
            logger.info(logInfo)
        return False
    return True


def JsonFileExist(Path: str, initContent: dict | str | list = None, indent: int = 2,
                  logEnable: bool = False, logInfo: str = "") -> bool:
    """
    判断json文件是否存在，不存在则初始化创建，若提供了initContent模板，则按模板进行创建，\n
    否则创建空对象。若模板为字符串则按给定字符串初始化，否则以字典作为模板进行初始化\n
    需要json文件所在的文件夹存在，否则报错\n

    :param indent: json缩进空格数
    :param initContent: 将对象作为Json初始化模板
    :param Path: Json文件路径名，例如 /Dir/to/json/path/file.json
    :param logInfo: 日志内容，若为空则输出默认内容
    :param logEnable: 创建文件是否输出日志，默认不输出
    :return: 存在则返回true，实际使用中并不关心返回值
    """
    if os.path.exists(Path):
        return True
    else:
        if initContent is not None:
            if isinstance(initContent, str):
                outJson = initContent
            else:
                outJson = json.dumps(obj=initContent, indent=indent, ensure_ascii=False)
        else:
            outJson = "{}"
        with open(Path, mode="w", encoding="utf-8") as file:
            file.write(outJson)
        # 输出日志
        if logEnable:
            if logInfo == "":
                logInfo = f"文件 {Path} 不存在，已创建"
            logger.info(logInfo)
        return False


def getFileInfo(path: str):
    """获取文件全部信息"""

    if not os.path.exists(path):
        raise FileNotFoundError()
    else:
        return os.stat(path)


if __name__ == '__main__':
    # id = getFileID("Data/Utils/File/File2")
    print(id)
