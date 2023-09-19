"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/9/8-8:26
@Desc: api实现
@Ver : 1.0.0
"""
import asyncio
import json

from Hiyori.Utils.API.Baidu import baidu
from nonebot.matcher import Matcher
import aiohttp
import os
import aiofiles
import hashlib


# from tenacity import retry, stop_after_attempt, wait_fixed


async def getToken(QQ: int, matcher: Matcher) -> int | None:
    status = await baidu.Api.Pan.openapi_Refresh_Access_Token(QQ, matcher)
    if status == 1:
        baidu.dumps()
    elif status == -1:
        await matcher.send("token获取失败，超级管理员未配置key。")
        return None
    return baidu.Api.Pan.userInfo[str(QQ)]["access_token"]


async def userInfo(QQ: int, matcher: Matcher = None) -> dict[str, any] | None:
    """
    获取当前用户信息，若不成功返回None
    :param QQ: 用户QQ号
    :param matcher: 事件matcher

    返回说明\n
    baidu_name	string	百度账号\n
    netdisk_name	string	网盘账号\n
    avatar_url	string	头像地址\n
    vip_type	int	会员类型，0普通用户、1普通会员、2超级会员\n
    uk	int	用户ID
    """
    token = await getToken(QQ, matcher)
    if token is None:
        return None
    url = f"https://pan.baidu.com/rest/2.0/xpan/nas?access_token={token}&method=uinfo"
    # 发送请求
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            result = await response.json()
            return result


async def diskInfo(QQ: int, matcher: Matcher = None) -> dict[str, any] | None:
    """
    获取用户当前网盘信息，若不成功返回None

    :param QQ: 用户QQ号
    :param matcher: 事件matcher

    返回说明\n
    total	int	总空间大小，单位B\n
    expire	bool	7天内是否有容量到期\n
    used	int	已使用大小，单位B\n
    free	int	免费容量，单位B
    """
    token = await getToken(QQ, matcher)
    if token is None:
        return None
    url = f"https://pan.baidu.com/api/quota?access_token={token}&checkfree=1&checkexpire=1"
    # 发送请求
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            result = await response.json()
            print(result)
            return result


async def fileInfoByFids(QQ: int, fids: int | list[int] = None, dlink: int = 1, thumb: int = 1, extra: int = 1, needmedia: int = 1, matcher: Matcher = None) \
        -> list[dict[str, any]] | None:
    """
    根据文件的id查询文件信息，上限100个，若不成功返回None

    :param QQ: 用户QQ号
    :param matcher: 事件matcher
    :param fids: fid，int类型
    :param dlink: 是否需要下载地址, 0为否，1为是
    :param thumb: 是否需要缩略图地址，0为否，1为是
    :param extra: 图片是否需要拍摄时间，原图分辨率等其他信息，0为否，1为是
    :param needmedia: 视频是否需要展示时长信息，单位为秒，0为否，1为是
    :return:

    返回说明\n
    list	json array	文件信息列表 \n
    names	json	如果查询共享目录，该字段为共享目录文件上传者的uk和账户名称 \n
    list[0]["category"]	int	文件类型，含义如下：1 视频， 2 音乐，3 图片，4 文档，5 应用，6 其他，7 种子 \n
    list[0]["dlink”]	string	文件下载地址，参考下载文档进行下载操作 \n
    list[0]["file_name”]	string	文件名 \n
    list[0]["isdir”]	int	是否是目录，为1表示目录，为0表示非目录 \n
    list[0]["server_ctime”]	int	文件的服务器创建Unix时间戳，单位秒 \n
    list[0]["server_mtime”]	int	文件的服务器修改Unix时间戳，单位秒 \n
    list[0]["size”]	int	文件大小，单位字节 \n
    list[0]["thumbs”]	json	缩略图地址 \n
    list[0]["height”]	int	图片高度 \n
    list[0]["width”]	int	图片宽度 \n
    list[0]["date_taken”]	int	图片拍摄时间
    """
    token = await getToken(QQ, matcher)
    url = "https://pan.baidu.com/rest/2.0/xpan/multimedia"
    if isinstance(fids, int):
        fids = [fids]
    fids = str(fids)
    params = {"method": "filemetas", "access_token": token, "fsids": fids, "dlink": dlink,
              "thumb": thumb, "extra": extra, "needmedia": needmedia}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            result = await response.json()
            if result["errno"] == 0:
                return result["list"]
            else:
                return None


async def fileInfo(QQ: int, path: str, dlink: int = 1, thumb: int = 1, extra: int = 1, needmedia: int = 1, matcher: Matcher = None,
                   fuzzy_matching: bool = False, ignoreFolder: bool = False, ignoreFile: bool = False) -> dict[str, any] | None:
    """
    文件信息查询，支持文件模糊查询，若未查询到结果返回None，否则返回对应信息
    :param QQ: 用户QQ号
    :param matcher: 事件matcher
    :param path: 文件路径
    :param dlink: 是否需要下载地址, 0为否，1为是
    :param thumb: 是否需要缩略图地址，0为否，1为是
    :param extra: 图片是否需要拍摄时间，原图分辨率等其他信息，0为否，1为是
    :param needmedia: 视频是否需要展示时长信息，单位为秒，0为否，1为是
    :param fuzzy_matching: 是否进行模糊匹配，为True则进行模糊匹配
    :param ignoreFolder: 是否无视文件夹，为True则不匹配文件夹，一般在模糊匹配下使用
    :param ignoreFile: 是否无视文件，为True则不匹配问价，一般在模糊匹配下使用

    返回说明\n
    list	json array	文件信息列表 \n
    names	json	如果查询共享目录，该字段为共享目录文件上传者的uk和账户名称 \n
    list[0]["category"]	int	文件类型，含义如下：1 视频， 2 音乐，3 图片，4 文档，5 应用，6 其他，7 种子 \n
    list[0]["dlink”]	string	文件下载地址，参考下载文档进行下载操作 \n
    list[0]["filename”]	string	文件名 \n
    list[0]["isdir”]	int	是否是目录，为1表示目录，为0表示非目录 \n
    list[0]["server_ctime”]	int	文件的服务器创建Unix时间戳，单位秒 \n
    list[0]["server_mtime”]	int	文件的服务器修改Unix时间戳，单位秒 \n
    list[0]["size”]	int	文件大小，单位字节 \n
    list[0]["thumbs”]	json	缩略图地址 \n
    list[0]["height”]	int	图片高度 \n
    list[0]["width”]	int	图片宽度 \n
    list[0]["date_taken”]	int	图片拍摄时间
    """
    # 文件路径标准化
    if path.endswith("/"):
        path = path.rstrip("/")
    dirPath = os.path.dirname(path)  # 路径名
    fileName = os.path.basename(path)  # 文件名
    infos = await listDir(QQ=QQ, path=dirPath, matcher=matcher)
    if infos is not None:
        for info in infos:
            # 若进行模糊匹配，则只需文件开头相同
            if (info["server_filename"].startswith(fileName) and fuzzy_matching) or info["server_filename"] == fileName:
                # 无视文件夹类型
                if ignoreFolder and info["isdir"] == 1:
                    continue
                # 无视文件类型
                if ignoreFile and info["isdir"] == 0:
                    continue
                fid = info["fs_id"]
                info = await fileInfoByFids(QQ=QQ, matcher=matcher, fids=fid, dlink=dlink, thumb=thumb, extra=extra, needmedia=needmedia)
                if info is None:
                    return None
                else:
                    return info[0]
    return None


async def listDir(QQ: int, path: str = "/", order: str = "name", desc: int = 1, start: int = 0, limit: int = 100,
                  web: int = 1, folder: int = 0, showempty: int = 1, matcher: Matcher = None) -> list[dict[str, any]] | None:
    """
    获取文件列表，若不成功返回None

    :param QQ: 用户QQ号
    :param matcher: 事件matcher
    :param path: 需要list的目录，以/开头的绝对路径, 默认为/
    :param order: 排序字段：默认为name；time表示先按文件类型排序，后按修改时间排序；name表示先按文件类型排序，后按文件名称排序；(注意，此处排序是按字符串排序的，如果用户有剧集排序需求，需要自行开发)size表示先按文件类型排序，后按文件大小排序。
    :param desc: 默认为升序，设置为1实现降序 （注：排序的对象是当前目录下所有文件，不是当前分页下的文件）
    :param start: 起始位置，从0开始
    :param limit: 查询数目，默认为1000，建议最大不超过1000
    :param web: 值为1时，返回dir_empty属性和缩略图数据
    :param folder: 是否只返回文件夹，0 返回所有，1 只返回文件夹，且属性只返回path字段
    :param showempty: 是否返回dir_empty属性，0 不返回，1 返回

    返回字典参数：\n
    fs_id	uint64	文件在云端的唯一标识ID \n
    path	string	文件的绝对路径 \n
    server_filename	string	文件名称 \n
    size	uint	文件大小，单位B \n
    server_mtime	uint	文件在服务器修改时间 \n
    server_ctime	uint	文件在服务器创建时间 \n
    local_mtime	uint	文件在客户端修改时间 \n
    local_ctime	uint	文件在客户端创建时间 \n
    isdir	uint	是否为目录，0 文件、1 目录 \n
    category	uint	文件类型，1 视频、2 音频、3 图片、4 文档、5 应用、6 其他、7 种子 \n
    md5	string	云端哈希（非文件真实MD5），只有是文件类型时，该字段才存在 \n
    dir_empty	int	该目录是否存在子目录，只有请求参数web=1且该条目为目录时，该字段才存在， 0为存在， 1为不存在 \n
    thumbs	array	只有请求参数web=1且该条目分类为图片时，该字段才存在，包含三个尺寸的缩略图URL \n
    """
    token = await getToken(QQ, matcher)
    if token is None:
        return None
    params = {
        "access_token": token,
        "dir": path,
        "order": order,
        "desc": desc,
        "start": start,
        "limit": limit,
        "web": web,
        "folder": folder,
        "showempty": showempty
    }
    url = f"https://pan.baidu.com/rest/2.0/xpan/file?method=list"
    # 发送请求
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            result = await response.json()
            # print(result)
            if result["errno"] == 0:
                return result["list"]
            else:
                return None


async def listDir_Recurse(QQ: int, path: str = "/", order: str = "name", desc: int = 1, start: int = 0, limit: int = 100,
                          ctime: int = None, mtime: int = None, web: int = 1, matcher: Matcher = None) -> dict[str, any] | None:
    """
        递归获取文件列表，注意返回类型与listDir不同，若不成功返回None

        :param QQ: 用户QQ号
        :param matcher: 事件matcher
        :param path: 需要list的目录，以/开头的绝对路径, 默认为/
        :param order: 排序字段：默认为name；time表示先按文件类型排序，后按修改时间排序；name表示先按文件类型排序，后按文件名称排序；(注意，此处排序是按字符串排序的，如果用户有剧集排序需求，需要自行开发)size表示先按文件类型排序，后按文件大小排序。
        :param desc: 默认为升序，设置为1实现降序 （注：排序的对象是当前目录下所有文件，不是当前分页下的文件）
        :param start: 起始位置，从0开始
        :param limit: 查询数目，默认为1000，建议最大不超过1000
        :param mtime: 文件修改时间，设置此参数，表示只返回修改时间大于mtime的文件
        :param ctime: 文件上传时间，设置此参数，表示只返回上传时间大于ctime的文件
        :param web: 值为1时，返回dir_empty属性和缩略图数据

        返回字典参数：\n
        has_more	int	是否还有下一页，0表示无，1表示有 \n
        cursor	int	当还有下一页时，为下一次查询的起点 \n
        list	list	文件列表 \n
        list[0]["category"] int	文件类型 \n
        list[0]["fs_id"]    int	文件在云端的唯一标识 \n
        list[0]["isdir"]	int	是否是目录，0为否，1为是 \n
        list[0]["local_ctime"]	int	文件在客户端创建时间\n
        list[0]["local_mtime"]	int	文件在客户端修改时间\n
        list[0]["server_ctime"]	int	文件在服务端创建时间\n
        list[0]["server_mtime"] int	文件在服务端修改时间\n
        list[0]["md5"]  string	云端哈希（非文件真实MD5）\n
        list[0]["size"]	int	文件大小\n
        list[0]["thumbs"]   string	缩略图地址\n
    """

    token = await getToken(QQ, matcher)
    if token is None:
        return None
    # 处理地址
    url = f"https://pan.baidu.com/rest/2.0/xpan/multimedia"
    params = {"method": "listall", "access_token": token, "path": path,
              "recursion": 1, "order": order, "desc": desc, "start": start, "limit": limit, "web": web}
    if ctime is not None:
        params["ctime"] = ctime
    if mtime is not None:
        params["mtime"] = mtime
        # 发送请求
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            result = await response.json()
            # print(result)
            if result["errno"] == 0:
                return result
            else:
                return None


async def downloadFile(QQ: int, localPath: str, panPath: str, matcher: Matcher = None, fuzzy_matching: bool = False) -> (int, str):
    """
    将网盘指定目录文件下载至指定文件目录，成功返回文件大小与文件名，失败抛出异常

    :param QQ: 用户QQ号
    :param matcher: 事件matcher
    :param localPath: 文件路径
    :param panPath: 网盘路径
    :param fuzzy_matching: 是否进行模糊匹配，若为true则进行模糊匹配

    :return: 下载文件大小，单位为字节
    """
    # start = time.time_ns()
    info = await fileInfo(QQ=QQ, matcher=matcher, path=panPath, fuzzy_matching=fuzzy_matching, ignoreFolder=True)
    if info is None:
        raise Exception
    else:
        dLink = info["dlink"]
    token = await getToken(QQ, matcher)
    params = {"access_token": token}
    headers = {"User-Agent": "pan.baidu.com"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=dLink, params=params, headers=headers) as response:
            async with aiofiles.open(file=localPath, mode="wb") as file:
                # 默认设置流式传输为 20M，需要更小则自行设置
                async for chunk in response.content.iter_chunked(20 * 1024 * 1024):
                    await file.write(chunk)
    # end = time.time_ns()
    # print((end - start) / (10 ** 9))
    return os.path.getsize(localPath), info["filename"]


async def _preUploadFile(QQ: int, localPath: str, panPath: str, rtype: int = 1, chunkSize: int = 4, matcher: Matcher = None) -> (dict[str, any], list):
    """
    网盘文件分片上传，预上传。若不成功返回None，否则返回分片请求结果。

    :param QQ: 用户QQ号
    :param matcher: 事件matcher
    :param localPath: 本地文件地址
    :param panPath: 网盘地址
    :param rtype: 文件命名策略。1 表示当path冲突时，进行重命名；2 表示当path冲突且block_list不同时，进行重命名；3 当云端存在同名文件时，对该文件进行覆盖
    :param chunkSize: 分片大小

    """

    token = await getToken(QQ, matcher)
    url = f"https://pan.baidu.com/rest/2.0/xpan/file?method=precreate&access_token={token}"
    if not os.path.isfile(localPath):
        return None
    origin_block_list, content_md5 = await _getBlockList(path=localPath, chunkSize=chunkSize)
    block_list = ['"' + b + '"' for b in origin_block_list]
    block_list = '[' + ",".join(block_list) + ']'
    size = os.stat(localPath).st_size
    params = {"path": panPath, "size": size, "isdir": 0, "block_list": block_list, "autoinit": 1, "rtype": rtype, "content-md5": content_md5}
    async with aiohttp.ClientSession() as session:
        # 设置默认超时时长为60s
        async with session.post(url=url, data=params, timeout=60) as response:
            result = await response.json()
            return result, origin_block_list


async def uploadFile(QQ: int, localPath: str, panPath: str, ondup: str = "fail", chunkSize: int = None, matcher: Matcher = None):
    """
    网盘文件上传，

    :param QQ: 用户QQ号
    :param localPath: 本地文件地址
    :param panPath: 网盘地址
    :param ondup: 重名文件策略：1. fail：重名则上传失败  2. overwrite：重名则覆盖  3. newcopy：重名则重命名
    :param chunkSize: 分片大小，单位MB。建议使用默认值
    :param matcher: 事件matcher

    返回说明 \n
    errno	int	错误码\n
    fs_id	uint64	文件在云端的唯一标识ID\n
    md5	string	文件的MD5，只有提交文件时才返回，提交目录时没有该值【单步上传时不返回】\n
    server_filename	string	文件名【单步上传时不返回】\n
    category	int	分类类型, 1 视频 2 音频 3 图片 4 文档 5 应用 6 其他 7 种子【单步上传时不返回】\n
    path	string	上传后使用的文件绝对路径\n
    size	uint64	文件大小，单位B\n
    ctime	uint64	文件创建时间\n
    mtime	uint64	文件修改时间\n
    isdir	int	是否目录，0 文件、1 目录 【单步上传时不返回】\n

    """
    token = await getToken(QQ=QQ, matcher=matcher)
    info = await userInfo(QQ=QQ)
    vip_type = info["vip_type"]
    if chunkSize is None:
        match vip_type:
            case 2:
                chunkSize = 32
            case 1:
                chunkSize = 16
            case _:
                chunkSize = 4
        # 判断文件是否存在
    if not os.path.isfile(localPath):
        raise FileNotFoundError("文件不存在")
    # 小于分片直接单步上传
    if os.stat(localPath).st_size <= chunkSize * 1024 * 1024:
        return await _uploadFile_singleStep(QQ=QQ, localPath=localPath, panPath=panPath, ondup=ondup)

    # 预上传
    panPath = "/" + os.path.join(panPath, os.path.basename(localPath)).replace("\\", "/")
    if ondup == "fail":
        rtype = 0
    elif ondup == "overwrite":
        rtype = 3
    else:
        rtype = 1
    result, block_list = await _preUploadFile(QQ=QQ, localPath=localPath, panPath=panPath, rtype=rtype, chunkSize=chunkSize, matcher=matcher)
    if result["errno"] != 0:
        # 预上传失败，返回预上传结果
        return result
    # 分片上传
    blocks = result["block_list"]
    uploadid = result["uploadid"]
    url = f"https://d.pcs.baidu.com/rest/2.0/pcs/superfile2"
    params = {"method": "upload", "access_token": token, "type": "tmpfile", "path": panPath, "uploadid": uploadid,
              "partseq": 0}
    chunkRead = chunkSize * 1024 * 1024
    async with aiohttp.ClientSession() as session:
        async with aiofiles.open(file=localPath, mode="rb") as file:
            count = 0
            while True:
                chunk = await file.read(chunkRead)
                if not chunk:
                    break
                if count not in blocks:
                    params["partseq"] += 1
                    count += 1
                    continue
                else:
                    data = aiohttp.FormData()
                    data.add_field("file",
                                   value=chunk,
                                   filename="temp__" + os.path.basename(localPath) + f"__{count}")
                    async with session.post(url=url, params=params, data=data) as response:
                        result = await response.text()
                        result = json.loads(result)
                        params["partseq"] += 1
                        count += 1
    # 创建文件

    url = f"https://pan.baidu.com/rest/2.0/xpan/file?method=create&access_token={token}"
    params = {"path": panPath, "size": str(os.stat(localPath).st_size), "isdir": "0", "block_list": json.dumps(block_list), "uploadid": uploadid,
              "rtype": rtype}
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=params) as response:
            result = await response.json()
            return result


async def _uploadFile_singleStep(QQ: int, localPath: str, panPath: str, ondup: str = "fail", matcher: Matcher = None) -> dict[str, any] | None:
    """
    网盘文件单步上传。若不成功返回None，否则返回分片请求结果。

    :param QQ: 用户QQ号
    :param matcher: 事件matcher
    :param localPath: 本地文件地址
    :param panPath: 网盘目录地址，请以"/"开头
    :param ondup: 覆盖方式："fail":重名时返回失败，"overwrite":重名时覆盖，"newcopy":重名时重新命名

    返回字典参数：\n
    path	string	文件的绝对路径\n
    size	uint64	文件大小，单位B\n
    ctime	uint64	文件创建时间\n
    mtime	uint64	文件修改时间\n
    md5	string	文件的MD5，只有提交文件时才返回，提交目录时没有该值\n
    fs_id	uint64	文件在云端的唯一标识ID\n
    request_id	string	请求标识\n

    返回示例
    {"ctime": 1691048365, "fs_id": 946375630980861, "md5": "1b6982181p91ea8340d1daa95ac60e9d", "mtime": 1691048365, "path": "/apps/AppName/filename.jpg",
    "request_id": 4978394455905006592, "size": 6656}
    """
    # 判断文件是否存在
    if not os.path.isfile(localPath):
        return None
    token = await getToken(QQ, matcher)
    if token is None:
        return None
    # 处理地址
    url = f"https://d.pcs.baidu.com/rest/2.0/pcs/file"
    panPath = os.path.join(panPath, os.path.basename(localPath)).replace("\\", "/")
    params = {"method": "upload", "access_token": token, "path": panPath, "ondup": ondup}
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field("file",
                       open(file=localPath, mode="rb"),
                       filename=os.path.basename(localPath))
        async with session.post(url=url, data=data, params=params) as response:
            try:
                result = await response.text()
                result = json.loads(result)
            except json.JSONDecodeError:
                return None
            return result


async def deleteFile(QQ: int, pathList: str | list[str], matcher: Matcher = None) -> int:
    """
    操作网盘指定路径文件。根据操作结果返回值。

    :param QQ: 用户QQ号
    :param matcher: 事件matcher
    :param pathList: 文件路径列表
    :return: -1：获取token失败、-9：文件不存在、111：有其他异步任务在执行、-7：文件名非法、0：操作成功
    """
    token = await getToken(QQ, matcher)
    if token is None:
        return -1
    if isinstance(pathList, str):
        pathList = str([pathList])
    else:
        pathList = str(pathList)
    url = f"https://pan.baidu.com/rest/2.0/xpan/file"
    params = {"method": "filemanager", "access_token": token, "opera": "delete", "async": 0, "filelist": pathList}
    async with aiohttp.ClientSession() as session:
        # 设置默认超时时长为60s
        async with session.get(url=url, params=params, timeout=60) as response:
            result = await response.json()
            # print(result)
            return result["errno"]


async def _getBlockList(path: str, chunkSize: int) -> (list[str], str):
    """
    计算文件分片MD5串与整体md5

    :param path: 文件路径
    :param chunkSize: 分片大小，可以为4，8，16，32。普通用户=4，普通会员=16，超级会员=32
    :return: MD5串，失败返回None
    """
    result = []
    if chunkSize not in {4, 8, 16, 32}:
        return None
    chunkRead = chunkSize * 1024 * 1024
    if not os.path.isfile(path):
        return None
    async with aiofiles.open(file=path, mode="rb") as file:
        total_md5 = hashlib.md5()
        while True:
            md5 = hashlib.md5()
            chunk = await file.read(chunkRead)
            if not chunk:
                break
            md5.update(chunk)
            total_md5.update(chunk)
            result.append(md5.hexdigest())
    return result, total_md5.hexdigest()


async def _getSliceMD5(path: str) -> str | None:
    """获取文件校验段MD5"""
    if not os.path.isfile(path):
        return None
    async with aiofiles.open(file=path, mode="rb") as file:
        md5 = hashlib.md5()
        while True:
            chunk = await file.read(256 * 10024)
            if not chunk:
                break
            md5.update(chunk)
            return md5.hexdigest()


if __name__ == '__main__':
    asyncio.run(uploadFile(QQ=654163754,
                           localPath="E:/Projects/Hiyori/Hiyori/Data/GroupFile_Backup/不区分用户名/905080027/7月tailwindui.zip",
                           panPath="apps/Hiyori/uploadTest",
                           ondup="fail"))
