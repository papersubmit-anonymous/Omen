import os
import re
import subprocess
import time
import frida
import sys

class HookMethod:
    def __int__(self):
        self.method_signature = ""
        self.method_offset = ""
        self.module_name = ""
    def info(self):
        print("[+]Hook Method")
        print("- Method Signature : ", self.method_signature)
        print("- Method Offset : ", self.method_offset)
        print("- Module Name : ", self.module_name)
    def log(self, app):
        logPath = os.path.join(app.workDir, "HookMethods.txt")
        with open(logPath, "a") as f:
            f.writelines("========== Method ==========\n")
            if self.method_signature != "":
                f.writelines("- method_signature : " + self.method_signature + "\n")
            if self.method_offset != "":
                f.writelines("- method_offset : " + self.method_offset + "\n")
            if self.module_name != "":
                f.writelines("- module_name : " + self.module_name + "\n")

hookMethods = []

def on_message(message, data):
    global hookMethods
    if message['type'] == 'send':
        payload = message['payload']
        if payload['type'] == 'dymaic_method_with_model':
            flag = True
            for method in hookMethods:
                if method.method_signature == payload['method_signature'] and method.module_name == payload['module_name']:
                    flag = False
                    break
            if flag:
                newMethod = HookMethod()
                newMethod.method_signature = payload['method_signature']
                newMethod.method_offset = payload['method_offset']
                newMethod.module_name = payload['module_name']
                hookMethods.append(newMethod)
        else:
            print("test")
    else:
        print(message)

def hookScan(appobj, timeout=10):
    global hookMethods
    processName = appobj.processName
    packageName = appobj.packageName
    # 测量方法的执行时间
    start_time = time.perf_counter()
    device = frida.get_usb_device()
    pid = device.spawn([packageName])
    session = device.attach(pid)
    with open("./CNFA/hookScan.js", encoding='utf-8') as f:
        script = session.create_script(f.read())
    script.on('message', on_message)
    script.load()
    script.exports_sync.start()  # 调用 start() 函数
    time.sleep(2)  # 等待30秒
    device.resume(pid)  # 将此行移到script.load()之前
    time.sleep(timeout)  # 等待30秒
    session.detach()  # 停止脚本
    end_time = time.perf_counter()
    # 计算方法的执行时间
    duration = end_time - start_time - timeout - 2
    appobj.dymaictime = appobj.dymaictime + duration
    return hookMethods
