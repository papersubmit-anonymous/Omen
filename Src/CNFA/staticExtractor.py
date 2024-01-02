import os.path
import re
from object.stjni import Stjni
def parseExtractor(workdir):
    methodobjs = []
    # workdir = "D:\PythonProject\DeedPool\workDirs\com_example_myapplication"
    filepath = os.path.join(workdir, "StaticExtractor.txt")
    Stjnis = []
    with open(filepath, 'r', encoding='utf-8') as file:
        # 逐行读取文件
        tmpStjnis = []
        PackageName = ""
        Static = ""
        ClassName = ""
        MethodName = ""
        ReturnType = ""
        Parameters = []
        ParameterCount = 0
        LibraryName = ""
        PackFlag = False
        classFlag = False
        methodFlag = False
        libraryFlag = False
        for line in file:
            line = line.strip()
            # 处理每一行（例如，打印到控制台）
            # print(line.strip())  # 使用strip()方法去除行尾的换行符
            if line == "@@@@@@@@@@@@[+]New Package@@@@@@@@@@@@":
                PackFlag = True
            if "Package Name: " in line and PackFlag:
                PackageName = line.split("Package Name: ")[1]
            if line == "=====[+]New Class=====":
                classFlag = True
            if "Class Name: " in line and classFlag:
                ClassName = line.split("Class Name: ")[1]
            if line == "$$$$$[+]New Method$$$$$":
                methodFlag = True
            if "Found native method: " in line and methodFlag:
                MethodName = line.split("Found native method: ")[1]
            if "Is static: " in line and methodFlag:
                print(line)
                Static = line.split("Is static: ")[1]
                print(Static)
            if "Return type: " in line and methodFlag:
                ReturnType = line.split("Return type: ")[1]
            if "Parameter count: " in line and methodFlag:
                ParameterCount = int(line.split("Parameter count: ")[1])
            if "Parameter type: " in line and methodFlag:
                ParameterType = line.split("Parameter type: ")[1].split(", Parameter name:")[0]
                ParameterName = line.split("Parameter name: ")[1]
                Parameter = [ParameterType, ParameterName]
                Parameters.append(Parameter)
            if "$$$$$$$$$$$$$$$$" in line:
                methodFlag = False
                tmpstjni = Stjni()
                tmpstjni.package = PackageName
                tmpstjni.aclass = ClassName
                tmpstjni.method = MethodName
                tmpstjni.return_type = ReturnType
                tmpstjni.param_count = ParameterCount
                tmpstjni.params = Parameters
                tmpstjni.static = Static
                tmpStjnis.append(tmpstjni)
                MethodName = ""
                ReturnType = ""
                Static = ""
                ParameterCount = 0
                Parameters = []
            if "****[+] New Library****" in line:
                libraryFlag = True
            if "Found System.loadLibrary call: " in line and libraryFlag:
                LibraryName = line.split("Found System.loadLibrary call: System.loadLibrary(\"")[1].split("\")")[0]
            if line == "********":
                libraryFlag = False
            if line == "===============":
                classFlag = False
                for tmpStjni in tmpStjnis:
                    tmpStjni.library = LibraryName
                    Stjnis.append(tmpStjni)
                LibraryName = ""
                ClassName = ""
                tmpStjnis = []
            if line == "@@@@@@@@@@@@@@@@@@@@@@@@":
                PackFlag = False
                PackageName = ""
    for jni in Stjnis:
        jni.info()
    return Stjnis

'''
if __name__ == '__main__':
    parseExtractor("123")


    def __init__(self):
        self.package = ""
        self.aclass = ""
        self.library = ""
        self.method = ""
        self.return_type = ""
        self.param_count = ""
        self.params = []
'''
