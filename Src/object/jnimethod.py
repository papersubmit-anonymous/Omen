import os


class JNIMethod:
    def __init__(self):
        self.PackageName = ""
        self.ClassName = ""
        self.Library = ""
        self.Method = ""
        self.ReturnType = ""
        self.ParamCount = ""
        self.Params = []
        self.MethodName = ""
        self.ModuleName = ""
        self.ModuleOffset = ""
        self.signature = ""
        self.type = ""
        self.Static = ""
        self.weight = 0

    def info(self):
        print("========== Method ==========")
        if self.type != "":
            print("- type : ", self.type)
        if self.PackageName != "":
            print("Method Package Name : ", self.PackageName)
        if self.ClassName != "":
            print("- Class Name : ", self.ClassName)
        if self.Library != "":
            print("- Method Library : ", self.Library)
        if self.Method != "":
            print("- Method Name : ", self.Method)
        if self.Static != "":
            print("- Static : ", self.Static)
        if self.ReturnType != "":
            print("- Return Type : ", self.ReturnType)
        if self.ParamCount != "":
            print("- Param Count : ", self.ParamCount)
        if self.Params != "":
            print("- Params : ", self.Params)
        if self.MethodName != "":
            print("- Method(.so) Name : ", self.MethodName)
        if self.ModuleName != "":
            print("- Module(.so) Name : ", self.ModuleName)
        if self.ModuleOffset != "":
            print("- Module(.so) Offset : ", self.ModuleOffset)
        if self.signature != "":
            print("- signature(.so) : ", self.signature)

    def log(self, app):
        logPath = os.path.join(app.workDir, "SourceJNIMethods.txt")
        with open(logPath, "a") as f:
            f.writelines("========== Method ==========\n")
            if self.type != "":
                f.writelines("- type : " + self.type + "\n")
            if self.PackageName != "":
                f.writelines("Method Package Name : " + self.PackageName + "\n")
            if self.ClassName != "":
                f.writelines("- Class Name : " + self.ClassName + "\n")
            if self.Library != "":
                f.writelines("- Method Library : " + self.Library + "\n")
            if self.Method != "":
                f.writelines("- Method Name : " + self.Method + "\n")
            if self.Static != "":
                f.writelines("- Static : " + self.Static + "\n")
            if self.ReturnType != "":
                f.writelines("- Return Type : " + self.ReturnType + "\n")
            if self.ParamCount != "":
                f.writelines("- Param Count : " + str(self.ParamCount) + "\n")
            if self.Params:
                for param in self.Params:
                    f.writelines("- Params Type: " + param[0] + " Params ID: " + param[1] + "\n")
            if self.MethodName != "":
                f.writelines("- Method(.so) Name : " + self.MethodName + "\n")
            if self.ModuleName != "":
                f.writelines("- Module(.so) Name : " + self.ModuleName + "\n")
            if self.ModuleOffset != "":
                f.writelines("- Module(.so) Offset : " + self.ModuleOffset + "\n")
            if self.signature != "":
                f.writelines("- signature(.so) : " + self.signature + "\n")
