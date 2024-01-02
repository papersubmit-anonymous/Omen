import os
import re
import subprocess
import time
import frida
import sys

class Method:
    def __int__(self, ):
        self.mtype = ""
        self.Name = ""
        self.ModuleName = ""
        self.ModuleOffset = ""

    def info(self):
        print("[+]New Method")
        print("- Method Type : ", self.mtype)
        print("- Method Name : ", self.Name)
        print("- Module Name : ", self.ModuleName)
        print("- Module Offset : ", self.ModuleOffset)

    def Jlog(self, app):
        logPath = os.path.join(app.workDir, "JNIMethod_ScanLibrary.txt")
        with open(logPath, "a") as f:
            f.writelines("========== Method ==========\n")
            if self.Name != "":
                f.writelines("Method Name : " + self.Name + "\n")
            if self.ModuleName != "":
                f.writelines("Module Name : " + self.ModuleName + "\n")
            if self.ModuleOffset != "":
                f.writelines("Module Offset : " + self.ModuleOffset + "\n")

    def Mlog(self, app):
        logPath = os.path.join(app.workDir, "Method_ScanLibrary.txt")
        with open(logPath, "a") as f:
            f.writelines("========== Method ==========\n")
            if self.Name != "":
                f.writelines("Method Name : " + self.Name + "\n")
            if self.ModuleName != "":
                f.writelines("Module Name : " + self.ModuleName + "\n")
            if self.ModuleOffset != "":
                f.writelines("Module Offset : " + self.ModuleOffset + "\n")


JNIMethods = []
Methods = []
Successful_Load = []


def on_message(message, data):
    global JNIMethods, Methods, Successful_Load
    if message['type'] == 'send':
        payload = message['payload']
        if payload['type'] == 'successLib':
            print("[+] Get Sucessfull JNIMethod")
            #if type(payload['Name']) == "str":
            print(payload['Name'])
            if payload['Name'] not in Successful_Load:
                Successful_Load.append(payload['Name'])
        elif payload['type'] == 'JNIMethod':
            print("[+] Get New JNIMethod")
            print("- JNI Method Name : ", payload['Name'])
            print("- JNI Module Name : ", payload['ModuleName'])
            print("- JNI Module Offset : ", payload['ModuleOffset'])
            flag = True
            for obj in JNIMethods:
                if obj.Name == payload['Name'] and obj.ModuleName == payload['ModuleName']:
                    flag = False
                    break
            if flag:
                newJNIMethod = Method()
                newJNIMethod.mtype = 'JNIMethod'
                newJNIMethod.Name = payload['Name']
                newJNIMethod.ModuleName = payload['ModuleName']
                newJNIMethod.ModuleOffset = payload['ModuleOffset']
                JNIMethods.append(newJNIMethod)
        elif payload['type'] == 'Method':
            print("[+] Get New Method")
            print("- Method Name : ", payload['Name'])
            print("- Module Name : ", payload['ModuleName'])
            print("- Module Offset : ", payload['ModuleOffset'])
            flag = True
            for obj in Methods:
                if obj.Name == payload['Name'] and obj.ModuleName == payload['ModuleName']:
                    flag = False
                    break
            if flag:
                newMethod = Method()
                newMethod.mtype = 'Method'
                newMethod.Name = payload['Name']
                newMethod.ModuleName = payload['ModuleName']
                newMethod.ModuleOffset = payload['ModuleOffset']
                Methods.append(newMethod)
        else:
            print("test")
    else:
        print(message)


def scanlib(app, timeout=15):
    global permissions
    packageName = app.packageName
    TargetModules = app.library
    processName = ''
    main_activity = ""
    # 执行命令并获取输出
    output = subprocess.check_output(["adb", "shell", "dumpsys", "package", packageName], encoding="utf-8")
    # 使用正则表达式匹配主Activity
    match = re.search(r"MAIN:\n\s*(.*)", output)
    # 使用正则表达式匹配主Activity
    match = re.search(r"MAIN:\n\s*(.*)", output)
    if match:
        main_activity = match.group(1)
        main_activity = main_activity.split(' ')[1].split(' ')[0]
        print(main_activity)
    adbCmd = "adb shell am start -n " + main_activity
    print("[ADB] : ", adbCmd)
    output = subprocess.run(['adb', 'shell', 'monkey', '-p', packageName, '-c', 'android.intent.category.LAUNCHER', '1'])
    print(output)
    time.sleep(1)
    # 执行命令并获取输出
    process = subprocess.Popen("frida-ps -Uai", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 逐行读取输出
    while True:
        line = process.stdout.readline()
        if not line:
            break
        tmpstr = line.strip().decode("utf-8")
        if packageName in tmpstr:
            processName = tmpstr.split('  ')[1].split('  ')[0]
            app.processName = processName
            print(processName)
    parts = packageName.split(".")
    packageName = ".".join(parts[:3])
    processName = app.processName
    # packageName = app.packageName
    print("[+] processName : ", processName)
    print("[+] packageName : ", app.packageName)
    print("[+] TargetModules : ", TargetModules)
    print("[+] app.packageName : ", app.packageName)

    # 使用 os.system() 方法执行 adb 命令
    # for permission in permissions:
    # os.system(f'adb shell pm grant {packageName} {permission}')
    # time.sleep(1)
    print("============== LoadLibrary ==============")
    # 测量方法的执行时间
    start_time = time.perf_counter()
    device = frida.get_usb_device()
    pid = device.spawn([packageName])
    session = device.attach(pid)
    # session = device.attach(processName)
    with open("CNFA/loadLib.js", encoding='utf-8') as f:
        script = session.create_script(f.read())
    time.sleep(0.5)
    script.on('message', on_message)
    script.load()
    script.exports_sync.start(TargetModules, app.packageName)  # 调用 start() 函数
    time.sleep(2)  # 等待30秒
    device.resume(pid)  # 将此行移到script.load()之前
    time.sleep(timeout)  # 等待30秒
    session.detach()  # 停止脚本

    # 计算方法的执行时间
    end_time = time.perf_counter()
    duration = end_time - start_time - 2 - timeout
    app.dymaictime = app.dymaictime + duration

    print("[+] Successful_Load : ", Successful_Load)
    print("[+] Success Load")
    if Successful_Load:
        print("============== ScanLibrary ==============")
        device = frida.get_usb_device()
        process = device.attach(processName)
        with open('CNFA/scanLibrary.js', encoding='utf-8') as f:
            jscode = f.read()
        script = process.create_script(jscode)
        script.on('message', on_message)
        script.load()
        # 测量方法的执行时间
        start_time = time.perf_counter()
        script.exports_sync.scan(Successful_Load)
        # 计算方法的执行时间
        end_time = time.perf_counter()
        duration = end_time - start_time - timeout
        app.dymaictime = app.dymaictime + duration
        try:
            while 1:
                time.sleep(0.1)
                # 获取当前时间戳，并与程序开始时间戳比较
                if time.time() - start_time > timeout:  # 30s
                    break
        except KeyboardInterrupt:
            sys.exit()



def scan(app):
    global JNIMethods, Methods
    Alllibs = app.library
    print("[+] Start Extractor Library : ", Alllibs)
    scanlib(app, timeout=15)
    time.sleep(2)
    return JNIMethods, Methods
