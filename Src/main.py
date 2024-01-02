import os
import subprocess
import time
import argparse
from CNFA.cnfa import cfnaScan
from object.app import App

workDirs = "workDirs"
apk_dir = "apks"
platform = "Windows"  # Windows or Linux
extractorJarPath = os.path.join('CNFA', 'Extractor.jar')
appList = []
installargs = False
abiargs = "x86_64"
rebuild = True

def jadxUpack(apk_path, workdir):
    # 使用aapt获取包名
    if platform == "Windows":
        cmd = f'jadx {apk_path} -d {workdir}'
    else:
        cmd = f'jadx {apk_path} -d {workdir}'
    subprocess.run(cmd, shell=True)


def nonEmptyLine(workdir):
    # 定义输入文件和输出文件
    input_file = os.path.join(workdir, "log.txt")
    output_file = os.path.join(workdir, "StaticExtractor.txt")
    # 读取文件内容
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # 移除空行
    non_empty_lines = [line for line in lines if line.strip()]
    # 将非空行写入新文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(non_empty_lines)


def extraLib(libpath):
    libs = []
    if os.path.exists(libpath):
        for root, dirs, files in os.walk(libpath):
            for file in files:
                libs.append(file)
                # print(os.path.join(root, file))
    return libs


def run_adb_command(command):
    # print(["adb"] + command)
    process = subprocess.Popen(["adb"] + command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode("utf-8").strip(), stderr.decode("utf-8").strip()

def is_app_installed(package_name):
    try:
        output = subprocess.check_output(["adb", "shell", "pm", "list", "packages", package_name])
        if package_name in output.decode("utf-8"):
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        print("Error: {}".format(e))
        return False


def initapk(apk_file):
    global appList, installargs, abiargs, rebuild
    apk_path = os.path.join(apk_dir, apk_file)
    print(apk_path)
    stdout, stderr = run_adb_command(["devices"])
    print(stdout)
    time.sleep(0.5)
    stdout, stderr = run_adb_command(["root"])
    print(stdout)
    time.sleep(0.5)
    # 使用aapt获取包名
    if platform == "Windows":
        cmd = f'aapt dump badging {apk_path} | findstr "package: name"'
    else:
        cmd = f'aapt dump badging {apk_path} | grep "package: name"'
    output = subprocess.check_output(cmd, shell=True).decode('utf-8')
    # 解析包名
    package_name = output.split(" ")[1].split("=")[1].strip("'")
    # 可选安装
    if is_app_installed(package_name):
        print("App is already installed.")
    else:
        print("App is not installed. Installing now...")
        if installargs:
            stdout, stderr = run_adb_command(["install", apk_path])
            print(stdout)
            time.sleep(1)
    print(f"APK file: {apk_file}, Package name: {package_name}")
    # build App Object
    workdir = os.path.join(workDirs, package_name.replace(".", "_"))
    if not os.path.exists(workdir):
        os.mkdir(workdir)
        print("[+] Build New Dir: ", workdir)
    newApp = App(package_name, apk_path, workdir)
    newApp.rebuild = rebuild
    if rebuild:
        jadxUpack(apk_path, workdir)
    else:
        pass
    newApp.info()
    # 获取文件大小（以千字节为单位）
    filesize = "{:.2f}".format(os.stat(apk_path).st_size / 1024)
    newApp.filesize = filesize
    libPath = os.path.join(workdir, "resources", "lib")
    TargetPath = ""
    if os.path.exists(libPath):
        if abiargs == "arm64-v8a":
            TargetPath = os.path.join(libPath, "arm64-v8a")
        elif abiargs == "armeabi-v7a":
            TargetPath = os.path.join(libPath, "armeabi-v7a")
        elif abiargs == "x86":
            TargetPath = os.path.join(libPath, "x86")
        elif abiargs == "x86_64":
            TargetPath = os.path.join(libPath, "x86_64")
        else:
            print("[-] ERROR: Can't not Find Library! ")
            return
    # 分析程序包含的Lib库
    Alllibs = []
    libs = extraLib(TargetPath)
    for lib in libs:
        if lib not in Alllibs:
            Alllibs.append(lib)
    print("[+] Extractor All Library: ", Alllibs)
    newApp.library = Alllibs
    appList.append(newApp)

#  python .\main.py -i ".\apks\" -o ".\workDirs\" -p "Windows" -a "x86_64" -r -s
if __name__ == '__main__':
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="FANM：Fuzz Android Native Method")
    parser.add_argument('-i', '--input', type=str, help="The folder where the APK is stored")
    parser.add_argument('-o', '--out', type=str, help="Output Folder")
    parser.add_argument('-s', '--install', action='store_true', help="Whether to install APP")
    parser.add_argument('-p', '--platform', type=str, help="Running platform, e.g. Windows or Linux, default Windows")
    parser.add_argument('-a', '--abi', type=str,
                        help="ABI type used by Android APP, e.g. arm64-v8a, armeabi-v7a, x86, x86_64, default x86_64")
    parser.add_argument('-r', '--rebuild', action='store_true', help="Is it necessary to start all over again")
    args = parser.parse_args()
    # 打印配置信息
    print(f"=================== START FANM ===================")
    print(f"[+] --in : {args.input}")
    apk_dir = args.input
    print(f"[+] --out : {args.out}")
    workDirs = args.out
    print(f"[+] --platform : {args.platform}")
    platform = args.platform
    print(f"[+] --abi : {args.abi}")
    abiargs = args.abi
    if args.install:
        installargs = True
        print(f"[+] --install : True")
    else:
        print(f"[+] --install : False")
    if args.rebuild:
        rebuild = True
        print(f"[+] --rebuild : True")
    else:
        rebuild = False
        print(f"[+] --rebuild : False")
    # 查找当前目录下所有的apk文件
    apk_files = [f for f in os.listdir(apk_dir) if f.endswith(".apk")]
    # 初始化APP
    for apk_file in apk_files:
        try:
            initapk(apk_file)
        except:
            pass
    # 开始信息提取
    for app in appList:
        start_time = time.perf_counter()
        try:
            # 扫描方法
            Methods = cfnaScan(app)
            end_time = time.perf_counter()
            # 计算方法的执行时间
            duration = end_time - start_time
            # 将执行时间保存为字符串
            duration_str = "{:.2f}".format(duration)
            app.totaltime = duration_str
        except:
            pass
    for app in appList:
        app.writetime()

    '''
    # Find JNI Methods
    for app in appList:
        find(app)
        break
    '''
