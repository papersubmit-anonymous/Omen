import os.path
import pickle

from NFTAP.weight import weightCalculation

basicType = ['long', 'int', 'string', 'char', 'charsequence', 'boolean', 'void', 'byte', 'short', 'float', 'double']

def checkType(typestr):
    flag = False
    for ch in basicType:
        if ch in typestr.lower():
            flag = True
            break
    return flag

def sort_key(obj):
    return (obj.weight, obj.MethodName[0], obj.ModuleName[0])

def assessment(wordir):
    #wordir = app.workDir
    sourceMethods = []
    javaMethods = []
    unknownMethods = []
    #wordir = "..\workDirs\com_v2ray_ang"
    pkldir = os.path.join(wordir, "methodpkl")

    pkl_files = [f for f in os.listdir(pkldir) if f.endswith(".pkl")]
    for pkl in pkl_files:
        paths = os.path.join(pkldir, pkl)
        #print(paths)
        try:
            with open(paths, "rb") as f:
                method = pickle.load(f)
                #method.info()
                if len(method.Params) != 0 and method.Params[0] != ['', '']:
                    flag = True
                    if len(method.Params) == 1 and "bool" in method.Params[0][0]:
                        flag = False
                    Params = method.Params
                    for Param in Params:
                        #print("[+] Check : ", Param)
                        if not checkType(Param[0]):
                            #print("[X]")
                            flag = False
                    if flag:
                        #method.info()
                        sourceMethods.append(method)
        except:
            pass



    for method in sourceMethods:
        #method.info()
        weightCalculation(method)
        #print(method.weight)
        '''
        if method.type == "Java":
            javaMethods.append(method)
        else:
            unknownMethods.append(method)'''

    sorted_objects = sorted(sourceMethods, key=sort_key)
    sourceMethods = sorted_objects[::-1]

    for method in sourceMethods:
        method.info()
        #print(method.weight)
        if method.type == "Java":
            javaMethods.append(method)
        else:
            unknownMethods.append(method)

    pathjava = os.path.join(wordir, "javaMethods")
    if not os.path.exists(pathjava):
        os.mkdir(pathjava)
    index = 1
    for method in javaMethods:
        savepath = os.path.join(pathjava, str(index) + "-" + method.MethodName.replace(".", "_") + ".pkl")
        with open(savepath, "wb") as f:
            pickle.dump(method, f)
        index = index + 1

    pathUnknown = os.path.join(wordir, "unknownMethods")
    if not os.path.exists(pathUnknown):
        os.mkdir(pathUnknown)
    index = 1
    for method in unknownMethods:
        savepath = os.path.join(pathUnknown, str(index) + "-" + method.MethodName.replace(".", "_") + ".pkl")
        with open(savepath, "wb") as f:
            pickle.dump(method, f)
        index = index + 1



if __name__ == '__main__':
    wordir = "..\workDirs\com_v2ray_ang"


    assessment(wordir)