"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/31-15:44
@Desc: QQ群组文件相关封装
@Ver : 1.0.0
"""
import json
import os
from tenacity import retry, stop_after_attempt
from aiohttp import ClientSession, ClientTimeout
import aiofiles

from nonebot.adapters.onebot.v11 import Bot

from Hiyori.Utils.File import DirExist


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

    @retry(stop=stop_after_attempt(3))
    async def download(self, path: str, bot: Bot, session: ClientSession = None):
        """
        将群文件下载到本地文件夹，最多尝试三次。
        :param bot: bot
        :param path: 本地路径
        :param session: 若传入session则使用session，否则使用独立session
        """
        url = await bot.get_group_file_url(group_id=self.group_id, file_id=self.file_id, busid=self.busid)
        url = url["url"]
        print(f"尝试下载文件{self.file_name}")
        if session is None:
            async with ClientSession() as s:
                async with s.get(url=url) as response:
                    async with aiofiles.open(file=path, mode="wb") as file:
                        # 默认设置流式传输为 20M，需要更小则自行设置
                        async for chunk in response.content.iter_chunked(20 * 1024 * 1024):
                            await file.write(chunk)
        else:
            async with session.get(url=url) as response:
                async with aiofiles.open(file=path, mode="wb") as file:
                    # 默认设置流式传输为 20M，需要更小则自行设置
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

    async def download(self, path: str, bot: Bot, session: ClientSession = None) -> (int, list):
        """
        将群文件夹中的所有文件递归下载至指定文件夹。\n
        对于重名文件的处理：\n
        + 若下载文件夹存在同名文件，直接覆盖\n
        + 若群聊文件夹存在同盟文件夹，添加后缀\n

        :param path: 指定下载目录，对于本folder来说，文件将会被下载到path/self.folder_name目录下
        :param bot: bot
        :param session: 若传入session则使用session，否则使用独立session
        :return: 下载文件大小，错误信息列表
        """
        downloadSize = 0
        downloadError = []
        folderPath = os.path.join(path, self.folder_name)
        # 由母文件夹判断路径存在性
        DirExist(folderPath)
        if session is None:
            timeout = ClientTimeout(connect=2)
            async with ClientSession(timeout=timeout) as newSession:
                fileNames = set()
                # 下载所有文件
                for file in self.files.values():
                    filePath = os.path.join(folderPath, file.file_name)
                    count = 1
                    while filePath in fileNames:
                        # 文件名冲突，尝试重命名
                        filePath = os.path.join(folderPath, file.file_name)
                        filePath = os.path.splitext(filePath)[0] + f"({count})" + os.path.splitext(filePath)[1]
                        count += 1
                    fileNames.add(filePath)
                    try:
                        await file.download(path=filePath, bot=bot, session=newSession)
                    except Exception:
                        downloadError.append(file.file_name)
                    else:
                        downloadSize += file.file_size
                # 下载所有文件夹
                for folder in self.folders.values():
                    size, error = await folder.download(path=folderPath, bot=bot, session=newSession)
                    downloadSize += size
                    downloadError += error
        else:
            fileNames = set()
            # 下载所有文件
            for file in self.files.values():
                filePath = os.path.join(folderPath, file.file_name)
                count = 1
                while filePath in fileNames:
                    # 文件名冲突，尝试重命名
                    filePath = os.path.join(folderPath, file.file_name)
                    filePath = os.path.splitext(filePath)[0] + f"({count})" + os.path.splitext(filePath)[1]
                    count += 1
                fileNames.add(filePath)
                try:
                    await file.download(path=filePath, bot=bot, session=session)
                except Exception:
                    downloadError.append(file.file_name)
                else:
                    downloadSize += file.file_size
            # 下载所有文件夹
            for folder in self.folders.values():
                size, error = await folder.download(path=folderPath, bot=bot, session=session)
                downloadSize += size
                downloadError += error
        return downloadSize, downloadError
