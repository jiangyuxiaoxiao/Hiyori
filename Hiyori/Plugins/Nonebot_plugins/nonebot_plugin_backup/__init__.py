from nonebot import get_driver, logger, on_shell_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from collections import deque

import requests
import os
import time
from pathlib import Path


backup_group = get_driver().config.dict().get('backup_group', [])
backup_command = get_driver().config.dict().get('backup_command', "备份群文件")
backup_maxsize = get_driver().config.dict().get('backup_maxsize', 300)
backup_minsize = get_driver().config.dict().get('backup_minsize', 0.01)
backup_temp_files = get_driver().config.dict().get('backup_temp_files', True)
backup_temp_file_ignore = get_driver().config.dict().get(
    'backup_temp_file_ignore', [".gif", ".png", ".jpg", ".mp4"])


linker_parser = ArgumentParser(add_help=False)
linker = on_shell_command(backup_command, parser=linker_parser, priority=1)

recovery_command = get_driver().config.dict().get('recovery_command', "恢复群文件")
recovery_parser = ArgumentParser(add_help=False)
recovery = on_shell_command(
    recovery_command, parser=recovery_parser, priority=1)


essence_command = get_driver().config.dict().get('essence_command', "备份群精华")
essence_parser = ArgumentParser(add_help=False)
essence = on_shell_command(
    essence_command, parser=essence_parser, priority=1)


class EventInfo:
    fdindex = -1
    fsuccess = fjump = fsizes = 0
    fdtoolarge = []
    fbroken = []
    fdnames = []

    def __init__(self) -> None:
        ...

    def init(self) -> None:
        self.fdindex = -1
        self.fsuccess = self.fjump = self.fsizes = 0
        self.fdtoolarge = []
        self.fbroken = []
        self.fdnames = []


async def SaveToDisk(bot, ff, fdpath, EIF, gid):
    fname = ff["file_name"]
    fid = ff["file_id"]
    fbusid = ff["busid"]
    fsize = ff["file_size"]
    fpath = Path(fdpath, fname)

    if fsize/1024/1024 < backup_minsize:
        return

    if fsize/1024/1024 > backup_maxsize:
        EIF.fdtoolarge.append(
            EIF.fdnames[EI.fdindex] + "/" + fname)
        return

    if not Path(fpath).exists():
        try:

            finfo = await bot.get_group_file_url(group_id=gid, file_id=str(fid), bus_id=int(fbusid))
            url = finfo['url']
            req = requests.get(url)

            if not Path(fdpath).exists():
                os.makedirs(fdpath)
            with open(fpath, 'wb') as mfile:
                mfile.write(req.content)
            EIF.fsizes += fsize
            EIF.fsuccess += 1
        except Exception as e:
            EIF.fbroken.append(fdpath + "/" + fname)
            print(e)
            logger.debug("文件获取不到/已损坏:" + fdpath + "/" + fname)
    else:
        EIF.fsizes += Path(fpath).stat().st_size
        EIF.fjump += 1


async def createFolder(bot, root_dir, gid):
    root = await bot.get_group_root_files(group_id=gid)
    folders = root.get("folders")
    fdnames = []
    fdnames.extend([i["folder_name"] for i in folders])

    for parent, dirs, files in os.walk(root_dir):
        if dirs:
            for fd_name in dirs:
                if fd_name not in fdnames:
                    print(fd_name)
                    await bot.create_group_file_folder(
                        group_id=gid, name=fd_name, parent_i="/")


async def upload_files(bot, gid, folder_id, root_dir):
    group_root = await bot.get_group_files_by_folder(group_id=gid, folder_id=folder_id)
    files = group_root.get("files")
    filenames = []
    if files:
        filenames = [ff["file_name"] for ff in files]
    if os.path.exists(root_dir):
        for entry in os.scandir(root_dir):
            if entry.is_file() and entry.name not in filenames:
                absolute_path = Path(root_dir).resolve().joinpath(entry.name)

                await bot.upload_group_file(
                    group_id=gid, file=str(absolute_path), name=entry.name, folder=folder_id)

EI = EventInfo()


@essence.handle()
async def essen(bot: Bot, event: GroupMessageEvent, state: T_State):
    gid = event.group_id

    args = vars(state.get("_args"))
    logger.debug(args)

    messages = []
    essen_list = await bot.get_essence_msg_list(group_id=gid)
    for es in essen_list:
        print("------------")
        print(es["sender_nick"])
        print(es["message_id"])
        print(es["sender_time"])
        message_id = es["message_id"]
        # try:
        msg = await bot.get_msg(message_id=message_id)
        print(msg["message"])
        node = {
            "type": "node",
            "data": {
                "name": "精华收集者",
                "uin": "10086",
                "content": msg["message"]
            }}
        messages.append(node)
        # except Exception as e:
        #     print(e)
    await bot.send_group_forward_msg(group_id=491207941, messages=messages)

    await essence.finish("备份完成")


@recovery.handle()
async def recover(bot: Bot, event: GroupMessageEvent, state: T_State):
    EI.init()
    gid = event.group_id
    if str(gid) in backup_group or backup_group == []:
        args = vars(state.get("_args"))
        logger.debug(args)

        await bot.send(event, "恢复中,请稍后(需要管理员权限)")
        # tstart = time.time()
        root_dir = "./qqgroup/" + str(gid)

        # 创建群文件夹
        await createFolder(bot, root_dir, gid)

        # 上传文件

        root = await bot.get_group_root_files(group_id=gid)
        folders = root.get("folders")
        # fdpath = "./qqgroup/" + str(event.group_id)

        await upload_files(bot, gid, "/", root_dir)

        # 广度优先搜索
        dq = deque()

        if folders:
            dq.extend([i["folder_id"] for i in folders])
            EI.fdnames.extend([i["folder_name"] for i in folders])

        while dq:
            EI.fdindex += 1
            _ = dq.popleft()
            logger.debug("下一个搜索的文件夹：" + _)
            root = await bot.get_group_files_by_folder(group_id=gid, folder_id=_)

            await upload_files(bot, gid, _, root_dir + "/" + EI.fdnames[EI.fdindex])

        await recovery.finish("恢复完成")


@linker.handle()
async def link(bot: Bot, event: GroupMessageEvent, state: T_State):
    EI.init()
    gid = event.group_id
    if str(gid) in backup_group or backup_group == []:
        args = vars(state.get("_args"))
        logger.debug(args)

        await bot.send(event, "备份中,请稍后…")
        tstart = time.time()
        root = await bot.get_group_root_files(group_id=gid)
        folders = root.get("folders")
        if backup_temp_files:
            files = root.get("files")
            fdpath = "./Data/GroupFileBackUp/" + str(event.group_id)
            if files:
                for ff in files:
                    suf = Path(ff["file_name"]).suffix
                    userName = ff["uploader_name"]
                    if suf in backup_temp_file_ignore:
                        continue

                    await SaveToDisk(bot, ff, fdpath + "/" + str(userName), EI, gid)

        # 广度优先搜索
        dq = deque()

        if folders:
            dq.extend([i["folder_id"] for i in folders])
            EI.fdnames.extend([i["folder_name"] for i in folders])

        while dq:
            EI.fdindex += 1
            _ = dq.popleft()
            logger.debug("下一个搜索的文件夹：" + _)
            root = await bot.get_group_files_by_folder(group_id=gid, folder_id=_)

            fdpath = "./Data/GroupFileBackUp/" + \
                str(gid) + "/" + EI.fdnames[EI.fdindex]

            file = root.get("files")

            if file:
                for ff in file:
                    userName = ff["uploader_name"]
                    await SaveToDisk(bot, ff, fdpath + "/" + str(userName), EI, gid)

        if len(EI.fdtoolarge) == 0:
            EI.fdtoolarge = "无"
        else:
            EI.fdtoolarge = "\n".join(EI.fdtoolarge)

        if len(EI.fbroken) == 0:
            EI.fbroken = ""
        else:
            EI.fbroken = "检测到损坏文件:" + '\n'.join(EI.fbroken)

        EI.fsizes = round(EI.fsizes/1024/1024, 2)
        tsum = round(time.time()-tstart, 2)

        await linker.finish("此次备份耗时%2d秒; 共备份%d个文件,跳过已备份%d个文件, 累计备份大小%.2f M,\n未备份大文件列表(>%dm):\n%s\n%s" % (tsum, EI.fsuccess, EI.fjump, EI.fsizes, backup_maxsize, EI.fdtoolarge, EI.fbroken))
