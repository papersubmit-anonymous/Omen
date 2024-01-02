import subprocess
import time
from multiprocessing import Process

'''
adb devices
adb root
adb push ./frida-server-16.0.11-android-x86_64 /data/local/tmp/frida-server
adb shell chmod 755 /data/local/tmp/frida-server
adb shell "/data/local/tmp/frida-server &"
frida-ps -U
'''

platform = "x86_64"  # arm64 or x86_64


def run_adb_command(command):
    # print(["adb"] + command)
    process = subprocess.Popen(["adb"] + command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()
    return stdout.decode("utf-8").strip(), stderr.decode("utf-8").strip()


def initFrida():
    stdout, stderr = run_adb_command(["devices"])
    print(stdout)
    time.sleep(0.5)
    stdout, stderr = run_adb_command(["root"])
    print(stdout)
    time.sleep(0.5)
    stdout, stderr = run_adb_command(["devices"])
    print(stdout)
    time.sleep(1)
    if platform == "x86_64":
        # stdout, stderr = run_adb_command(
        # ["push", "./Frida/frida-server-14.2.18-android-x86_64", "/data/local/tmp/frida-server"])
        stdout, stderr = run_adb_command(
            ["push", "./Frida/frida-server-16.0.11-android-x86_64", "/data/local/tmp/frida-server"])
    else:
        stdout, stderr = run_adb_command(
            ["push", "./Frida/frida-server-16.0.11-android-arm64", "/data/local/tmp/frida-server"])
    print(stdout)
    time.sleep(2)
    stdout, stderr = run_adb_command(["shell", "chmod", "755", "/data/local/tmp/frida-server"])
    print(stdout)
    time.sleep(0.5)
    # stdout, stderr = run_adb_command(["shell", "'nohup /data/local/tmp/frida-server &'"])
    command = 'adb shell "nohup /data/local/tmp/frida-server &"'
    subprocess.run(command, shell=True)
    # print(stdout)
    # time.sleep(0.5)


def monitor_frida_server():
    while True:
        # 检查frida-server是否正在运行
        stdout, stderr = run_adb_command(["shell", "pgrep", "-f", "frida-server"])
        frida_server_pid = stdout

        if frida_server_pid:
            print(f"frida-server is running with PID: {frida_server_pid}")
        else:
            print("frida-server is not running, starting...")
            time.sleep(0.5)
            stdout, stderr = run_adb_command(["devices"])
            print(stdout)
            time.sleep(0.5)
            # run_adb_command(["shell", "'nohup /data/local/tmp/frida-server &'"])
            command = 'adb shell "nohup /data/local/tmp/frida-server &"'
            subprocess.run(command, shell=True)
        # 等待一段时间后再次检查frida-server的状态
        time.sleep(10)


if __name__ == '__main__':
    # 启动 initFrida 进程
    init_frida_process = Process(target=initFrida)
    init_frida_process.start()
    time.sleep(15)

    # 启动 monitor_frida_server 进程
    monitor_frida_process = Process(target=monitor_frida_server)
    monitor_frida_process.start()
