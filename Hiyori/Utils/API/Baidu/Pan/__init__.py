"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/8/23-14:43
@Desc: 百度网盘云服务
@Ver : 1.0.0
"""
from Hiyori.Utils.API.Baidu import baidu
import asyncio
import aiohttp
import urllib.parse
import os
import aiofiles
import time


async def getToken() -> int | None:
    status = await baidu.Api.Pan.openapi_Refresh_Access_Token()
    if status == 1:
        baidu.dumps()
    elif status == -1:
        return None
    return baidu.Api.Pan.access_token


async def userInfo() -> dict[str, any] | None:
    """
    获取当前用户信息，若不成功返回None

    返回说明\n
    baidu_name	string	百度账号\n
    netdisk_name	string	网盘账号\n
    avatar_url	string	头像地址\n
    vip_type	int	会员类型，0普通用户、1普通会员、2超级会员\n
    uk	int	用户ID
    """
    token = await getToken()
    if token is None:
        return None
    token = baidu.Api.Pan.access_token
    url = f"https://pan.baidu.com/rest/2.0/xpan/nas?access_token={token}&method=uinfo"
    # 发送请求
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            result = await response.json()
            print(result)
            return result


async def diskInfo() -> dict[str, any] | None:
    """
    获取用户当前网盘信息，若不成功返回None

    返回说明\n
    total	int	总空间大小，单位B\n
    expire	bool	7天内是否有容量到期\n
    used	int	已使用大小，单位B\n
    free	int	免费容量，单位B
    """
    token = await getToken()
    if token is None:
        return None
    url = f"https://pan.baidu.com/api/quota?access_token={token}&checkfree=1&checkexpire=1"
    # 发送请求
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            result = await response.json()
            print(result)
            return result


async def fileInfoByFids(fids: int | list[int], dlink: int = 1, thumb: int = 1, extra: int = 1, needmedia: int = 1) -> list[dict[str, any]] | None:
    """
    根据文件的id查询文件信息，上限100个。

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
    token = await getToken()
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


async def fileInfo(path: str, dlink: int = 1, thumb: int = 1, extra: int = 1, needmedia: int = 1) -> dict[str, any] | None:
    """
    文件信息查询，若未查询到结果返回None，否则返回对应信息
    :param path: 文件路径
    :param dlink: 是否需要下载地址, 0为否，1为是
    :param thumb: 是否需要缩略图地址，0为否，1为是
    :param extra: 图片是否需要拍摄时间，原图分辨率等其他信息，0为否，1为是
    :param needmedia: 视频是否需要展示时长信息，单位为秒，0为否，1为是

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
    dirPath = os.path.dirname(path)  # 路径名
    fileName = os.path.basename(path)  # 文件名
    infos = await listDir(path=dirPath)
    if infos is not None:
        for info in infos:
            if info["server_filename"] == fileName:
                fid = info["fs_id"]
                info = await fileInfoByFids(fids=fid, dlink=dlink, thumb=thumb, extra=extra, needmedia=needmedia)
                if info is None:
                    return None
                else:
                    return info[0]

    return None


async def listDir(path: str = "/", order: str = "name", desc: int = 1, start: int = 0, limit: int = 100,
                  web: int = 1, folder: int = 0, showempty: int = 1) -> list[dict[str, any]] | None:
    """
    获取文件列表

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
    token = await getToken()
    if token is None:
        return None
    # 处理地址
    fileDir = urllib.parse.quote(path)
    url = f"https://pan.baidu.com/rest/2.0/xpan/file?method=list" \
          f"&access_token={token}" \
          f"&dir={fileDir}" \
          f"&order={order}" \
          f"&desc={desc}" \
          f"&start={start}" \
          f"&limit={limit}" \
          f"&web={web}" \
          f"&folder={folder}" \
          f"&showempty={showempty}"
    # 发送请求
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            result = await response.json()
            # print(result)
            if result["errno"] == 0:
                return result["list"]
            else:
                return None


async def listDir_Recurse(path: str = "/", order: str = "name", desc: int = 1, start: int = 0, limit: int = 100,
                          ctime: int = None, mtime: int = None, web: int = 1) -> dict[str, any]:
    """
        递归获取文件列表，注意返回类型与listDir不同

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

    token = await getToken()
    if token is None:
        return None
    # 处理地址
    fileDir = urllib.parse.quote(path)
    url = f"https://pan.baidu.com/rest/2.0/xpan/multimedia"
    params = {"method": "listall", "access_token": token, "path": path,
              "recursion": 1, "order": order, "desc": desc, "start": start, "limit": limit}
    if ctime is not None:
        params["ctime"] = ctime
    if mtime is not None:
        params["mtime"] = mtime
        # 发送请求
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            result = await response.json()
            # print(result)
            return result


async def downloadFile(localPath: str, panPath: str) -> int:
    """
    将网盘指定目录文件下载至指定文件目录，成功返回1，失败返回0

    :param localPath: 文件路径
    :param panPath: 网盘路径
    :return:
    """
    # start = time.time_ns()
    info = await fileInfo(path=panPath)
    if info is None:
        return 0
    dLink = info["dlink"]
    token = await getToken()
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
    return 1


if __name__ == '__main__':
    # asyncio.run(getUserInfo())
    # asyncio.run(getDiskInfo())
    # asyncio.run(listDir(path="/Gal/ATRI/ATRI-my  dear moments.docx"))
    # asyncio.run(listDir_Recurse(path="/"))
    # asyncio.run(fileInfo(path="/Gal/ATRI/ATRI-my  dear moments.docx"))

    asyncio.run(
        downloadFile(localPath="C:\\Users\\65416\\Desktop\\网盘测试\\danei2.mp4", panPath="/我的资源/达内java2022年/1 FUNDAMENTAL01/06： 数组（下） 、 方法pm.mp4"))
    print(1)
