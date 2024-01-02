from object.automethod import AutoMethod

def checkauto(method, app):
    ModuleName = ""
    SoName = ""
    JavaName = ""
    Class = ""
    Package = ""
    ParamCount = 0
    Params = []
    if method.ParamCount != 0:
        ParamCount = method.ParamCount
    else:
        return None
    if method.Params != []:
        Params = method.Params
    else:
        return None
    # 检查Library
    if method.ModuleName != "":
        ModuleName = method.ModuleName
    elif method.Library != "":
        for libray in app.library:
            if method.Library in libray:
                ModuleName = libray
    else:
        pass
    if method.MethodName != "":
        SoName = method.MethodName
    if method.Method != "":
        JavaName = method.Method
    if method.ClassName != "":
        Class = method.ClassName
    if method.PackageName != "":
        Package = method.PackageName
    newAutoMethod = AutoMethod()
    newAutoMethod.Module = ModuleName
    # Java_com_example_myapplication_MainActivity_stringFromJNI
    newAutoMethod.SoName = SoName
    # stringFromJNI
    newAutoMethod.JavaName = JavaName
    newAutoMethod.Class = Class
    newAutoMethod.Package = Package
    newAutoMethod.ParamCount = ParamCount
    newAutoMethod.Params = Params
    return newAutoMethod
