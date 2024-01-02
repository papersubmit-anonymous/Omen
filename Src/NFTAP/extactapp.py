import os.path
import pickle
import shutil
import subprocess

import psutil
from NFTAP.weight import weightCalculation
from concurrent.futures import ProcessPoolExecutor
totalnumpath = "num.txt"
wordir = "..\workDirs"
appdir = "..\\apks"
tagetapks = "..\\targetapk"
dicts = {}
def buildict(apk_file):
        try:
            apk_path = os.path.join(appdir, apk_file)
            print(apk_path)
            # 使用aapt获取包名
            cmd = f'aapt dump badging {apk_path} | findstr "package: name"'
            output = subprocess.check_output(cmd, shell=True).decode('utf-8')
            # 解析包名
            package_name = output.split(" ")[1].split("=")[1].strip("'")
            dicts[package_name] = apk_path
        except:
            pass
def assessment(sub_folder):
    pkgname = sub_folder.replace('_', '.')
    # 查找当前目录下所有的apk文件
    if pkgname in dicts:
        print("get apk: " + pkgname)
        shutil.copy(dicts[pkgname], tagetapks)


if __name__ == '__main__':
    apk_files = [f for f in os.listdir(appdir) if f.endswith(".apk")]
    # 获取真实CPU核心数
    true_cpu_cores = psutil.cpu_count(logical=False)
    # 创建进程池
    with ProcessPoolExecutor(max_workers=true_cpu_cores) as executor:
        for apk_file in apk_files:
            buildict(apk_file)
    # 遍历目录下的所有文件夹
    # 获取目录下所有子文件和文件夹
    if not os.path.exists(tagetapks):
        os.mkdir(tagetapks)
    sub_items = os.listdir(wordir)
    # 过滤出所有的文件夹名字
    sub_folders = [sub_item for sub_item in sub_items if os.path.isdir(os.path.join(wordir, sub_item))]
    # 获取真实CPU核心数
    true_cpu_cores = psutil.cpu_count(logical=False)
    # 创建进程池
    with ProcessPoolExecutor(max_workers=true_cpu_cores) as executor:
        # 处理所有的文件夹
        for sub_folder in sub_folders:
            # 处理子文件夹
            print(sub_folder)
            assessment(sub_folder)