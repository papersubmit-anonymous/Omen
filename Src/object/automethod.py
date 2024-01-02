import os


class AutoMethod:
    def __init__(self):
        # libmyapplication.so
        self.Module = ""
        # Java_com_example_myapplication_MainActivity_stringFromJNI
        self.SoName = ""
        # stringFromJNI
        self.JavaName = ""
        self.Class = ""
        self.Package = ""
        self.ParamCount = 0
        self.Params = []

    def Info(self):
        print("========== Method ==========")
        if self.Module != "":
            print("- Module : ", self.Module)
        if self.SoName != "":
            print("SoName : ", self.SoName)
        if self.JavaName != "":
            print("- JavaName : ", self.JavaName)
        if self.Class != "":
            print("- Class : ", self.Class)
        if self.Package != "":
            print("- Package : ", self.Package)
        if self.ParamCount != "":
            print("- Param Count : ", self.ParamCount)
        if self.Params != "":
            print("- Params : ", self.Params)

    def log(self, app):
        logPath = os.path.join(app.workDir, "AutoMethods.txt")
        with open(logPath, "a") as f:
            f.writelines("========== AutoMethod ==========\n")
            if self.Module != "":
                f.writelines("- type : " + self.Module + "\n")
            if self.SoName != "":
                f.writelines("SoName : " + self.SoName + "\n")
            if self.JavaName != "":
                f.writelines("- JavaName : " + self.JavaName + "\n")
            if self.Class != "":
                f.writelines("- Class : " + self.Class + "\n")
            if self.Package != "":
                f.writelines("- Package : " + self.Package + "\n")
            if self.ParamCount != "":
                f.writelines("- Param Count : " + str(self.ParamCount) + "\n")
            if self.Params:
                for param in self.Params:
                    f.writelines("- Params Type: " + param[0] + " Params ID: " + param[1] + "\n")