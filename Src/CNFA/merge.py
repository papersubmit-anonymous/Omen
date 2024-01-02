import os
from object.jnimethod import JNIMethod

'''
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
        self.type = "
    
'''

# JNIMethods来自Frida动态扫描，staticMethodObjs来自静态分析
# JNIMethods都是在C/C++层以Java_开头符合JNI规约的方法
# staticMethodObjs都在Java层声明的Natvie方法
# JNIMethods -》 class Method
# staticMethodObjs - 》 class Stjni
# 所以这里返回的一定都是Native方法，只不过是有无原生库映射
'''
JNIMethods
========== Method ==========
Method Name : Java_com_example_myapplication_MainActivity_stringFromJNI
Module Name : libmyapplication.so
Module Offset : 0x1fa90
'''
'''
staticMethodObjs
========== Method ==========
- Package Name : package com.example.myapplication;
- Class Name : MainActivity
- Library : myapplication
- Method : stringFromJNI()
- Static : Dymaic
- Return Type : String
- Param Count : 0
'''


def mergeExtLib(JNIMethods, staticMethodObjs, app):
    mergejnis = []
    for JNIs in JNIMethods:
        # 限制一定属于目前APP的Native Library
        if JNIs.ModuleName in app.library:
            tmpstr = JNIs.Name  # C/C++层方法名称
            # Java_com_example_myapplication_MainActivity_stringFromJNI
            # 按照JNI规约可获取其它信息
            tmpstr = tmpstr.split("_")
            # 获取Java包名
            package_name_group = tmpstr[1:-2]
            package_name = ""  # com.example.myapplication
            for index in range(len(package_name_group)):
                if index < len(package_name_group) - 1:
                    package_name = package_name + package_name_group[index] + "."
                else:
                    package_name = package_name + package_name_group[index]
            # 获取Java类名
            class_name = tmpstr[-2]  # MainActivity
            # 获取Java方法名
            method_name = tmpstr[-1]  # stringFromJNI
            newJNI = JNIMethod()
            newJNI.type = "Java"
            # 这个方法所在的包名
            newJNI.PackageName = package_name
            # 这个方法所在的类名
            newJNI.ClassName = class_name
            # 这个方法所在的库名
            newJNI.ModuleName = JNIs.ModuleName
            # 这个方法的C/C++层名称
            newJNI.MethodName = JNIs.Name
            # 这个方法的Java方法名
            # libmyapplication.so
            newJNI.Method = method_name
            # 这个方法在原生库的偏移
            # 0x1fa90
            newJNI.ModuleOffset = JNIs.ModuleOffset
            mergejnis.append(newJNI)
    # staticMethodObj 也一定是原生方法
    for staticMethodObj in staticMethodObjs:
        flag = True
        for jni in mergejnis:
            # 如果在同一个类、同一个名称则合并
            '''
            jni.Method = stringFromJNI
            jni.ClassName = MainActivity
            staticMethodObj.method = stringFromJNI()
            staticMethodObj.aclass = MainActivity
            '''
            if jni.Method in staticMethodObj.method and staticMethodObj.aclass in jni.ClassName:
                # 这个方法在Java层的返回值
                jni.ReturnType = staticMethodObj.return_type
                # 这个方法的参数数量
                jni.ParamCount = staticMethodObj.param_count
                # 这个方法的具体参数
                jni.Params = staticMethodObj.params
                # 这个方法所在的Java层库名
                jni.Library = staticMethodObj.library
                jni.Static = staticMethodObj.static
                flag = False
                break
        if flag:
            # 未能和原生层匹配上的原生方法
            newJNI = JNIMethod()
            newJNI.type = "Unknown"
            # 这个方法所在的包名
            # com.example.myapplication
            newJNI.PackageName = staticMethodObj.package.split("package ")[1].split(";")[
                0]  # package com.example.myapplication;
            # 这个方法所在的类名
            # MainActivity
            newJNI.ClassName = staticMethodObj.aclass
            # 这个方法所在的Java层库名
            # myapplication
            newJNI.Library = staticMethodObj.library
            # 这个方法对应的Java层名称
            # stringFromJNI
            newJNI.Method = staticMethodObj.method.split("(")[0]
            # 这个方法在Java层的返回值
            # String
            newJNI.ReturnType = staticMethodObj.return_type
            # 这个方法的参数数量
            newJNI.ParamCount = staticMethodObj.param_count
            # 这个方法的具体参数
            newJNI.Params = staticMethodObj.params
            mergejnis.append(newJNI)
    return mergejnis


# mergeJNIMethods一定是原生方法，hookJNIMethods一定是JNI函数
# mergeJNIMethods -》 class JNIMethod
# hookMethods -》 class HookMethod
'''
========== Method ==========
- method_signature : java.lang.String com.example.myapplication.NativeLoader.getNativeString()
- method_offset : 0x1fc00
- module_name : libmyapplication.so
'''


def mergeHookJNImethod(mergeJNIMethods, hookMethods, app):
    for hookMethod in hookMethods:
        if hookMethod.module_name in app.library:
            flag = True
            hookSignature = hookMethod.method_signature
            hookSignature = hookSignature.split(" ")[1]
            PackageName = ""
            PackageNameG = hookSignature.split(".")[:-2]
            for index in range(len(PackageNameG)):
                if index < len(PackageNameG) - 1:
                    PackageName = PackageName + PackageNameG[index] + "."
                else:
                    PackageName = PackageName + PackageNameG[index]
            print(PackageName)
            Method = hookSignature.split(".")[-1].split("(")[0]
            for JNIMethods in mergeJNIMethods:
                if JNIMethods.PackageName in PackageName and JNIMethods.Method in Method:
                    JNIMethods.ModuleName = hookMethod.module_name
                    JNIMethods.ModuleOffset = hookMethod.method_offset
                    JNIMethods.signature = hookMethod.method_signature
                    flag = False
                    break
        '''
        if flag:
            method_offset = hookMethod.method_offset
            module_name = hookMethod.module_name
            if module_name in app.library:
                signature = hookMethod.method_signature
                returntpe = signature.split(" ")[0]
                sourceParams = signature.split("(")[1].split(")")[0]
                sourceParams = sourceParams.split(", ")
                Params = []
                for param in sourceParams:
                    if param != '':
                        lists = [param, ""]
                        Params.append(lists)
                ParamCount = len(Params)
                MethodName = signature.split(" ")[1].split("(")[0]
                tmpgroup = MethodName.split(".")[:-2]
                PackageName = ""
                for index in range(len(tmpgroup)):
                    if index < len(tmpgroup) - 1:
                        PackageName = PackageName + tmpgroup[index] + "."
                    else:
                        PackageName = PackageName + tmpgroup[index]
                ClassName = MethodName.split(".")[-2]
                Method = MethodName.split(".")[-1]
                newJNI = JNIMethod()
                newJNI.type = "Unknown"
                newJNI.PackageName = PackageName
                newJNI.ClassName = ClassName
                newJNI.Method = Method
                newJNI.ReturnType = returntpe
                newJNI.ParamCount = ParamCount
                newJNI.Params = Params
                newJNI.MethodName = MethodName
                newJNI.ModuleName = module_name
                newJNI.ModuleOffset = method_offset
                newJNI.signature = signature
                if module_name in app.library:
                    mergeJNIMethods.append(newJNI)'''


def mergeHookmethod(Methods, hookMethods, app, mergeJNIMethods):
    for hookM in hookMethods:
        if hookM.module_name in app.library:
            for JNIs in Methods:
                if JNIs.ModuleName == hookM.module_name and JNIs.ModuleOffset == hookM.method_offset:
                    tmpstr = JNIs.Name  # C/C++层方法名称
                    # Java_com_example_myapplication_MainActivity_stringFromJNI
                    # 按照JNI规约可获取其它信息
                    tmpstr = tmpstr.split("_")
                    # 获取Java包名
                    package_name_group = tmpstr[1:-2]
                    package_name = ""  # com.example.myapplication
                    for index in range(len(package_name_group)):
                        if index < len(package_name_group) - 1:
                            package_name = package_name + package_name_group[index] + "."
                        else:
                            package_name = package_name + package_name_group[index]
                    # 获取Java类名
                    class_name = tmpstr[-2]  # MainActivity
                    # 获取Java方法名
                    method_name = tmpstr[-1]  # stringFromJNI
                    newJNI = JNIMethod()
                    newJNI.type = "Java"
                    # 这个方法所在的包名
                    newJNI.PackageName = package_name
                    # 这个方法所在的类名
                    newJNI.ClassName = class_name
                    # 这个方法所在的库名
                    newJNI.ModuleName = JNIs.ModuleName
                    # 这个方法的C/C++层名称
                    newJNI.MethodName = JNIs.Name
                    # 这个方法的Java方法名
                    # libmyapplication.so
                    newJNI.Method = method_name
                    # 这个方法在原生库的偏移
                    # 0x1fa90
                    newJNI.ModuleOffset = JNIs.ModuleOffset
                    mergeJNIMethods.append(newJNI)
                    break





