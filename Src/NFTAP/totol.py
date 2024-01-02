import csv
import os.path
import pickle
import psutil
from NFTAP.weight import weightCalculation
from concurrent.futures import ProcessPoolExecutor
totalnumpath = "num.txt"
wordir = "..\workDirs"
totalsignpath = "sign.txt"
totalcsv = "num.csv"
Gtotalnum = 0
Gjavanum = 0
Gjninum = 0
total = []
totalsign = []
signdict = {}

def assessment(apkpath):
    global wordir, Gtotalnum, Gjavanum, Gjninum, totalnumpath, totalsignpath, total, totalsign
    # wordir = app.workDir
    sourceMethods = []
    javaMethods = []
    unknownMethods = []
    # wordir = "..\workDirs\com_v2ray_ang"
    pkldir = os.path.join(wordir, apkpath, "methodpkl")
    # print(pkldir)
    pkl_files = [f for f in os.listdir(pkldir) if f.endswith(".pkl")]
    totalnum = 0
    javanum = 0
    jninum = 0
    numpath = os.path.join(wordir, apkpath, "num.txt")
    signpath = os.path.join(wordir, apkpath, "sign.txt")
    with open(numpath, 'w', encoding='utf-8') as file:
            pass
    with open(signpath, 'w', encoding='utf-8') as file:
            pass
    for pkl in pkl_files:
        paths = os.path.join(pkldir, pkl)
        try:
            sign = ""
            with open(paths, "rb") as f:
                method = pickle.load(f)
                totalnum = totalnum + 1
                Gtotalnum = Gtotalnum + 1
                if method.type == "Java":
                    javanum = javanum + 1
                    Gjavanum = Gjavanum + 1
                else:
                    jninum = jninum + 1
                    Gjninum = Gjninum + 1
                sign = method.ReturnType
                if "String" in sign:
                    sign = "String"
                else:
                    sign = method.ReturnType
                for Param in method.Params:
                    if "String" in Param[0]:
                        sign = sign + " " + "String"
                    elif "String[]" in Param[0]:
                        sign = sign + " " + "String[]"
                    else:
                        sign = sign + " " + Param[0]
            totalsign.append(sign)
            with open(signpath, 'a', encoding='utf-8') as file:
                file.writelines(sign + "\n")
            with open(totalsignpath, 'a', encoding='utf-8') as file:
                file.writelines(sign + "\n")
        except:
            pass
    with open(numpath, 'a', encoding='utf-8') as file:
        file.writelines("[Total Method Num] : " + str(totalnum) + "\n")
        file.writelines("[Java Method Num] : " + str(javanum) + "\n")
        file.writelines("[JNI Method Num] : " + str(jninum) + "\n")
    pkgname = apkpath.replace('_', '.')
    total.append([pkgname, totalnum, javanum, jninum])
    with open(totalnumpath, 'a', encoding='utf-8') as file:
        file.writelines("==================" + apkpath + "==================" + "\n")
        file.writelines("[Total Method Num] : " + str(totalnum) + "\n")
        file.writelines("[Java Method Num] : " + str(javanum) + "\n")
        file.writelines("[JNI Method Num] : " + str(jninum) + "\n")


if __name__ == '__main__':
    # 将非空行写入新文件
    with open(totalnumpath, 'w', encoding='utf-8') as file:
        pass
    with open(totalsignpath, 'w', encoding='utf-8') as file:
        pass
    # 遍历目录下的所有文件夹
    # 获取目录下所有子文件和文件夹
    sub_items = os.listdir(wordir)
    # 过滤出所有的文件夹名字
    sub_folders = [sub_item for sub_item in sub_items if os.path.isdir(os.path.join(wordir, sub_item))]
    # 获取真实CPU核心数
    true_cpu_cores = psutil.cpu_count(logical=False)
    # 创建进程池
    with ProcessPoolExecutor(max_workers=true_cpu_cores) as executor:
        # 处理所有的文件夹
        for sub_folder in sub_folders:
            # 处理子文件夹
            print(sub_folder)
            assessment(sub_folder)
    with open(totalnumpath, 'a', encoding='utf-8') as file:
        file.writelines("[Total Method Num] : " + str(Gtotalnum) + "\n")
        file.writelines("[Java Method Num] : " + str(Gjavanum) + "\n")
        file.writelines("[JNI Method Num] : " + str(Gjninum) + "\n")
    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['packagename', 'totalnum', 'javanum', 'jninum'])
        for row in total:
            writer.writerow(row)
    for sign in totalsign:
        signdict[sign] = 0
    for sign in totalsign:
        tmp = signdict[sign]
        tmp = tmp + 1
        signdict[sign] = tmp
    with open("signjs.txt", 'w', encoding='utf-8') as file:
        for sign in signdict:
            file.writelines(sign + " : " + str(signdict[sign]) + " : " + str(signdict[sign]/len(totalsign)) + "\n")

