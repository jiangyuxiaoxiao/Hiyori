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


async def getToken() -> int | None:
    status = await baidu.Api.Pan.openapi_Refresh_Access_Token()
    if status == 1:
        baidu.dumps()
    elif status == -1:
        return None
    return baidu.Api.Pan.access_token


async def getUserInfo() -> dict[str, any] | None:
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


async def getDiskInfo() -> dict[str, any] | None:
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


async def listDir(path: str = "/", order: str = "name", desc: int = 1, start: int = 0, limit: int = 100,
                  web: int = 1, folder: int = 0, showempty: int = 0) -> list[dict[str, any]] | None:
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
    dir = urllib.parse.quote(path)
    url = f"https://pan.baidu.com/rest/2.0/xpan/file?method=list" \
          f"&access_token={token}" \
          f"&dir={dir}" \
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
            print(result)
            return result


if __name__ == '__main__':
    # asyncio.run(getUserInfo())
    # asyncio.run(getDiskInfo())
    asyncio.run(listDir(path="/我的资源"))
    print(1)
