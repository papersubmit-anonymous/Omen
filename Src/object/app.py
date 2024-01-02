import os


class App:
    def __init__(self, packageName, apkPath, workDir):
        self.workDir = workDir
        self.packageName = packageName
        self.apkPath = apkPath
        self.processName = ""
        self.JNIMethods = []
        self.library = []
        self.rebuild = True
        # Time
        self.totaltime = 0
        self.statictime = 0
        self.dymaictime = 0
        self.filesize = "0"
        #
        pklpath = os.path.join(self.workDir, "methodpkl")
        if not os.path.exists(pklpath):
            os.makedirs(pklpath)
        autoMethodpath = os.path.join(self.workDir, "autoMethod")
        if not os.path.exists(autoMethodpath):
            os.makedirs(autoMethodpath)
        # JNIMethod_ScanLibrary.txt
        logPath = os.path.join(self.workDir, "StaticExtractorJNIMethods.txt")
        with open(logPath, "w") as f:
            pass
        logPath = os.path.join(self.workDir, "JNIMethod_ScanLibrary.txt")
        with open(logPath, "w") as f:
            pass
        logPath = os.path.join(self.workDir, "Method_ScanLibrary.txt")
        with open(logPath, "w") as f:
            pass
        logPath = os.path.join(self.workDir, "SourceJNIMethods.txt")
        with open(logPath, "w") as f:
            pass
        logPath = os.path.join(self.workDir, "NoneJniNativeMethods.txt")
        with open(logPath, "w") as f:
            pass
        logPath = os.path.join(self.workDir, "HookMethods.txt")
        with open(logPath, "w") as f:
            pass
        logPath = os.path.join(self.workDir, "AutoMethods.txt")
        with open(logPath, "w") as f:
            pass

    def info(self):
        if self.packageName != "":
            print("[+] APP Package Name : ", self.packageName)
        if self.apkPath != "":
            print("- APK Path : ", self.apkPath)
        if self.processName != "":
            print("- APP Process Name : ", self.processName)
        if self.JNIMethods:
            for jni in self.JNIMethods:
                jni.info()  # jni class info method

    def writetime(self):
        timepath = os.path.join(self.workDir, "time.txt")
        with open(timepath, "w") as f:
            f.writelines("size: " + self.filesize + "\n")
            self.totaltime = self.statictime + self.dymaictime
            totaltime = "{:.2f}".format(self.totaltime)
            statictime = "{:.2f}".format(self.statictime)
            dymaictime = "{:.2f}".format(self.dymaictime)
            print("totle: " + totaltime)
            print("static: " + statictime)
            print("dymaic: " + dymaictime)
            f.writelines("totle: " + totaltime + "\n")
            f.writelines("static: " + statictime + "\n")
            f.writelines("dymaic: " + dymaictime + "\n")