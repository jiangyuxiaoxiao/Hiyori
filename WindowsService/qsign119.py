"""
@Author: Kasugano Sora
@Github: https://github.com/jiangyuxiaoxiao
@Date: 2023/09/20-09:30
@Desc: Qsign1.19版本
@Ver : 1.0.0
"""
import subprocess
import locale

cmd = [".\\Cqhttp\\Qsign1.1.9\\bin\\unidbg-fetch-qsign.bat",
       "--basePath=.\\Cqhttp\\Qsign1.1.9\\txlib\\8.9.80"]


def start_process(command):
    encoding = locale.getpreferredencoding()
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, encoding=encoding)


def monitor_process(process, command):
    while True:
        # 检查进程是否还在运行
        return_code = process.poll()
        if return_code is not None:
            print(f"进程已退出，退出码为 {return_code}，正在重新启动...")
            process = start_process(command)
        else:
            # 读取进程的输出
            output = process.stdout.readline().rstrip("\n")
            print(output)


def main():
    # 定义你要执行的命令
    process = start_process(cmd)
    monitor_process(process, cmd)


if __name__ == "__main__":
    main()
