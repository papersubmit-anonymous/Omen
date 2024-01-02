// 引入延迟发送的时间间隔（以毫秒为单位）
const SEND_INTERVAL = 100; // 100毫秒

function findRawJni(targetModule) {
    //const targetFunctionName = "stringFromJNI";
    // 获取所有加载的模块
    const modules = Process.enumerateModules();
    // 遍历每个模块
    for (const module of modules) {
        if (module.name.includes(targetModule)) {
            // 检查每个导出函数的名称是否与目标函数名匹配
            // 获取模块的导出函数
            const exports = module.enumerateExports();
            for (const exp of exports) {
                //console.log(exp.name);
                // 输出找到的模块信息
                if (exp.name.includes("Java_")) {
                    console.log("Function Name:", exp.name);
                    console.log("Function address:", exp.address);
                    console.log("Found target function in module:", module.name);
                    console.log("Module base address:", module.base);
                    console.log("method_offset:", ptr(exp.address).sub(module.base));
                    setTimeout(() => {
                        send({
                            'type': 'JNIMethod',
                            'Name': exp.name,
                            'ModuleName': module.name,
                            'ModuleOffset': ptr(exp.address).sub(module.base),
                        });
                    }, SEND_INTERVAL);
                } else {
                    setTimeout(() => {
                        send({
                            'type': 'Method',
                            'Name': exp.name,
                            'ModuleName': module.name,
                            'ModuleOffset': ptr(exp.address).sub(module.base),
                        });
                    }, SEND_INTERVAL);
                }
            }
        }
    }
}

function scan(modules) {
    const interval = 1000;  // 1 seconds (in milliseconds)
    setInterval(() => {
        for (const module of modules) {
            findRawJni(module)
        }
    }, interval);
}

//let TargetModules = ['libjpgt.so', 'liblept.so', 'libpngt.so', 'libtess.so']
//let packageName = "com.simplemobiletools.gallery.pro"
//start(TargetModules, packageName)
//const targetModuleName = "libtun2socks.so"
//const TargetModules = ["libmmkv.so", "libgojni.so", "libtun2socks.so"]
//start(TargetModules)


rpc.exports = {
    scan: scan,
}