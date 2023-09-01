"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/31-15:44
@Desc: QQ群组文件相关封装
@Ver : 1.0.0
"""
import asyncio
import json
import os
import time
from tenacity import retry, stop_after_attempt, wait_fixed
from aiohttp import ClientSession, ClientTimeout, TCPConnector
import aiofiles
import traceback

from nonebot.adapters.onebot.v11 import Bot

from Hiyori.Utils.File import DirExist
from Hiyori.Utils.Time import printTimeInfo


class QQGroupFile:
    """QQ文件类"""

    def __init__(self, group_id: int, file_id: str, file_name: str, busid: int, file_size: int, upload_time: int, dead_time: int,
                 modify_time: int, download_times: int, uploader: int, uploader_name: str, local_path: str = "", local_modify_time: int = 0):
        """
        :param group_id:群号
        :param file_id:文件ID
        :param file_name:文件名
        :param busid:文件类型
        :param file_size:文件大小
        :param upload_time:上传时间
        :param dead_time:过期时间,永久文件恒为0
        :param modify_time:最后修改时间
        :param download_times:下载次数
        :param uploader:上传者ID
        :param uploader_name:上传者名字
        :param local_path:本地保存绝对路径
        :param local_modify_time:本地最后修改时间
        """
        self.group_id: int = group_id
        self.file_id: str = file_id
        self.file_name: str = file_name
        self.busid: int = busid
        self.file_size: int = file_size
        self.upload_time: int = upload_time
        self.dead_time: int = dead_time
        self.modify_time: int = modify_time
        self.download_times: int = download_times
        self.uploader: int = uploader
        self.uploader_name: str = uploader_name
        self.local_path: str = local_path
        self.local_modify_time: int = local_modify_time

    def to_dict(self) -> dict[str, any]:
        """转换为字典格式"""
        return {
            "group_id": self.group_id,
            "file_id": self.file_id,
            "file_name": self.file_name,
            "busid": self.busid,
            "file_size": self.file_size,
            "upload_time": self.upload_time,
            "dead_time": self.dead_time,
            "modify_time": self.modify_time,
            "download_times": self.download_times,
            "uploader": self.uploader,
            "uploader_name": self.uploader_name,
            "local_path": self.local_path,
            "local_modify_time": self.local_modify_time
        }

    @classmethod
    def from_dict(cls, data: dict[str, any]):
        """从字典中构建"""
        thisFile = cls(data["group_id"], data["file_id"], data["file_name"], data["busid"], data["file_size"], data["upload_time"],
                       data["dead_time"], data["modify_time"], data["download_times"], data["uploader"], data["uploader_name"])
        if "local_path" in data.keys():
            thisFile.local_path = data["local_path"]
        if "local_modify_time" in data.keys():
            thisFile.local_modify_time = data["local_modify_time"]
        return thisFile

    def dumps(self) -> str:
        """序列化为json字符串"""
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    @classmethod
    def loads(cls, jsonStr: str):
        """从json字符串中反序列化"""
        data = json.loads(jsonStr)
        return cls.from_dict(data)

    @retry(stop=stop_after_attempt(20), wait=wait_fixed(5))
    async def download(self, path: str, bot: Bot, session: ClientSession = None):
        """
        将群文件下载到本地文件夹，最多尝试二次。
        :param bot: bot
        :param path: 本地路径
        :param session: 若传入session则使用session，否则使用独立session
        """
        url = await bot.get_group_file_url(group_id=self.group_id, file_id=self.file_id, busid=self.busid)
        url = url["url"]
        if session is None:
            async with ClientSession() as s:
                async with s.get(url=url) as response:
                    async with aiofiles.open(file=path, mode="wb") as file:
                        # 默认设置流式传输为 20M，需要更小则自行设置
                        print(f"写入文件{self.file_name}")
                        async for chunk in response.content.iter_chunked(20 * 1024 * 1024):
                            await file.write(chunk)
        else:
            async with session.get(url=url) as response:
                async with aiofiles.open(file=path, mode="wb") as file:
                    # 默认设置流式传输为 20M，需要更小则自行设置
                    print(f"写入文件{self.file_name}")
                    async for chunk in response.content.iter_chunked(20 * 1024 * 1024):
                        await file.write(chunk)


class QQGroupFolder:
    def __init__(self, group_id: int, folder_id: str | None, folder_name: str, create_time: int, creator: int, creator_name: str, total_file_count: int,
                 local_path: str = ""):
        """

        :param group_id: 群号
        :param folder_id: 文件夹id
        :param folder_name: 文件夹名
        :param create_time: 创建时间
        :param creator: 创建者id
        :param creator_name: 创建者名
        :param total_file_count: 总文件个数
        :param local_path: 文件保存本地路径
        """
        self.group_id: int = group_id
        self.folder_id: str = folder_id
        self.folder_name: str = folder_name
        self.create_time: int = create_time
        self.creator: int = creator
        self.creator_name: str = creator_name
        self.total_file_count: int = total_file_count
        self.local_path: str = local_path
        self.files: dict[str, QQGroupFile] = dict()
        self.folders: dict[str, QQGroupFolder] = dict()

    def __add__(self, other):
        """向文件夹中添加子文件或子文件夹"""
        if isinstance(other, QQGroupFile):
            self.files[other.file_id] = other
        elif isinstance(other, QQGroupFolder):
            self.folders[other.folder_id] = other
        else:
            raise TypeError("不能将QQGroupFolder与QQGroupFile或QQGroupFolder以外的类型相加")

    def to_dict(self) -> dict[str, any]:
        """转换为字典格式"""
        return {
            "group_id": self.group_id,
            "folder_id": self.folder_id,
            "folder_name": self.folder_name,
            "create_time": self.create_time,
            "creator": self.creator,
            "creator_name": self.creator_name,
            "total_file_count": self.total_file_count,
            "local_path": self.local_path,
            "files": {fid: f.to_dict() for fid, f in self.files.items()},
            "folders": {fid: f.to_dict() for fid, f in self.folders.items()}
        }

    @classmethod
    def from_dict(cls, data: dict[str, any]):
        thisFolder = cls(data["group_id"], data["folder_id"], data["folder_name"], data["create_time"], data["creator"], data["creator_name"],
                         data["total_file_count"])
        if "local_path" in data.keys():
            thisFolder.local_path = data["local_path"]
        if "files" in data.keys():
            for file in data["files"]:
                thisFolder += QQGroupFile.from_dict(file)
        if "folders" in data.keys():
            for folder in data["folders"]:
                thisFolder += QQGroupFolder.from_dict(folder)
        return thisFolder

    def dumps(self) -> str:
        """序列化为json字符串"""
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    @classmethod
    def loads(cls, jsonStr: str):
        """从json字符串中反序列化"""
        data = json.loads(jsonStr)
        return cls.from_dict(data)

    async def getGroupFolderInfo(self, bot: Bot):
        """通过GoCqhttp初始化文件夹信息"""

        # 为None时，说明是根目录
        if self.folder_id is None:
            info = await bot.get_group_root_files(group_id=self.group_id)
        # 不为None时，说明是子目录
        else:
            info = await bot.get_group_files_by_folder(group_id=self.group_id, folder_id=self.folder_id)
        # 添加子文件信息
        if info["files"] is not None:
            for file in info["files"]:
                file = QQGroupFile.from_dict(file)
                self.files[file.file_id] = file
        # 添加子文件夹信息
        if info["folders"] is not None:
            for folder in info["folders"]:
                folder = QQGroupFolder.from_dict(folder)
                # 递归添加子文件夹信息
                await folder.getGroupFolderInfo(bot)
                self.folders[folder.folder_id] = folder

    async def concurrentDownload(self, dirPath: str, bot: Bot, concurrentNum: int = 5, ignoreTempFile: bool = False) -> str:
        """
        并发下载群文件夹中的所有文件。\n
        对于重名文件的处理：\n
        + 若下载文件夹存在同名文件，直接覆盖
        + 若群聊文件夹存在同盟文件夹，添加后缀
        对于下载失败的处理：\n
        + 若下载失败则对应文件的localPath = ""
        + 若下载成功则写入对应的localPath，为相对路径
        对于临时文件的处理：\n
        当下载临时文件时，速度可能较慢甚至无法正常下载，导致耗时较长。可以传入ignoreTempFile=True来屏蔽临时文件下载。
        对于日志的写入：当下载完成后：\n
        + 将下载文件的树状结构图写入/.config/config.json中
        + 将报错信息栈写入/.error/error.log中
        + 将下载日志写入/.log/log.txt中

        :param dirPath: 指定下载目录，对于本folder来说，文件将会被下载到path/self.folder_name目录下
        :param bot: bot
        :param concurrentNum: 最大并发数
        :param ignoreTempFile: 是否忽略临时文件
        :return: 下载文件总大小，错误信息列表
        """

        class FileDownloadException(Exception):
            """文件下载异常类"""

            def __init__(self, _file: QQGroupFile):
                self.file = _file

        # 1. 遍历，递归统计所有文件对应路径
        start = time.time_ns()
        files: list[QQGroupFile] = []

        def folderWalk(qqFolder: QQGroupFolder, dir_path: str) -> QQGroupFolder:
            """遍历文件夹，计算所有文件夹的本地下载路径"""
            # 修改自身信息
            qqFolder.local_path = os.path.join(dir_path, qqFolder.folder_name).replace("\\", "/")
            DirExist(qqFolder.local_path)
            # 遍历修改所有子文件信息
            fileNames = set()
            for file_id in qqFolder.files.keys():
                file = qqFolder.files[file_id]
                filePath = os.path.join(qqFolder.local_path, file.file_name)
                count = 1
                while filePath in fileNames:
                    # 文件名冲突，尝试重命名
                    filePath = os.path.join(qqFolder.local_path, file.file_name)
                    filePath = os.path.splitext(filePath)[0] + f"({count})" + os.path.splitext(filePath)[1]
                    count += 1
                fileNames.add(filePath)
                file.local_path = filePath.replace("\\", "/")
                qqFolder.files[file_id] = file
                files.append(file)
            # 遍历修改所有子文件夹信息
            for folder_id, folder in qqFolder.folders.items():
                qqFolder.folders[folder_id] = folderWalk(folder, qqFolder.local_path)
            return qqFolder

        async def downloadFileWrapper(qf: QQGroupFile, path: str, b: Bot, s: ClientSession) -> QQGroupFile:
            """
            文件下载封装，记录下载异常信息，将下载异常的文件传入异常进行处理\n
            由于异步并发的原因，因此无法直接try..catch来处理异常。通过将其包裹到一个新异常中，从而传入文件信息以待后续处理。\n
            """

            try:
                await qf.download(path=path, bot=b, session=s)
            except Exception:
                raise FileDownloadException(qf)
            else:
                return qf

        # 更新文件信息
        newInfo = folderWalk(self, dirPath)
        self.local_path = newInfo.local_path.replace("\\", "/")
        self.files = newInfo.files
        self.folders = newInfo.folders

        # 2. 并发下载所有文件，返回结果
        async with asyncio.Semaphore(concurrentNum):
            timeout = ClientTimeout(connect=2, sock_read=5)
            connector = TCPConnector(limit=concurrentNum)
            async with ClientSession(timeout=timeout, connector=connector) as session:
                tasks = []
                failedFilesName = []  # 所有下载错误文件名
                failedFilesPath = set()  # 所有下载错误的路径
                totalDownloadBytes = 0  # 总下载字节数
                for file in files:
                    # 忽略临时文件
                    if ignoreTempFile and file.dead_time != 0:
                        failedFilesPath.add(file.local_path)
                        continue
                    task = asyncio.create_task(downloadFileWrapper(qf=file, path=file.local_path, b=bot, s=session))
                    tasks.append(task)
                # 等待所有下载任务完成
                results = await asyncio.gather(*tasks, return_exceptions=True)
                end = time.time_ns()
                # 记录错误信息
                logDir = os.path.join(self.local_path, ".log")
                DirExist(logDir)
                logPath = os.path.join(logDir, "error.log")
                with open(file=logPath, mode="a", encoding="utf-8") as resultLogFile:
                    for result in results:
                        if isinstance(result, FileDownloadException):
                            failedFilesName.append(result.file.file_name)
                            traceback.print_exception(type(result), result, result.__traceback__, file=resultLogFile)
                            failedFilesPath.add(result.file.local_path)
                        elif isinstance(result, QQGroupFile):
                            totalDownloadBytes += result.file_size
                resultLogPath = os.path.join(logDir, "result.log")
                with open(file=resultLogPath, mode="a", encoding="utf-8") as resultLogFile:
                    failedFilesPath = "\n".join(failedFilesPath) if failedFilesPath else "无下载错误文件"
                    msg = f"群文件下载完成，总下载大小{printSizeInfo(totalDownloadBytes)}，用时{printTimeInfo(end - start, 3)}。\n" \
                          f"下载错误文件列表：\n" \
                          f"{failedFilesPath}"
                    resultLogFile.write(msg)

        # 3. 修正localPath，剔除没有的path
        def folderWalk2(qqFolder: QQGroupFolder) -> QQGroupFolder:
            """遍历文件夹，剔除错误文件路径"""
            # 修改自身信息
            for file_id in qqFolder.files.keys():
                if qqFolder.files[file_id].local_path in failedFilesPath:
                    qqFolder.files[file_id].local_path = ""
            # 遍历修改所有子文件夹信息
            for folder_id, folder in qqFolder.folders.items():
                qqFolder.folders[folder_id] = folderWalk2(folder)
            return qqFolder

        newInfo = folderWalk2(self)
        self.folders = newInfo.folders
        self.files = newInfo.files

        # 打印最终结果
        # 打印文件树
        log_path = os.path.join(self.local_path, ".config")
        DirExist(log_path)
        log_path = os.path.join(log_path, "config.json")
        with open(file=log_path, mode="w", encoding="utf-8") as f:
            f.write(self.dumps())
        # 打印日志信息

        return msg


# 工具函数
def printSizeInfo(size: int) -> str:
    """
    打印文件大小信息，根据具体的值选择合适的单位。

    :param size 文件大小，单位为字节。
    """
    if size < 1024:
        size = str(size) + "B"
    elif size < 1024 ** 2:
        size = str(round(size / 1024, 3)) + "KB"
    elif size < 1024 ** 3:
        size = str(round(size / (1024 ** 2), 3)) + "MB"
    elif size < 1024 ** 4:
        size = str(round(size / (1024 ** 3), 3)) + "GB"
    else:
        size = str(round(size / (1024 ** 4), 3)) + "TB"
    return str(size)
