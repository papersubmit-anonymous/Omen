'''
results.append({
"package": package,
"class": class_name,
"library": library_name,
"method": method_name,
"return_type": return_type,
"param_count": param_count,
"params": params
})
{'package': 'package com.example.myapplication', 'class': 'MainActivity', 'library': 'myapplication', 'method': 'stringFromJNI', 'return_type': 'String', 'param_count': 0, 'params': []}
{'package': 'package com.example.myapplication', 'class': 'NativeLoader', 'library': 'myapplication', 'method': 'getNativeString', 'return_type': 'String', 'param_count': 0, 'params': []}
'''
import os


class Stjni:
    def __init__(self):
        self.package = ""
        self.aclass = ""
        self.library = ""
        self.method = ""
        self.return_type = ""
        self.param_count = ""
        self.static = ""
        self.params = []

    def info(self):
        print("========== Static Extractor JNI ==========")
        if self.package != "":
            print("- Package Name : ", self.package)
        if self.aclass != "":
            print("- Class Name : ", self.aclass)
        if self.library != "":
            print("- Library : ", self.library)
        if self.method != "":
            print("- Method : ", self.method)
        if self.static != "":
            print("- Static : ", self.static)
        if self.return_type != "":
            print("- Return Type : ", self.return_type)
        if self.param_count != "":
            print("- Param Count : ", self.param_count)
        if self.params != "":
            print("- Params : ", self.params)

    def log(self, app):
        logPath = os.path.join(app.workDir, "StaticExtractorJNIMethods.txt")
        with open(logPath, "a") as f:
            f.writelines("========== Method ==========\n")
            if self.package != "":
                f.writelines("- Package Name : " + self.package + "\n")
            if self.aclass != "":
                f.writelines("- Class Name : " + self.aclass + "\n")
            if self.library != "":
                f.writelines("- Library : " + self.library + "\n")
            if self.method != "":
                f.writelines("- Method : " + self.method + "\n")
            if self.static != "":
                f.writelines("- Static : " + self.static + "\n")
            if self.return_type != "":
                f.writelines("- Return Type : " + self.return_type + "\n")
            if self.param_count != "":
                f.writelines("- Param Count : " + str(self.param_count) + "\n")
            if self.params != []:
                for param in self.params:
                    f.writelines("- Params Type: " + param[0] + " Params ID: " + param[1] + "\n")
