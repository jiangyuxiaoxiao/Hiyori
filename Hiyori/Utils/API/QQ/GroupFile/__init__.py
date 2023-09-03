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
import re
import time
import datetime
import shutil
from tenacity import retry, stop_after_attempt, wait_fixed
from aiohttp import ClientSession, ClientTimeout, TCPConnector
import aiofiles
import traceback

from nonebot.adapters.onebot.v11 import Bot
from nonebot.log import logger

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
        :param upload_time:上传时间，10位时间戳
        :param dead_time:过期时间,永久文件恒为0
        :param modify_time:最后修改时间，10位时间戳
        :param download_times:下载次数
        :param uploader:上传者ID
        :param uploader_name:上传者名字
        :param local_path:本地保存绝对路径
        :param local_modify_time:本地最后修改时间，13位时间戳
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

    async def download(self, path: str, bot: Bot, attemptCount: int | None = 20, waitAfterFail: int | float | None = 5, session: ClientSession = None):
        """
        将群文件下载到本地文件夹，最多尝试二次。
        :param bot: bot
        :param path: 本地路径
        :param attemptCount: 下载失败尝试次数
        :param waitAfterFail: 下载失败后重试等待时间，单位秒
        :param session: 若传入session则使用session，否则使用独立session
        """
        if attemptCount is None:
            attemptCount = 20
        if waitAfterFail is None:
            waitAfterFail = 5

        @retry(stop=stop_after_attempt(attemptCount), wait=wait_fixed(waitAfterFail))
        async def _download(self: QQGroupFile, path: str, bot: Bot, session: ClientSession = None):
            url = await bot.get_group_file_url(group_id=self.group_id, file_id=self.file_id, busid=self.busid)
            url = url["url"]
            logger.opt(colors=True).debug(f"<yellow>开始请求文件{self.file_name}</yellow>")
            if session is None:
                async with ClientSession() as s:
                    async with s.get(url=url) as response:
                        async with aiofiles.open(file=path, mode="wb") as file:
                            # 默认设置流式传输为 20M，需要更小则自行设置
                            logger.opt(colors=True).debug(f"<blue>开始写入文件{self.file_name}</blue>")
                            async for chunk in response.content.iter_chunked(20 * 1024 * 1024):
                                await file.write(chunk)
            else:
                async with session.get(url=url) as response:
                    async with aiofiles.open(file=path, mode="wb") as file:
                        # 默认设置流式传输为 20M，需要更小则自行设置
                        logger.opt(colors=True).debug(f"<blue>开始写入文件{self.file_name}</blue>")
                        async for chunk in response.content.iter_chunked(20 * 1024 * 1024):
                            await file.write(chunk)

        await _download(self, path, bot, session)


class FileDownloadException(Exception):
    """文件下载异常类"""

    def __init__(self, _file: QQGroupFile):
        self.file = _file


async def downloadFile(file: QQGroupFile, path: str, bot: Bot, session: ClientSession = None, attemptCount: int | None = None,
                       waitAfterFail: int | float | None = None) -> QQGroupFile:
    """
    文件下载封装，记录下载异常信息，将下载异常的文件传入异常进行处理\n
    由于异步并发的原因，因此无法直接try..catch来处理异常。通过将其包裹到一个新异常中，从而传入文件信息以待后续处理。\n
    """
    try:
        await file.download(path=path, bot=bot, session=session, waitAfterFail=waitAfterFail, attemptCount=attemptCount)
    except Exception:
        logger.opt(colors=True).error(f"<red>文件{file.file_name}下载失败</red>")
        raise FileDownloadException(file)
    else:
        logger.opt(colors=True).success(f"<green>成功下载文件{file.file_name}</green>")
        return file


class QQGroupFolder:
    """QQ文件夹类"""

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
        return self

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
            for file in data["files"].values():
                newFile = QQGroupFile.from_dict(file)
                thisFolder = thisFolder + newFile
        if "folders" in data.keys():
            for folder in data["folders"].values():
                thisFolder = thisFolder + QQGroupFolder.from_dict(folder)
        return thisFolder

    def dumps(self) -> str:
        """序列化为json字符串"""
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    @classmethod
    def loads(cls, jsonStr: str):
        """从json字符串中反序列化"""
        data = json.loads(jsonStr)
        return cls.from_dict(data)

    # 通过GoCqhttp初始化文件夹信息
    async def updateInfoFromQQ(self, bot: Bot):
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
                await folder.updateInfoFromQQ(bot)
                self.folders[folder.folder_id] = folder

    # 递归获取文件夹中所有文件
    def getAllFiles(self) -> list[QQGroupFile]:
        """递归获取文件夹中所有文件"""
        files: list[QQGroupFile] = []
        files += [f for f in self.files.values()]
        for folder in self.folders.values():
            files += folder.getAllFiles()
        return files

    # 递归获取文件夹中所有文件夹，包括自身
    def getAllFolders(self) -> list:
        """递归获取文件夹中所有文件夹，包括自身"""
        folders: list = [self]
        folders += [folder.getAllFolders() for folder in self.folders.values()]
        return folders

    # 根据本地路径获取对应文件夹，不区分用户名模式
    def getFolderByLocalPath(self, localPath: str):
        """
        根据本地路径获取对应文件夹
        :param localPath: 待搜索本地路径

        :return: 找到对应文件夹则返回文件夹对象，不存在则返回None
        """
        if self.local_path == localPath:
            return self
        for folder in self.folders.values():
            result = folder.getFolderByLocalPath(localPath)
            if result is not None:
                return result
        return None

    # 根据本地路径的实际情况，删除路径不存在的节点
    def checkLocalPath(self):
        deleteID = []
        for file_id, file in self.files.items():
            if not os.path.isfile(file.local_path):
                deleteID.append(file_id)
        for file_id in deleteID:
            self.files.pop(file_id)
        for folder_id, folder in self.folders.items():
            folder.checkLocalPath()

    # 根据本地路径创建新文件夹，不区分用户名模式
    # TODO
    def createFolderByLocalPath(self, localPath: str, bot: Bot) -> int:
        """
        根据本地路径创建新文件夹

        :param bot: cqbot
        :param localPath: 待搜索本地路径
        :return: 创建成功返回1，文件夹已存在返回0，未创建成功返回-1
        """
        # 由于文件夹路径格式统一，因此若不满足包含关系则localPath对应的路径肯定不在对应文件夹里
        if not localPath.startswith(self.local_path):
            return -1
        else:
            if localPath == self.local_path:
                return 0  # 文件夹已存在
            relPath = os.path.relpath(localPath, self.local_path).replace("\\", "/")
            if "/" not in relPath:
                # 说明localPath是self的子节点
                for folder in self.folders.values():
                    if folder.local_path == localPath:
                        return 0
                # 说明文件夹节点不存在，准备创建
                # TODO 创建
                # newFolder = QQGroupFolder(group_id=self.group_id, folder_id="", folder_name=relPath, create_time=-1, creator=)
            else:
                for folder in self.folders.values():
                    result = folder.createFolderByLocalPath(localPath, bot)
                    if result == 0 or result == 1:
                        return result
                return -1

    # 遍历文件夹，计算所有文件夹的本地下载路径，返回收集到的所有文件列表
    def calculateLocalPaths(self, dir_path: str) -> list[QQGroupFile]:
        """遍历文件夹，计算所有文件夹的本地下载路径，返回收集到的所有文件列表"""
        files: list[QQGroupFile] = []
        # 修改自身信息
        self.local_path = os.path.join(dir_path, self.folder_name).replace("\\", "/")
        DirExist(self.local_path)
        # 遍历修改所有子文件信息
        fileNames = set()
        for file_id in self.files.keys():
            filePath = os.path.join(self.local_path, self.files[file_id].file_name)
            count = 1
            while filePath in fileNames:
                # 文件名冲突，尝试重命名
                filePath = os.path.join(self.local_path, self.files[file_id].file_name)
                filePath = os.path.splitext(filePath)[0] + f"({count})" + os.path.splitext(filePath)[1]
                count += 1
            fileNames.add(filePath)
            self.files[file_id].local_path = filePath.replace("\\", "/")
            files.append(self.files[file_id])

        # 遍历修改所有子文件夹信息
        for folder_id, folder in self.folders.items():
            files += folder.calculateLocalPaths(self.local_path)

        return files

    # 遍历文件夹，计算所有文件夹的本地下载路径，文件路径结构为群名/人名/群文件，返回收集到的所有文件列表
    def calculateLocalPathsByName(self, dir_path: str) -> list[QQGroupFile]:
        """
        遍历文件夹，计算所有文件夹的本地下载路径，文件路径结构为群名/人名/群文件，返回收集到的所有文件列表

        :param dir_path: 文件夹路径
        """
        fileNames: dict[str, set[str]] = dict()  # 用于统计重复的文件名
        fileDirs = set()  # 用于统计相同的文件夹

        # self.local_path = os.path.join(dir_path, self.folder_name).replace("\\", "/")

        def _updateLocalPathsByName(folder: QQGroupFolder, dir_path: str, basePath: str) -> list[QQGroupFile]:
            """遍历闭包函数"""
            # 修改自身信息
            # 对于文件夹而言，其记录的localPath并非实际的Path，而与updateLocalPaths的路径保持一致
            files: list[QQGroupFile] = []
            folder.local_path = os.path.join(dir_path, folder.folder_name).replace("\\", "/")
            for file_id in folder.files.keys():
                # 修正用户名，避免出现非法字符
                if os.name == "nt":
                    folder.files[file_id].uploader_name = re.sub(pattern=r'[\/:*?"<>|]', string=folder.files[file_id].uploader_name, repl="")
                    if folder.files[file_id].uploader_name == "":
                        folder.files[file_id].uploader_name = "default"
                else:
                    folder.files[file_id].uploader_name = folder.files[file_id].uploader_name.replace("/", "")
                    if folder.files[file_id].uploader_name == "":
                        folder.files[file_id].uploader_name = "default"
                # 计算文件实际路径目录
                relPath = os.path.relpath(folder.local_path, basePath)
                fileDir = os.path.join(basePath, folder.files[file_id].uploader_name, relPath)
                if fileDir not in fileDirs:
                    DirExist(fileDir)
                    fileDirs.add(fileDir)
                    fileNames[fileDir] = set()
                filePath = os.path.normpath(os.path.join(fileDir, folder.files[file_id].file_name))
                # 检查文件名是否重复
                count = 1
                while filePath in fileNames[fileDir]:
                    # 文件名冲突，尝试重命名
                    filePath = os.path.normpath(os.path.join(fileDir, folder.files[file_id].file_name))
                    filePath = os.path.splitext(filePath)[0] + f"({count})" + os.path.splitext(filePath)[1]
                    count += 1
                fileNames[fileDir].add(filePath)
                folder.files[file_id].local_path = filePath.replace("\\", "/")
                files.append(folder.files[file_id])

            # 遍历修改所有子文件夹信息
            for folder_id, _folder in folder.folders.items():
                files += _updateLocalPathsByName(_folder, folder.local_path, basePath)

            return files

        # 遍历修改所有子文件信息
        return _updateLocalPathsByName(self, dir_path=dir_path, basePath=os.path.join(dir_path, self.folder_name).replace("\\", "/"))

    # 并发下载群文件夹中的所有文件。
    async def download(self, dirPath: str, bot: Bot, concurrentNum: int = 20, ignoreTempFile: bool = False, attemptCount: int | None = None,
                       waitAfterFail: int | float | None = None, connectTimeout: float | None = 2, downloadTimeout: float | None = 5,
                       mode: str = "ByName") -> str:
        """
        并发下载群文件夹中的所有文件。\n
        concurrentNum = 1等效于阻塞下载，因此不再实现\n
        对于重名文件的处理：\n
        + 若下载文件夹存在同名文件，直接覆盖
        + 若群聊文件夹存在同盟文件夹，添加后缀
        对于已有config.json的处理:\n
        + 本函数实现的是 **覆盖** 下载，因此原config.json也会被覆盖。
        对于下载失败的处理：\n
        + 若下载失败则对应文件的local_path = ""
        + 若下载成功则写入对应的local_path，为相对路径。写入对应文件的本地最后修改时间local_modify_time。
        对于临时文件的处理：\n
        当下载临时文件时，速度可能较慢甚至无法正常下载，导致耗时较长。可以传入ignoreTempFile=True来屏蔽临时文件下载。
        对于日志的写入：当下载完成后：\n
        + 将下载文件的树状结构图写入/.config/config.json中
        + 将报错信息栈写入/.log/error.log中
        + 将下载日志写入/.log/result.log中

        :param dirPath: 指定下载目录，对于本folder来说，文件将会被下载到path/self.folder_name目录下
        :param bot: bot
        :param concurrentNum: 下载并发数
        :param ignoreTempFile: 是否忽略临时文件
        :param attemptCount: 下载重试次数
        :param waitAfterFail: 下载失败后等待时间
        :param connectTimeout: 单位秒，从发出请求到建立连接的等待最长时间，当超过这个时间会中断请求
        :param downloadTimeout: 单位秒，读取最长等待时间，当超过readTimeout的间隔时间没有从服务器接收到数据包会中断请求。注意：是间隔时间，当一个文件较大时可能需要花费较长时间，但是只要
        一直从服务器下载并不会中断对应的下载。只有当超过downloadTimeout时长没有接收到数据包才会中断请求
        :param mode: 下载模式 ByName：根据上传用户名构建文件结构(区分用户名/群号/用户名/群文件)； Origin：根据群文件原始目录结构构建文件结构(不区分用户名/群号/群文件)
        :return: 下载文件总大小，错误信息列表
        """

        # 0. 参数预处理
        if connectTimeout is None:
            connectTimeout = 2
        if downloadTimeout is None:
            downloadTimeout = 5
        # 1. 遍历，递归统计所有文件对应路径
        start = time.time_ns()
        date = datetime.datetime.now().strftime("%Y年%m月%d日 %H时%M分%S秒")

        # 更新文件信息，收集所有需要下载的文件
        if mode == "Origin":
            dirPath = os.path.join(dirPath, "不区分用户名").replace("\\", "/")
            files = self.calculateLocalPaths(dirPath)
        else:
            dirPath = os.path.join(dirPath, "区分用户名").replace("\\", "/")
            files = self.calculateLocalPathsByName(dirPath)

        # 2. 并发下载所有文件，返回结果
        async with asyncio.Semaphore(concurrentNum):
            timeout = ClientTimeout(connect=connectTimeout, sock_read=downloadTimeout)
            connector = TCPConnector(limit=concurrentNum)
            async with ClientSession(timeout=timeout, connector=connector) as session:
                tasks = []
                failedFilesPath = set()  # 所有下载错误的路径
                tempFilesPath = set()
                totalDownloadBytes = 0  # 总下载字节数
                for file in files:
                    # 忽略临时文件
                    if ignoreTempFile and file.dead_time != 0:
                        tempFilesPath.add(file.local_path)
                        continue
                    task = asyncio.create_task(
                        downloadFile(file=file, path=file.local_path, bot=bot, session=session, waitAfterFail=waitAfterFail, attemptCount=attemptCount))
                    tasks.append(task)
                # 等待所有下载任务完成
                results = await asyncio.gather(*tasks, return_exceptions=True)
                end = time.time_ns()
                # 记录错误信息
                logDir = os.path.join(self.local_path, ".log", date)
                DirExist(logDir)
                errorLogPath = os.path.join(logDir, f"error.log")
                with open(file=errorLogPath, mode="a", encoding="utf-8") as errorLogFile:
                    for result in results:
                        if isinstance(result, FileDownloadException):
                            # 对于错误文件，将报错信息写入log
                            traceback.print_exception(type(result), result, result.__traceback__, file=errorLogFile)
                            failedFilesPath.add(result.file.local_path)
                        elif isinstance(result, QQGroupFile):
                            # 对于成功下载文件，计算总下载大小
                            totalDownloadBytes += result.file_size
                resultLogPath = os.path.join(logDir, f"result.log")
                with open(file=resultLogPath, mode="a", encoding="utf-8") as resultLogFile:
                    failedFilesPathStr = "\n".join(
                        [os.path.relpath(path, dirPath).replace("\\", "/") for path in failedFilesPath]
                    ) if failedFilesPath else "无下载错误文件"
                    msg = f"群文件下载完成，总文件数{len(files)}，总下载文件数{len(files) - len(failedFilesPath) - len(tempFilesPath)}，" \
                          f"下载错误数{len(failedFilesPath)}，跳过临时文件数{len(tempFilesPath)}。" \
                          f"总下载大小{printSizeInfo(totalDownloadBytes)}，用时{printTimeInfo(end - start, 3)}。\n" \
                          f"下载错误文件列表：\n" \
                          f"{failedFilesPathStr}"
                    resultLogFile.write(msg)

        # 3. 修正localPath，剔除没有的path
        def folderWalk(qqFolder: QQGroupFolder) -> QQGroupFolder:
            """遍历文件夹，剔除错误文件路径"""
            # 修改自身信息
            for file_id in qqFolder.files.keys():
                # 删除错误文件和临时文件的本地路径信息，没有本地路径信息的文件被视为没有下载
                if qqFolder.files[file_id].local_path in failedFilesPath or qqFolder.files[file_id].local_path in tempFilesPath:
                    qqFolder.files[file_id].local_path = ""
                # 对于正确下载的文件，记录本地最后修改日期
                else:
                    qqFolder.files[file_id].local_modify_time = int(os.path.getmtime(qqFolder.files[file_id].local_path) * 1000)
            # 遍历修改所有子文件夹信息
            for folder_id, folder in qqFolder.folders.items():
                folderWalk(qqFolder.folders[folder_id])
            return qqFolder

        folderWalk(self)

        # 打印最终结果
        # 打印文件树
        log_path = os.path.join(self.local_path, ".config")
        DirExist(log_path)
        log_path = os.path.join(log_path, "config.json")
        with open(file=log_path, mode="w", encoding="utf-8") as f:
            f.write(self.dumps())
        # 打印日志信息

        return msg

    async def SyncFromGroup(self, dirPath: str, bot: Bot, concurrentNum: int = 20, ignoreTempFile: bool = False, attemptCount: int | None = None,
                            waitAfterFail: int | float | None = None, connectTimeout: float | None = 2, downloadTimeout: float | None = 5,
                            mode: str = "ByName") -> str:
        """
        从群文件夹将文件同步到本地。\n
        此为单向同步功能，方向为将群文件同步到本地。\n
        concurrentNum = 1等效于阻塞下载，因此不再实现\n
        对于重名文件的处理：\n
        + 若文件ID不同：下载并覆盖
        + 若文件ID相同，服务器最后修改时间不同：下载并覆盖
        + 若文件ID相同，服务器最后修改时间相同：跳过
        对于已有config.json的处理:\n
        + 下载完成后进行覆盖
        对于下载失败文件的处理：\n
        + 若下载失败则不修改对应文件的config
        对于临时文件的处理：\n
        当下载临时文件时，速度可能较慢甚至无法正常下载，导致耗时较长。可以传入ignoreTempFile=True来屏蔽临时文件下载。
        对于日志的写入：当下载完成后：\n
        + 将下载文件的树状结构图写入/.config/config.json中
        + 将报错信息栈写入/.log/error.log中
        + 将下载日志写入/.log/result.log中

        :param dirPath: 指定下载目录，对于本folder来说，文件将会被下载到path/self.folder_name目录下
        :param bot: bot
        :param concurrentNum: 下载并发数
        :param ignoreTempFile: 是否忽略临时文件
        :param attemptCount: 下载重试次数
        :param waitAfterFail: 下载失败后等待时间
        :param connectTimeout: 单位秒，从发出请求到建立连接的等待最长时间，当超过这个时间会中断请求
        :param downloadTimeout: 单位秒，读取最长等待时间，当超过readTimeout的间隔时间没有从服务器接收到数据包会中断请求。注意：是间隔时间，当一个文件较大时可能需要花费较长时间，但是只要
        一直从服务器下载并不会中断对应的下载。只有当超过downloadTimeout时长没有接收到数据包才会中断请求
        :param mode: 下载模式 ByName：根据上传用户名构建文件结构(区分用户名/群号/用户名/群文件)； Origin：根据群文件原始目录结构构建文件结构(不区分用户名/群号/群文件)
        :return: 下载文件总大小，错误信息列表
        """
        start = time.time_ns()
        date = datetime.datetime.now().strftime("%Y年%m月%d日 %H时%M分%S秒")
        # 1. 判断config.json是否存在，不存在则直接调用download进行下载。
        if mode == "Origin":
            configPath = os.path.join(dirPath, "不区分用户名", str(self.group_id), ".config", "config.json")

        else:
            configPath = os.path.join(dirPath, "区分用户名", str(self.group_id), ".config", "config.json")
        if not os.path.isfile(configPath):
            result = await self.download(dirPath=dirPath, bot=bot, concurrentNum=concurrentNum, ignoreTempFile=ignoreTempFile, attemptCount=attemptCount,
                                         waitAfterFail=waitAfterFail, connectTimeout=connectTimeout, downloadTimeout=downloadTimeout)
            return result

        # 2. 尝试读取本地config.json进行同步，若失败则调用download覆盖下载
        try:
            with open(configPath, mode="r", encoding="utf-8") as f:
                data = f.read()
            data = json.loads(data)
            localGroupFile = QQGroupFolder.from_dict(data)
        except Exception:
            result = await self.download(dirPath=dirPath, bot=bot, concurrentNum=concurrentNum, ignoreTempFile=ignoreTempFile, attemptCount=attemptCount,
                                         waitAfterFail=waitAfterFail, connectTimeout=connectTimeout, downloadTimeout=downloadTimeout)
            return result
        # 3. 将本地文件树与当前群聊文件树进行比对
        # 3.1 根据mode生成当前群聊文件树的本地路径
        if mode == "Origin":
            dirPath = os.path.join(dirPath, "不区分用户名").replace("\\", "/")
            files = self.calculateLocalPaths(dirPath)
        else:
            dirPath = os.path.join(dirPath, "区分用户名").replace("\\", "/")
            files = self.calculateLocalPathsByName(dirPath)
        # 3.2 遍历本地文件树，删除已变动节点
        localGroupFile.checkLocalPath()
        # 3.3 遍历群聊文件树，与本地文件节点进行对比。不存在的节点：下载，位置变动的节点：移动本地位置
        localFiles = localGroupFile.getAllFiles()
        localFilesDict: dict[str, QQGroupFile] = {file.file_id: file for file in localFiles}
        tasks = []
        failedFilesPath = set()  # 所有下载错误的路径
        tempFilesPath = set()
        totalDownloadBytes = 0  # 总下载字节数
        skipFiles = []
        async with asyncio.Semaphore(concurrentNum):
            timeout = ClientTimeout(connect=connectTimeout, sock_read=downloadTimeout)
            connector = TCPConnector(limit=concurrentNum)
            async with ClientSession(timeout=timeout, connector=connector) as session:
                for file in files:
                    # 文件不存在
                    if file.file_id not in localFilesDict.keys():
                        # 且满足临时文件逻辑
                        if (file.dead_time != 0 and not ignoreTempFile) or file.dead_time == 0:
                            task = asyncio.create_task(
                                downloadFile(file=file, path=file.local_path, bot=bot, session=session, waitAfterFail=waitAfterFail, attemptCount=attemptCount))
                            tasks.append(task)
                        else:
                            tempFilesPath.add(file.local_path)
                    else:
                        localFile = localFilesDict[file.file_id]
                        # 文件在本地文件树上存在，在群聊树上也存在，在实际地址上也存在
                        if os.path.isfile(localFile.local_path):
                            # 文件的服务器最后修改时间发生变动 或 文件与服务器文件不一致：删除本地文件，下载群聊文件
                            if localFile.modify_time != file.modify_time \
                                    or os.path.getsize(localFile.local_path) != file.file_size:
                                # 且满足临时文件逻辑
                                if (file.dead_time != 0 and not ignoreTempFile) or file.dead_time == 0:
                                    os.remove(path=localFile.local_path)
                                    task = asyncio.create_task(
                                        downloadFile(file=file, path=file.local_path, bot=bot, session=session, waitAfterFail=waitAfterFail,
                                                     attemptCount=attemptCount))
                                    tasks.append(task)
                                # 不满足临时文件处理逻辑，进行挂树
                                else:
                                    # TODO
                                    pass
                            # 文件与服务器文件不一致 最后修改日期也未变，但是地址变动：移动本地文件
                            elif localFile.local_path != file.local_path:
                                shutil.move(src=localFile.local_path, dst=file.local_path)
                            # 文件未发生变动：不进行操作
                            else:
                                skipFiles.append(file)
                        # 文件在本地文件树上存在，在群聊树上也存在，在实际地址上不存在，下载文件
                        else:
                            task = asyncio.create_task(
                                downloadFile(file=file, path=file.local_path, bot=bot, session=session, waitAfterFail=waitAfterFail, attemptCount=attemptCount))
                            tasks.append(task)
                # 等待所有下载任务完成
                results = await asyncio.gather(*tasks, return_exceptions=True)

        # 3.4 遍历本地文件树，与群聊文件节点进行对比。不存在的节点：挂在群聊文件树上。
        end = time.time_ns()
        # 4 记录log，保存结果
        logDir = os.path.join(self.local_path, ".log", date)
        DirExist(logDir)
        errorLogPath = os.path.join(logDir, f"error.log")
        with open(file=errorLogPath, mode="a", encoding="utf-8") as errorLogFile:
            for result in results:
                if isinstance(result, FileDownloadException):
                    # 对于错误文件，将报错信息写入log
                    traceback.print_exception(type(result), result, result.__traceback__, file=errorLogFile)
                    failedFilesPath.add(result.file.local_path)
                elif isinstance(result, QQGroupFile):
                    # 对于成功下载文件，计算总下载大小
                    totalDownloadBytes += result.file_size
        resultLogPath = os.path.join(logDir, f"result.log")
        with open(file=resultLogPath, mode="a", encoding="utf-8") as resultLogFile:
            failedFilesPathStr = "\n".join(
                [os.path.relpath(path, dirPath).replace("\\", "/") for path in failedFilesPath]
            ) if failedFilesPath else "无下载错误文件"
            msg = f"群文件下载完成，总文件数{len(files)}，总下载文件数{len(files) - len(failedFilesPath) - len(tempFilesPath) - len(skipFiles)}，" \
                  f"下载错误数{len(failedFilesPath)}，跳过临时文件数{len(tempFilesPath)}，跳过已下载文件数{len(skipFiles)}。" \
                  f"总下载大小{printSizeInfo(totalDownloadBytes)}，用时{printTimeInfo(end - start, 3)}。\n" \
                  f"下载错误文件列表：\n" \
                  f"{failedFilesPathStr}"
            resultLogFile.write(msg)
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
