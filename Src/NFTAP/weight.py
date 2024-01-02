basicType = ['long', 'int', 'string', 'char', 'charsequence', 'boolean', 'void', 'byte', 'short', 'float', 'double']
basictype5 = ['string', 'char', 'charsequence']
basictype3 = ['long', 'int', 'short', 'float', 'double']
basictype1 = ['boolean', 'void', 'byte']

method5 = ["alloc", "realloc", "free", "memcpy"]
method4 = ["create", "delete", "modify", "update"]
method3 = ["set", "get", "access", "load", "save"]
method2 = ["encrypt", "decrypt", "hash", "sign"]

model4 = ["ssl", "crypto", "network"]


def weightCalculation(method):
    Params = method.Params
    # Parameter Analysis
    totalScore = 0.0
    # Memory operation sensitivity
    for Param in Params:
        flag = True
        for sz in basictype5:
            if sz in Param[0].lower():
                totalScore = totalScore + (0.4 * 5)
                flag = False
                break
        if flag:
            for sz in basictype3:
                if sz in Param[0].lower():
                    totalScore = totalScore + (0.4 * 3)
                    flag = False
                    break
        if flag:
            for sz in basictype1:
                if sz in Param[0].lower():
                    totalScore = totalScore + (0.4 * 2)
                    flag = False
                    break
        if flag:
            totalScore = totalScore + (0.4 * 1)
    # Method name keyword
    MethodName = method.MethodName
    flag = True
    for sz in method5:
        if sz in MethodName.lower():
            totalScore = totalScore + (0.3 * 5)
            flag = False
            break
    if flag:
        for sz in method4:
            if sz in MethodName.lower():
                totalScore = totalScore + (0.3 * 4)
                flag = False
                break
    if flag:
        for sz in method3:
            if sz in MethodName.lower():
                totalScore = totalScore + (0.3 * 3)
                flag = False
                break
    if flag:
        for sz in method2:
            if sz in MethodName.lower():
                totalScore = totalScore + (0.3 * 2)
                flag = False
                break
    if flag:
        totalScore = totalScore + (0.3 * 1)
    # Library name/module name
    ModuleName = method.ModuleName
    for sz in model4:
        if sz in ModuleName.lower():
            totalScore = totalScore + (0.2 * 1)
            break
    totalScore = totalScore + (0.3 * len(Params))
    method.weight = totalScore
