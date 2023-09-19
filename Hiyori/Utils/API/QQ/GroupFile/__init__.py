"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/31-15:44
@Desc: QQ群组文件相关封装
@Ver : 1.0.0
"""
from __future__ import annotations
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
                 modify_time: int, download_times: int, uploader: int, uploader_name: str, local_path: str = "", local_modify_time: int = 0,
                 local_file_id: int = 0):
        """
        :param group_id:群号
        :param file_id:文件ID 传入""时视为本地文件
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
        :param local_file_id:本地文件ID
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
        self.local_file_id: int = local_file_id
        # 不存储数据
        self.parentFolder: QQGroupFolder | None = None  # 用于指向父节点

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
            "local_modify_time": self.local_modify_time,
            "local_file_id": self.local_file_id
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
        if "local_file_id" in data.keys():
            thisFile.local_file_id = data["local_file_id"]
        return thisFile

    @classmethod
    def createFromLocalFile(cls, group_id: int, path: str) -> QQGroupFile:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"路径{path}没有找到本地文件或该路径为目录")
        file_name = os.path.basename(path)
        file_size = os.stat(path).st_size
        local_modify_time = os.stat(path).st_mtime_ns
        local_file_id = os.stat(path).st_ino
        local_path = os.path.normpath(path).replace("\\", "/").strip("/")
        file = cls(group_id=group_id, file_id="", file_name=file_name, busid=0, file_size=file_size, upload_time=0, dead_time=0, modify_time=0,
                   download_times=0, uploader=0, uploader_name="", local_path=local_path, local_modify_time=local_modify_time, local_file_id=local_file_id)
        return file

    def dumps(self) -> str:
        """序列化为json字符串"""
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    @classmethod
    def loads(cls, jsonStr: str):
        """从json字符串中反序列化"""
        data = json.loads(jsonStr)
        return cls.from_dict(data)

    async def _download(self, path: str, bot: Bot, attemptCount: int | None = 20, waitAfterFail: int | float | None = 5, session: ClientSession = None):
        """
        将群文件下载到本地文件夹，内部封装
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
        async def innerDownload(self: QQGroupFile, path: str, bot: Bot, session: ClientSession = None):
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

        await innerDownload(self, path, bot, session)

    async def download(self, path: str, bot: Bot, session: ClientSession = None, attemptCount: int | None = None,
                       waitAfterFail: int | float | None = None):
        """
        文件下载封装，记录下载异常信息，将下载异常的文件传入异常进行处理\n
        由于异步并发的原因，因此无法直接try..catch来处理异常。通过将其包裹到一个新异常中，从而传入文件信息以待后续处理。\n
        + 当下载失败时：抛出FileDownloadException异常
        + 当下载成功时：写入文件的最后修改时间、文件本地ID
        """
        try:
            await self._download(path=path, bot=bot, session=session, waitAfterFail=waitAfterFail, attemptCount=attemptCount)
        except Exception:
            logger.opt(colors=True).error(f"<red>文件{self.file_name}下载失败</red>")
            raise FileDownloadException(self)
        else:
            logger.opt(colors=True).success(f"<green>成功下载文件{self.file_name}</green>")
            stat = os.stat(path)
            self.local_file_id = stat.st_ino
            self.local_modify_time = stat.st_mtime_ns
            return self

    async def upload(self, bot: Bot, uploaderID: int = 0, oldFolder: QQGroupFolder = None) -> str:
        """
        调用go-cq的api进行文件上传：文件的上传将不使用并发，避免封号。\n
        当文件的文件夹不存在时：将不进行上传。因此，若需上传文件至群聊中不存在的文件夹，应该新建文件夹。\n

        :param bot: cqbot
        :param uploaderID: 当提供了uploaderID将更精确地找到对应文件
        :param oldFolder: 提供上传前的群文件夹数据，便于比对
        :return: 挂载文件夹id
        """
        if oldFolder is None:
            oldFolder = QQGroupFolder(group_id=self.group_id, folder_id=None, folder_name=f"{self.group_id}",
                                      create_time=0, creator=0, creator_name="", total_file_count=0,
                                      local_path="")
            await oldFolder.updateInfoFromQQ(bot)
        oldFiles = oldFolder.getAllFiles()
        oldFilesID = [file.file_id for file in oldFiles]
        try:
            folder = self.parentFolder
            if folder is None:
                raise FileUploadException(self, "文件不存在文件夹")
            path = os.path.abspath(self.local_path)
            if folder.folder_id is None:
                # 上传至根文件夹
                await bot.upload_group_file(group_id=self.group_id, file=path, name=self.file_name)
            else:
                await bot.upload_group_file(group_id=self.group_id, file=path, name=self.file_name, folder=folder.folder_id)
        except Exception as e:
            if isinstance(e, FileUploadException):
                raise e
            else:
                raise FileUploadException(self, "文件上传失败")
        else:
            logger.opt(colors=True).success(f"<green>成功上传文件{self.file_name}</green>")
            if folder.folder_id is None:
                filesData = await bot.get_group_root_files(group_id=self.group_id)
            else:
                filesData = await bot.get_group_files_by_folder(group_id=self.group_id, folder_id=folder.folder_id)
            # 反序列化
            filesData = filesData["files"]
            files = [QQGroupFile.from_dict(fileData) for fileData in filesData]
            sameNameFiles: list[QQGroupFile] = []
            for file in files:
                # 跳过不同上传者
                if uploaderID != 0:
                    if uploaderID != file.uploader:
                        continue
                # 跳过旧文件id
                if file.file_id in oldFilesID:
                    continue
                sameNameFiles.append(file)
            if len(sameNameFiles) == 0:
                raise FileUploadException(self, "群文件夹中未找到上传文件")
            sameNameFiles = sorted(sameNameFiles, key=lambda file: file.upload_time, reverse=True)
            file = sameNameFiles[0]  # 取最近一个上传的文件为准
            # 更新文件信息
            self.group_id = file.group_id
            self.file_id = file.file_id
            self.file_name = file.file_name
            self.busid = file.busid
            self.file_size = file.file_size
            self.upload_time = file.upload_time
            self.dead_time = file.dead_time
            self.modify_time = file.modify_time
            self.download_times = file.download_times
            self.uploader = file.uploader
            self.uploader_name = file.uploader_name
            # 移出local_file
            if self in folder.local_files:
                folder.local_files.remove(self)
                folder.files[self.file_id] = self
            return folder.folder_id

    async def deleteFromGroup(self, bot: Bot):
        try:
            await bot.delete_group_file(group_id=self.group_id, file_id=self.file_id, busid=self.busid)
        except:
            raise FileDeleteException(self, f"文件{self.file_name}删除失败")


class FileDownloadException(Exception):
    """文件下载异常类"""

    def __init__(self, file: QQGroupFile):
        self.file = file


class FileUploadException(Exception):
    """文件上传异常类"""

    def __init__(self, file: QQGroupFile, reason: str = ""):
        self.file = file
        self.reason = reason


class FileDeleteException(Exception):
    """文件删除异常"""

    def __init__(self, file: QQGroupFile, reason: str = ""):
        self.file = file
        self.reason = reason


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
        self.depth: int = 0
        self.files: dict[str, QQGroupFile] = dict()
        self.folders: dict[str, QQGroupFolder] = dict()
        self.local_files: list[QQGroupFile] = list()  # 用于存储尚未上传至群的所有本地文件
        self.local_folders: list[QQGroupFolder] = list()  # 用于存储尚未上传至群的所有本地文件夹
        # 不存储数据
        self.parentFolder: QQGroupFolder | None = None  # 用于指向父节点

    def _updateDepth(self):
        for folder in self.folders.values():
            folder.depth = self.depth + 1
            folder._updateDepth()
        for local_folder in self.local_folders:
            local_folder.depth = self.depth + 1
            local_folder._updateDepth()

    def __add__(self, other):
        """向文件夹中添加子文件或子文件夹"""

        if isinstance(other, QQGroupFile):
            # id不存在视为临时本地文件
            if other.file_id == "":
                other.parentFolder = self
                self.local_files.append(other)
            else:
                other.parentFolder = self
                self.files[other.file_id] = other
        elif isinstance(other, QQGroupFolder):
            if other.folder_id == "":
                other.parentFolder = self
                self.local_folders.append(other)
            else:
                other.parentFolder = self
                self.folders[other.folder_id] = other
            # 更新深度
            self._updateDepth()
        else:
            raise TypeError("不能将QQGroupFolder与QQGroupFile或QQGroupFolder以外的类型相加")
        return self

    def add(self, node):
        """向文件夹中添加子文件或子文件夹"""
        if isinstance(node, QQGroupFile):
            # id不存在视为临时本地文件
            if node.file_id == "":
                node.parentFolder = self
                self.local_files.append(node)
            else:
                node.parentFolder = self
                self.files[node.file_id] = node
        elif isinstance(node, QQGroupFolder):
            if node.folder_id == "":
                node.parentFolder = self
                self.local_folders.append(node)
            else:
                node.parentFolder = self
                self.folders[node.folder_id] = node
            # 更新深度
            self._updateDepth()
        else:
            raise TypeError("不能将QQGroupFolder与QQGroupFile或QQGroupFolder以外的类型加入QQGroupFile")
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
            "depth": self.depth,
            "files": {fid: f.to_dict() for fid, f in self.files.items()},
            "folders": {fid: f.to_dict() for fid, f in self.folders.items()},
            "local_files": [file.to_dict() for file in self.local_files],
            "local_folders": [folder.to_dict() for folder in self.local_folders]
        }

    @classmethod
    def from_dict(cls, data: dict[str, any]):
        thisFolder = cls(data["group_id"], data["folder_id"], data["folder_name"], data["create_time"], data["creator"], data["creator_name"],
                         data["total_file_count"])
        if "local_path" in data.keys():
            thisFolder.local_path = data["local_path"]
        if "files" in data.keys():
            for file in data["files"].values():
                thisFolder = thisFolder + QQGroupFile.from_dict(file)
        if "local_files" in data.keys():
            for local_file in data["local_files"]:
                thisFolder = thisFolder + QQGroupFile.from_dict(local_file)
        if "folders" in data.keys():
            for folder in data["folders"].values():
                thisFolder = thisFolder + QQGroupFolder.from_dict(folder)
        if "local_folders" in data.keys():
            for local_folder in data["local_folders"]:
                thisFolder = thisFolder + QQGroupFolder.from_dict(local_folder)
        if "depth" in data.keys():
            thisFolder.depth = data["depth"]

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
                self.add(file)
        # 添加子文件夹信息
        if info["folders"] is not None:
            for folder in info["folders"]:
                folder = QQGroupFolder.from_dict(folder)
                self.add(folder)
                # 递归添加子文件夹信息
                await folder.updateInfoFromQQ(bot)

    # 递归获取文件夹中所有文件，包括local_file
    def getAllFiles(self) -> list[QQGroupFile]:
        """递归获取文件夹中所有文件，包括local_file"""
        files: list[QQGroupFile] = []
        files += [f for f in self.files.values()]
        files += self.local_files
        for folder in self.folders.values():
            files += folder.getAllFiles()
        for folder in self.local_folders:
            files += folder.getAllFiles()
        return files

    # 递归获取文件夹中所有文件夹，包括自身，包括local_folder
    def getAllFolders(self) -> list:
        """递归获取文件夹中所有文件夹，包括自身，包括local_folder"""
        folders: list = [self]
        folders += self.local_folders
        for folder in self.folders.values():
            folders += folder.getAllFolders()

        return folders

    # 根据本地路径获取对应文件夹，不区分用户名模式
    def getFolderByLocalPath(self, localPath: str) -> QQGroupFolder | None:
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

        for folder in self.local_folders:
            result = folder.getFolderByLocalPath(localPath)
            if result is not None:
                return result
        return None

    # 移动file节点到指定文件夹路径
    def moveFileToDir(self, file: QQGroupFile, dirPath: str) -> bool:
        """
        移动self下的file节点到指定文件夹路径，只移动节点不移动本地文件。dirPath请传入目录路径！

        :param file: 需要移动的文件
        :param dirPath: 移动到指定路径
        :return: False：移动失败 True：移动成功
        """
        if file not in self.local_files and file not in self.files.values():
            return False
        # 找到目标文件夹
        result, folder = self.createFolderByLocalPath(dirPath)
        if result == -1:
            return False
        # 检查文件夹是否已有对应文件
        for f in folder.files.values():
            if file.file_id == f.file_id:
                return False
        for f in folder.local_files:
            if file.local_file_id == f.local_file_id:
                return False

        # 从原文件夹中移除并挂树
        if file in self.local_files:
            self.local_files.remove(file)
            folder.add(file)
            return True
        elif file.file_id in self.files.keys():
            self.files.pop(file.file_id)
            folder.add(file)
            return True

        return False

    # 将file挂载到指定id的目录
    def moveFileToDirByFolderID(self, file: QQGroupFile, folderID: str) -> bool:
        """将文件移动到指定id的文件夹"""
        if self.parentFolder is not None:
            rootFolder = self.parentFolder
        else:
            rootFolder = self
        while rootFolder.parentFolder is not None:
            rootFolder = rootFolder.parentFolder
        folders = rootFolder.getAllFolders()
        foldersDict = {folder.folder_id: folder for folder in folders}
        if folderID not in foldersDict.keys():
            return False

        folder = foldersDict[folderID]

        # 从原文件夹中移除并挂树
        if file in self.local_files:
            self.local_files.remove(file)
            folder.add(file)
            return True
        if file.file_id in self.files.keys():
            self.files.pop(file.file_id)
            folder.add(file)
            return True
        return False

    # 根据本地路径的实际情况，删除路径不存在的节点，更改路径变动的节点，添加本地未记录节点
    def checkLocalPath(self):
        deleteFiles = []
        localDict = getLocalFilesID(self.local_path, ignoreFolders={".config", ".log"})
        files = self.getAllFiles()
        for file in files:
            # 删除无local_id节点
            if file.local_file_id == 0:
                deleteFiles.append(file)
            if file.local_file_id != 0:
                # 删除local_id节点无本地映射的节点
                if file.local_file_id not in localDict.keys():
                    deleteFiles.append(file)
                else:
                    # 更新本地信息
                    file.local_path = localDict[file.local_file_id]
                    file.local_modify_time = os.stat(file.local_path).st_mtime_ns
        for file in deleteFiles:
            result = self.delete(file)
            logger.opt(colors=True).debug(f"<blue>删除文件节点{file.file_name}，操作{'成功' if result else '失败'}</blue>")
        # 查找本地未记录节点
        files = self.getAllFiles()
        local_ids = {file.local_file_id for file in files}
        for local_id in localDict.keys():
            if local_id not in local_ids:
                newFile = QQGroupFile.createFromLocalFile(group_id=self.group_id, path=localDict[local_id])
                self.add(newFile)
                self.moveFileToDir(file=newFile, dirPath=os.path.dirname(newFile.local_path.strip("/")))

    # 删除节点
    def delete(self, node: QQGroupFolder | QQGroupFile) -> bool:
        """将对应的节点移除，仅允许移除同树节点。成功返回True，失败返回False"""
        if not isinstance(node, (QQGroupFolder, QQGroupFile)):
            return False
        nodeRoot = node.parentFolder
        if nodeRoot is None:
            return False
        while nodeRoot.parentFolder is not None:
            nodeRoot = nodeRoot.parentFolder
        if self.parentFolder is not None:
            selfRoot = self.parentFolder
            while selfRoot.parentFolder is not None:
                selfRoot = selfRoot.parentFolder
        else:
            selfRoot = self
        if selfRoot != nodeRoot:
            return False

        parent = node.parentFolder
        if isinstance(node, QQGroupFolder):
            if node in parent.local_folders:
                parent.local_folders.remove(node)
                return True
            if node.folder_id in parent.folders.keys():
                parent.folders.pop(node.folder_id)
                return True
        if isinstance(node, QQGroupFile):
            if node in parent.local_files:
                parent.local_files.remove(node)
                return True
            if node.file_id in parent.files.keys():
                parent.files.pop(node.file_id)
                return True
        return False

    # 根据localPath在文件树中搜索并创建新文件夹节点
    def createFolderByLocalPath(self, localPath: str, initFlag: bool = True) -> (int, QQGroupFolder):
        """
        根据本地路径创建新文件夹节点：仅在文件树上创建文件夹节点，而不在文件系统中创建实际的文件夹。\n
        注意：文件夹的localPath并不与实际路径完全对应。在-o模式下是对应的，但是在默认的模式下是不包含上传者用户名的，而实际路径包含。\n
        注意：因此，在默认模式下，应预处理路径。\n

        :param localPath: 待创建文件夹路径
        :param initFlag: 初始化标志，避免无限递归。在外部使用时使用默认值即可，无需考虑该参数。
        :return: 创建成功返回(1,创建文件夹)，文件夹节点已存在返回(0,文件夹)，未创建成功返回(-1,None)
        """
        # 找到根节点后再根据根节点创建
        if self.parentFolder is not None and initFlag:
            rootFolder = self.parentFolder
            while rootFolder.parentFolder is not None:
                rootFolder = rootFolder.parentFolder
            return rootFolder.createFolderByLocalPath(localPath, False)
        # 由于文件夹路径格式统一，因此若不满足包含关系则localPath对应的路径肯定不在对应文件夹里
        if not localPath.startswith(self.local_path):
            return -1, None
        else:
            if localPath == self.local_path:
                return 0, self  # 文件夹已存在
            relPath = os.path.relpath(localPath, self.local_path).replace("\\", "/")
            # 文件夹为该节点的子节点
            if "/" not in relPath:
                # 说明localPath是self的子节点
                for folder in self.folders.values():
                    if folder.local_path == localPath:
                        return 0, folder
                for folder in self.local_folders:
                    if folder.local_path == localPath:
                        return 0, folder
                # 说明文件夹节点不存在，准备创建
                newFolder = QQGroupFolder(group_id=self.group_id, folder_id="", folder_name=relPath, create_time=-1, creator=-1, creator_name="",
                                          total_file_count=0, local_path=localPath)
                self.add(newFolder)
                return 1, newFolder
            # 仍非子节点，继续寻找
            else:
                # 尝试在群文件夹中创建
                for folder in self.folders.values():
                    result, f = folder.createFolderByLocalPath(localPath, False)
                    if result == 0 or result == 1:
                        return result, f
                # 尝试在本地文件夹中创建
                for folder in self.local_folders:
                    result, f = folder.createFolderByLocalPath(localPath, False)
                    if result == 0 or result == 1:
                        return result, f
                # 路径不存在，说明需要递归创建子文件夹
                relPaths = relPath.strip("/").split("/")
                newFolder = QQGroupFolder(group_id=self.group_id, folder_id="", folder_name=relPaths[0], create_time=-1, creator=-1, creator_name="",
                                          total_file_count=0, local_path=localPath)
                self.add(newFolder)
                return newFolder.createFolderByLocalPath(localPath, False)

    # 遍历文件夹，计算所有文件夹的本地下载路径，返回收集到的所有文件列表
    def calculateLocalPaths(self, dir_path: str) -> list[QQGroupFile]:
        """遍历文件夹，计算所有文件夹的本地下载路径，返回收集到的所有文件列表。"""
        files: list[QQGroupFile] = []
        # 修改自身信息
        self.local_path = os.path.join(dir_path, self.folder_name).replace("\\", "/")
        DirExist(self.local_path)
        # 遍历修改所有子文件信息
        fileNames = set()
        for file in self.files.values():
            filePath = os.path.join(self.local_path, file.file_name)
            count = 1
            while filePath in fileNames:
                # 文件名冲突，尝试重命名
                filePath = os.path.join(self.local_path, file.file_name)
                filePath = os.path.splitext(filePath)[0] + f"({count})" + os.path.splitext(filePath)[1]
                count += 1
            fileNames.add(filePath)
            file.local_path = filePath.replace("\\", "/")
            files.append(file)

        # 遍历修改所有子文件夹信息
        for folder in self.folders.values():
            files += folder.calculateLocalPaths(self.local_path)

        return files

    # 遍历文件夹，计算所有文件夹的本地下载路径，文件路径结构为群号/人名/群文件，返回收集到的所有文件列表
    def calculateLocalPathsByName(self, dir_path: str) -> list[QQGroupFile]:
        """
        遍历文件夹，计算所有文件夹的本地下载路径，文件路径结构为群名/人名/群文件，返回收集到的所有文件列表

        :param dir_path: 文件夹路径
        """
        fileNames: dict[str, set[str]] = dict()  # 用于统计重复的文件名
        fileDirs = set()  # 用于统计相同的文件夹

        def _updateLocalPathsByName(folder: QQGroupFolder, dir_path: str, basePath: str) -> list[QQGroupFile]:
            """遍历闭包函数"""
            # 修改自身信息
            # 对于文件夹而言，其记录的localPath并非实际的Path，而与updateLocalPaths的路径保持一致
            files: list[QQGroupFile] = []
            folder.local_path = os.path.join(dir_path, folder.folder_name).replace("\\", "/")
            for file in folder.files.values():
                # 修正用户名，避免出现非法字符
                if os.name == "nt":
                    file.uploader_name = re.sub(pattern=r'[\/:*?"<>|]', string=file.uploader_name, repl="")
                    if file.uploader_name == "":
                        file.uploader_name = "default"
                else:
                    file.uploader_name = file.uploader_name.replace("/", "")
                    if file.uploader_name == "":
                        file.uploader_name = "default"
                # 计算文件实际路径目录
                relPath = os.path.relpath(folder.local_path, basePath)
                fileDir = os.path.join(basePath, file.uploader_name, relPath)
                if fileDir not in fileDirs:
                    DirExist(fileDir)
                    fileDirs.add(fileDir)
                    fileNames[fileDir] = set()
                filePath = os.path.normpath(os.path.join(fileDir, file.file_name))
                # 检查文件名是否重复
                count = 1
                while filePath in fileNames[fileDir]:
                    # 文件名冲突，尝试重命名
                    filePath = os.path.normpath(os.path.join(fileDir, file.file_name))
                    filePath = os.path.splitext(filePath)[0] + f"({count})" + os.path.splitext(filePath)[1]
                    count += 1
                fileNames[fileDir].add(filePath)
                file.local_path = filePath.replace("\\", "/")
                files.append(file)

            # 遍历修改所有子文件夹信息
            for _folder in folder.folders.values():
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
                        file.download(path=file.local_path, bot=bot, session=session, waitAfterFail=waitAfterFail, attemptCount=attemptCount))
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
        self.checkLocalPath()

        # 打印最终结果
        # 打印文件树
        log_path = os.path.join(self.local_path, ".config")
        DirExist(log_path)
        log_path = os.path.join(log_path, "config.json")
        with open(file=log_path, mode="w", encoding="utf-8") as f:
            f.write(self.dumps())
        # 打印日志信息

        return msg

    async def syncFromGroup(self, *, dirPath: str, bot: Bot, concurrentNum: int = 20, ignoreTempFile: bool = False, attemptCount: int | None = None,
                            waitAfterFail: int | float | None = None, connectTimeout: float | None = 2, downloadTimeout: float | None = 5,
                            mode: str = "ByName") -> str:
        """
        **该函数仅限使用位置参数进行函数调用，避免将来可能的改动造成破坏性影响**\n
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
                                         waitAfterFail=waitAfterFail, connectTimeout=connectTimeout, downloadTimeout=downloadTimeout, mode=mode)
            return result

        # 2. 尝试读取本地config.json进行同步，若失败则调用download覆盖下载
        try:
            with open(configPath, mode="r", encoding="utf-8") as f:
                data = f.read()
            data = json.loads(data)
            localGroupFolder = QQGroupFolder.from_dict(data)
        except Exception:
            result = await self.download(dirPath=dirPath, bot=bot, concurrentNum=concurrentNum, ignoreTempFile=ignoreTempFile, attemptCount=attemptCount,
                                         waitAfterFail=waitAfterFail, connectTimeout=connectTimeout, downloadTimeout=downloadTimeout)
            return result
        # 3. 将本地文件树与当前群聊文件树进行比对
        # 3.1 根据mode生成当前群聊文件树的本地路径
        if mode == "Origin":
            dirPath = os.path.join(dirPath, "不区分用户名").replace("\\", "/")
            self.calculateLocalPaths(dirPath)
        else:
            dirPath = os.path.join(dirPath, "区分用户名").replace("\\", "/")
            self.calculateLocalPathsByName(dirPath)
        files = self.getAllFiles()
        # 3.2 遍历本地文件树，追踪更改已变动节点
        localGroupFolder.checkLocalPath()
        # 3.3 遍历群聊文件树，与本地文件节点进行对比。不存在的节点：下载，位置变动的节点：移动本地位置
        localFiles = localGroupFolder.getAllFiles()
        localFilesDict: dict[str, QQGroupFile] = {file.file_id: file for file in localFiles if file.file_id != ""}  # 不包含无file_id的节点，即所有local_file
        files_local_id = {file.local_file_id for file in files if file.local_file_id != 0}
        files_id = {file.file_id for file in files if file.file_id != 0}
        # filesDict: dict[str, QQGroupFile] = {file.local_file_id: file for file in files if file.local_file_id != 0}  # 不包含无local_file_id的节点
        tasks = []
        failedFilesPath = set()  # 所有下载错误的路径
        tempFilesPath = set()  # 所有临时文件路径
        totalDownloadBytes = 0  # 总下载字节数
        skipFilesPath = set()  # 所有跳过文件路径
        failedDeleteFilesPath = set()  # 所有删除失败文件路径
        deleteFilesPath = set()  # 所有删除文件路径
        failedMoveFilesPath = set()  # 所有移动失败文件路径
        moveFilesPath = set()  # 所有移动失败文件路径
        async with asyncio.Semaphore(concurrentNum):
            timeout = ClientTimeout(connect=connectTimeout, sock_read=downloadTimeout)
            connector = TCPConnector(limit=concurrentNum)
            async with ClientSession(timeout=timeout, connector=connector) as session:
                # 对于群聊文件树的所有文件
                for file in files:
                    # 文件在本地文件树不存在：此处是不比较local_file的，因为local_file在QQ上不存在，比较没有任何意义。
                    if file.file_id not in localFilesDict.keys():
                        # 不是临时文件，或者是临时文件，但是下载模式下载临时文件：下载文件
                        if (file.dead_time != 0 and not ignoreTempFile) or file.dead_time == 0:
                            task = asyncio.create_task(
                                file.download(path=file.local_path, bot=bot, session=session, waitAfterFail=waitAfterFail, attemptCount=attemptCount))
                            tasks.append(task)
                        # 跳过临时文件
                        else:
                            tempFilesPath.add(file.local_path)
                    # 文件在本地文件树存在
                    else:
                        localFile = localFilesDict[file.file_id]
                        # 文件在实际地址上存在
                        if os.path.isfile(localFile.local_path):
                            # 文件的服务器最后修改时间发生变动 或 文件与服务器文件不一致
                            if localFile.modify_time != file.modify_time \
                                    or os.path.getsize(localFile.local_path) != file.file_size:
                                # 不是临时文件，或者是临时文件，但是下载模式下载临时文件：删除本地文件，下载群聊文件
                                if (file.dead_time != 0 and not ignoreTempFile) or file.dead_time == 0:
                                    try:
                                        os.remove(path=localFile.local_path)
                                    # 删除失败，因此抛出异常：此时取消文件的下载。
                                    except FileNotFoundError | PermissionError | IsADirectoryError | NotADirectoryError | OSError as error:
                                        match error:
                                            case FileNotFoundError():
                                                errorMsg = "文件不存在"
                                            case PermissionError():
                                                errorMsg = "没有访问权限"
                                            case IsADirectoryError():
                                                errorMsg = "路径为目录"
                                            case OSError():
                                                errorMsg = "操作系统异常"
                                            case NotADirectoryError():
                                                errorMsg = "路径不是目录"
                                        # 回写本地文件信息
                                        file.local_file_id = localFile.local_file_id
                                        file.local_modify_time = os.stat(file.local_path).st_mtime_ns
                                        logger.opt(colors=True).error(f"<red>删除文件{file.file_name}失败：{errorMsg}</red>")
                                        failedDeleteFilesPath.add(localFile.local_path)
                                    else:
                                        deleteFilesPath.add(localFile.local_path)
                                        logger.opt(colors=True).debug(f"<blue>重下文件{file.file_name}</blue>")
                                        task = asyncio.create_task(
                                            file.download(path=file.local_path, bot=bot, session=session, waitAfterFail=waitAfterFail,
                                                          attemptCount=attemptCount))
                                        tasks.append(task)
                                # 是临时文件，不进行下载，但是进行挂树：将节点挂在实际路径下
                                else:
                                    result = self.moveFileToDir(file, os.path.dirname(localFile.local_path.strip("/")))
                                    if not result:
                                        failedMoveFilesPath.add(result)
                                    file.local_path = localFile.local_path
                                    file.local_file_id = localFile.local_file_id
                                    file.local_modify_time = localFile.local_modify_time
                            # 文件与服务器文件不一致 最后修改日期也未变，但是地址变动：移动本地文件
                            elif localFile.local_path != file.local_path:
                                try:
                                    shutil.move(src=localFile.local_path, dst=file.local_path)
                                except FileNotFoundError | PermissionError | IsADirectoryError | OSError | NotADirectoryError as error:
                                    # 对于移动失败的文件节点：由于移动失败，因此文件将不存在local_id属性，会在接下来的本地树回挂中挂上
                                    match error:
                                        case FileNotFoundError():
                                            errorMsg = "文件不存在"
                                        case PermissionError():
                                            errorMsg = "没有访问权限"
                                        case IsADirectoryError():
                                            errorMsg = "路径为目录"
                                        case OSError():
                                            errorMsg = "操作系统异常"
                                        case NotADirectoryError():
                                            errorMsg = "路径不是目录"
                                    logger.opt(colors=True).error(f"<red>移动文件{file.file_name}失败：{errorMsg}</red>")
                                    failedMoveFilesPath.add(localFile.local_path)
                                else:
                                    # 复制本地树的属性
                                    file.local_modify_time = os.stat(file.local_path).st_mtime_ns
                                    file.local_file_id = localFile.local_file_id
                                    moveFilesPath.add(f"{localFile.local_path} 移动到 {file.local_path}")
                                    logger.opt(colors=True).debug(f"<blue>移动文件{file.file_name}</blue>")
                            # 文件未发生变动：将本地文件信息更新到群聊文件树
                            else:
                                file.local_file_id = localFile.local_file_id
                                file.local_modify_time = localFile.local_modify_time
                                skipFilesPath.add(file)
                        # 文件在实际地址上不存在：下载文件
                        else:
                            task = asyncio.create_task(
                                file.download(path=file.local_path, bot=bot, session=session, waitAfterFail=waitAfterFail, attemptCount=attemptCount))
                            tasks.append(task)

                # 等待所有下载任务完成
                results = await asyncio.gather(*tasks, return_exceptions=True)

        # 3.4 遍历本地文件树，与群聊文件节点进行对比。不存在的节点：回挂在群聊文件树上。
        for file in localFiles:
            # 不存在的节点：挂树
            if (file.local_file_id not in files_local_id) and (file.file_id not in files_id):
                self.add(file)
                self.moveFileToDir(file=file, dirPath=os.path.dirname(file.local_path.strip("/")))
        # 3.5 检查文件树，追踪更改已变动节点
        self.checkLocalPath()
        # 3.6 打印保存文件树
        log_path = os.path.join(self.local_path, ".config")
        DirExist(log_path)
        log_path = os.path.join(log_path, "config.json")
        with open(file=log_path, mode="w", encoding="utf-8") as f:
            f.write(self.dumps())

        # 4 记录log，保存结果
        end = time.time_ns()
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
            msg = f"群文件下载完成，总文件数{len(files)}，总下载文件数{len(files) - len(failedFilesPath) - len(tempFilesPath) - len(skipFilesPath) - len(moveFilesPath)}，" \
                  f"下载错误数{len(failedFilesPath)}，跳过临时文件数{len(tempFilesPath)}，跳过已下载文件数{len(skipFilesPath) + len(moveFilesPath)}。" \
                  f"总下载大小{printSizeInfo(totalDownloadBytes)}，用时{printTimeInfo(end - start, 3)}。\n" \
                  f"下载错误文件列表：\n" \
                  f"{failedFilesPathStr}"
            resultLogFile.write(msg)

            # 打印移动失败列表
            resultLogFile.write("\n\n移动失败文件列表：\n")
            for path in failedMoveFilesPath:
                resultLogFile.write(path + "\n")
            # 打印移动文件列表
            resultLogFile.write("\n移动文件列表：\n")
            for path in moveFilesPath:
                resultLogFile.write(path + "\n")
            # 打印删除失败列表
            resultLogFile.write("\n删除失败文件列表：\n")
            for path in failedDeleteFilesPath:
                resultLogFile.write(path + "\n")
            # 打印删除文件列表
            resultLogFile.write("\n删除文件列表：\n")
            for path in deleteFilesPath:
                resultLogFile.write(path + "\n")

        return msg

    async def syncToGroup(self, *, bot: Bot, waitTime: float):
        """
        **该函数仅限使用位置参数进行函数调用，避免将来可能的改动造成破坏性影响**\n
        从本地将文件上传至群聊。\n
        在调用此函数时，self应为从config.json反序列化的本地文件夹\n
        在区分用户名模式下，无法直观地建立本地文件夹到群聊文件夹的映射，因此，区分用户名模式不支持上传同步，或者会造成期待以外的结果。

        :param bot cqBot
        :param waitTime 文件上传等待间隔，单位秒
        """
        # 群文件夹
        groupFolder = QQGroupFolder(group_id=self.group_id, folder_id=None, folder_name=f"{self.group_id}",
                                    create_time=0, creator=0, creator_name="", total_file_count=0,
                                    local_path="")
        await groupFolder.updateInfoFromQQ(bot)  # 从QQ拉取当前群聊的消息
        # 本地文件夹检查
        self.checkLocalPath()
        # 比对，并上传
        files = self.getAllFiles()
        groupFiles = groupFolder.getAllFiles()
        groupFilesID = {file.file_id for file in groupFiles}
        fileUploadExceptions = []
        fileRefreshExceptions = []
        uploadFiles = []
        updateFiles = []
        for file in files:
            # 不在id记录中的文件，进行上传
            if file.file_id not in groupFilesID:
                try:
                    await file.upload(bot=bot, uploaderID=int(bot.self_id), oldFolder=groupFolder)
                    await asyncio.sleep(waitTime)
                except FileUploadException as e:
                    fileUploadExceptions.append(e)
                else:
                    uploadFiles.append(file)
            # 最后修改日期变动的文件，进行先上传后删除
            if file.local_modify_time != os.stat(file.local_path).st_mtime_ns:
                try:
                    old_file_id = file.file_id
                    old_busid = file.busid
                    await file.upload(bot=bot, uploaderID=int(bot.self_id), oldFolder=groupFolder)
                    await asyncio.sleep(waitTime)
                except FileUploadException as e:
                    fileRefreshExceptions.append(e)
                else:
                    self.add(file)
                    try:
                        await bot.delete_group_file(group_id=self.group_id, file_id=old_file_id, busid=old_busid)
                    except FileDeleteException as e:
                        fileRefreshExceptions.append(e)
                    else:
                        updateFiles.append(file)
        # 打印配置
        configPath = os.path.join(self.local_path, ".config", "config.json")
        with open(file=configPath, mode="w", encoding="utf-8") as f:
            f.write(self.dumps())
        # 打印日志
        uploadFailsMsg = "\n上传失败文件：\n"
        uploadFailsMsg = uploadFailsMsg + "\n".join([os.path.relpath(path, self.local_path).replace("\\", "/") for path in
                                                     [e.file.local_path for e in fileUploadExceptions]]) if fileUploadExceptions else ""
        updateFailsMsg = "\n更新失败文件：\n"
        updateFailsMsg = updateFailsMsg + "\n".join([os.path.relpath(path, self.local_path).replace("\\", "/") for path in
                                                     [e.file.local_path for e in fileRefreshExceptions]]) if fileRefreshExceptions else ""
        uploadFilesMsg = "\n".join([os.path.relpath(path, self.local_path).replace("\\", "/") for path in
                                    [file.local_path for file in uploadFiles]])
        updateFilesMsg = "\n".join([os.path.relpath(path, self.local_path).replace("\\", "/") for path in
                                    [file.local_path for file in updateFiles]])
        date = datetime.datetime.now().strftime("上传同步——%Y年%m月%d日 %H时%M分%S秒")
        logDir = os.path.join(self.local_path, ".log", date)
        DirExist(logDir)
        resultLogPath = os.path.join(logDir, f"result.log")
        errorLogPath = os.path.join(logDir, f"error.log")
        msg = f"上传同步完成，上传文件{len(uploadFiles)}个，更新文件{len(updateFiles)}个，上传失败{len(fileUploadExceptions)}个，更新失败{len(fileRefreshExceptions)}个。"
        msg += f"\n上传文件列表：\n{uploadFilesMsg}" if uploadFilesMsg else ""
        msg += f"\n更新文件列表：\n{updateFilesMsg}" if updateFilesMsg else ""
        msg += f"{uploadFailsMsg}{updateFailsMsg}"

        with open(file=resultLogPath, mode="a", encoding="utf-8") as resultLogFile:
            resultLogFile.write(msg)
        with open(file=errorLogPath, mode="a", encoding="utf-8") as errorLogFile:
            for error in fileUploadExceptions:
                traceback.print_exception(type(error), error, error.__traceback__, file=errorLogFile)
            for error in fileRefreshExceptions:
                traceback.print_exception(type(error), error, error.__traceback__, file=errorLogFile)
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


def getFileID(path: str):
    """获取文件ID"""

    if not os.path.exists(path):
        raise FileNotFoundError()
    else:
        return os.stat(path).st_ino


def getLocalFilesID(path: str, ignoreFolders: set[str] = None) -> dict[int, str]:
    """
    递归提取路径下所有文件的id-路径字典，不包括文件夹，若路径不存在则返回空字典

    :param path 待提取路径
    :param ignoreFolders 无视该路径下的文件夹名
    """
    if ignoreFolders is None:
        ignoreFolders = set()
    totalResult = {}
    if os.path.isfile(path):
        totalResult[os.stat(path).st_ino] = os.path.normpath(path).replace("\\", "/").strip("/")
        return totalResult
    if os.path.isdir(path):
        files = os.listdir(path)
        for file in files:
            if file in ignoreFolders and os.path.isdir(os.path.join(path, file)):
                continue
            totalResult.update(getLocalFilesID(os.path.join(path, file)))
    return totalResult
