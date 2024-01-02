// 引入延迟发送的时间间隔（以毫秒为单位）
const SEND_INTERVAL = 100; // 100毫秒

function loadModuel(TargetModules, packageName) {
    //const targetFunctionName = "stringFromJNI";
    // 获取所有加载的模块
    const modules = Process.enumerateModules();
    for (const module of modules) {
        for (let i = 0; i < TargetModules.length; i++) {
            if (module.name.includes(TargetModules[i])) {
                send({
                    'type': 'successLib',
                    'Name': module.name,
                });
                TargetModules.splice(i, 1);
                break
            } // 输出数组中的每个元素
        }
    }
    var suffix = ""
    var libpath = ""
    var flaglib = 0
    // 遍历每个模块.寻找installation suffix
    for (const module of modules) {
        if (module.path.includes(packageName)) {
            //const inputString = "/data/app/~~Vx0YSgkMF_NKN3VfCInTAg==/com.onix.worker-dcDxkjHCmQm86LZyI479ew==/oat/x86_64/base.odex";
            console.log("[+] Find module path: ", module.path);
            const regex = /\/data\/app\/[^\/]+/;
            //const regex = /^(\/data\/app\/[^\/]+\/[^\/]+)/;
            const match = module.path.match(regex);
            if (match) {
                const extractedString = match[0];
                console.log("Extracted String: ", extractedString);
                libpath = extractedString + "/lib/x86_64/";
                console.log("[+] Find APP Load Lib Path: ", libpath);
                flaglib = 1;
            } else {
                console.log("Failed to match the regex.");
            }
        }
    }
    if (flaglib !== 1) {
        return 0
    }
    for (let i = 0; i < TargetModules.length; i++) {
        console.log("[+] Try Load :", TargetModules[i])
        var path = libpath + TargetModules[i]
        console.log(path)
        try {
            Module.load(path)
            console.log("Load :", TargetModules[i])
            send({
                'type': 'successLib',
                'Name': TargetModules[i],
            });
            TargetModules.splice(i, 1);
        } catch (error) {
            console.error("发生错误:", error.message);
        }
    }
}

function start(TargetModules, packageName) {
    console.log("[+] Start: ", TargetModules)
    const interval = 2000;  // 1 seconds (in milliseconds)
    setInterval(() => {
        loadModuel(TargetModules, packageName);
    }, interval);
}


rpc.exports = {
    start: start,
}