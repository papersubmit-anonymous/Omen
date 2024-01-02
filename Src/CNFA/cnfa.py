import os
import subprocess
import time
import pickle

from CNFA.automethod import checkauto
from CNFA.scanLibrary import scan
from CNFA.staticExtractor import parseExtractor
from CNFA.merge import mergeExtLib, mergeHookJNImethod, mergeHookmethod
from CNFA.hookScan import hookScan
from object.app import App

extractorJarPath = os.path.join('CNFA', 'Extractor.jar')


def nonEmptyLine(workdir):
    # 定义输入文件和输出文件
    input_file = os.path.join(workdir, "log.txt")
    output_file = os.path.join(workdir, "StaticExtractor.txt")
    # 读取文件内容
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # 移除空行
    non_empty_lines = [line for line in lines if line.strip()]
    # 将非空行写入新文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(non_empty_lines)


def extraLib(libpath):
    libs = []
    if os.path.exists(libpath):
        for root, dirs, files in os.walk(libpath):
            for file in files:
                libs.append(file)
                # print(os.path.join(root, file))
    return libs


def cfnaScan(app):
    # 初始化信息
    workdir = app.workDir
    sourcePath = os.path.join(workdir, "sources")
    logPath = os.path.join(workdir, "log.txt")
    # 测量方法的执行时间
    start_time = time.perf_counter()
    # 使用Jar包中的JavaParser来分析AST树
    # java -jar CNFA\Extractor.jar .\workDirs\com_example_myapplication\sources .\workDirs\com_example_myapplication\log.txt
    cmd = f'java -jar {extractorJarPath} {sourcePath} {logPath}'
    print("[+] CMD : ", cmd)
    if app.rebuild:
        output = subprocess.check_output(cmd, shell=True).decode('utf-8')
        # 清除原始数据中的空行
        nonEmptyLine(workdir)
        print("[+] nonEmptyLine")
    else:
        pass
    # 通过扫描Java文件获取到的staticMethodObjs，主要是为了找到Class
    # 这里不用在看了
    staticMethodObjs = parseExtractor(workdir)
    print("[+] parseExtractor")
    # staticMethodObjs 里保存的一定是Java里的Native方法
    for staticMethodObj in staticMethodObjs:
        staticMethodObj.info()
        # 写入StaticExtractorJNIMethods.txt
        staticMethodObj.log(app)
    end_time = time.perf_counter()
    # 计算方法的执行时间
    duration = end_time - start_time
    # 将执行时间保存为字符串
    app.statictime = duration
    # 测量方法的执行时间
    # 通过Frida扫描导出库获取到的，如果是"Java_"开头分类到JNIMethods，反之Methods
    # 应该JNIMethod为基准，JNI需要符合JNI的命名约定
    print("[+] Frida Scan Liaray ")
    JNIMethods, Methods = scan(app)
    print("=========== JNIMethods ===========")
    for JNIMethod in JNIMethods:
        JNIMethod.info()
        # 写入JNIMethod_ScanLibrary.txt
        JNIMethod.Jlog(app)
        time.sleep(0.1)
    print("=========== Methods ===========")
    for Method in Methods:
        Method.info()
        # 写入Method_ScanLibrary.txt
        Method.Mlog(app)
        time.sleep(0.1)
    # 构建JNI Method
    # JNIMethods来自Frida动态扫描，staticMethodObjs来自静态分析
    # 所以这里返回的一定都是Native方法，只不过是有无原生库映射
    mergeJNIMethods = mergeExtLib(JNIMethods, staticMethodObjs, app)
    print("[+]Merge staticMethodObjs&&JNIMethods")
    for jniMethod in mergeJNIMethods:
        jniMethod.info()
        # 写入SourceJNIMethods.txt
        # jniMethod.log(app)
        # time.sleep(0.1)
    # 通过劫持ART注册函数获取到的JNI函数，一定是JNI函数但不一定属于本应用
    # class HookMethod
    hookJNIMethods = hookScan(app, timeout=30)
    for method in hookJNIMethods:
        method.info()
        # 写入HookMethods.txt
        method.log(app)
        time.sleep(0.1)
    # 需要考虑补充JNI Mehtod 和 非JNI Method
    # mergeJNIMethods一定是原生方法，hookJNIMethods一定是JNI函数
    mergeHookJNImethod(mergeJNIMethods, hookJNIMethods, app)
    print("[+] Merge Hook JNI Method && staticMethodObjs && JNIMethods")
    # NoneJnis = mergeHookMethod(Methods, hookJNIMethods)
    mergeHookmethod(Methods, hookJNIMethods, app, mergeJNIMethods)
    print("[+] Merge Hook JNI Method && Methods")
    print("[+]Merge HookMethods")
    print("=========== JNI Methods ===========")
    for JNIMethod in mergeJNIMethods:
        JNIMethod.info()
        # 写入SourceJNIMethods.txt
        JNIMethod.log(app)
        time.sleep(0.1)
    index = 0
    for method in mergeJNIMethods:
        #savepath = os.path.join(app.workDir, "methodpkl", method.MethodName.replace(".", "_") + ".pkl")
        savepath = os.path.join(app.workDir, "methodpkl", str(index) + ".pkl")
        with open(savepath, "wb") as f:
            pickle.dump(method, f)
        index = index + 1
    autoMethod = []
    for method in mergeJNIMethods:
        tmp = checkauto(method, app)
        if tmp is not None:
            autoMethod.append(tmp)
            tmp.log(app)
    index = 0
    for method in autoMethod:
        savepath = os.path.join(app.workDir, "autoMethod", str(index) + ".pkl")
        with open(savepath, "wb") as f:
            pickle.dump(method, f)
        index = index + 1
    return mergeJNIMethods
