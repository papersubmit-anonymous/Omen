//定义了标准字符串的大小
const STD_STRING_SIZE = 3 * Process.pointerSize;
// 引入延迟发送的时间间隔（以毫秒为单位）
const SEND_INTERVAL = 50; // 100毫秒
//封装C++ std::string的类
class StdString {
    //构造函数
    constructor() {
        this.handle = Memory.alloc(STD_STRING_SIZE);
    }

    dispose() {
        const [data, isTiny] = this._getData();
        if (!isTiny) {
            Java.api.$delete(data);
        }
    }

    disposeToString() {
        const result = this.toString();
        this.dispose();
        return result;
    }

    toString() {
        const [data] = this._getData();
        return data.readUtf8String();
    }

    _getData() {
        const str = this.handle;
        const isTiny = (str.readU8() & 1) === 0;
        const data = isTiny ? str.add(1) : str.add(2 * Process.pointerSize).readPointer();
        return [data, isTiny];
    }
}

// 用于将一个方法ID（method_id）转换为一个人类可读的字符串
function prettyMethod(method_id, withSignature) {
    const result = new StdString();
    Java.api['art::ArtMethod::PrettyMethod'](result, method_id, withSignature ? 1 : 0);
    return result.disposeToString();
}

// 从内存中读取C++ std::string并将其转换为JS字符串
function readStdString(str) {
    if ((str.readU8() & 1) === 1) { // size LSB (=1) indicates if it's a long string
        return str.add(2 * Process.pointerSize).readPointer().readUtf8String();
    }
    return str.add(1).readUtf8String();
}

function attach(addr) {
    Interceptor.attach(addr, {
        onEnter: function (args) {
            this.arg0 = args[0]; // this
        },
        onLeave: function (retval) {
            var modulemap = new ModuleMap()
            modulemap.update()
            var module = modulemap.find(retval)
            // var string = Memory.alloc(0x100)
            // ArtMethod_PrettyMethod(string, this.arg0, 1)
            if (module != null) {
                var module_base = module.base
                var method_offset = ptr(retval).sub(module.base)
                var method_addr = ptr(retval)
                console.log('<' + module.name + '> method_name =>',
                    prettyMethod(this.arg0, 1),
                    ',offset=>', method_offset, ',module_name=>', module.name)
                setTimeout(() => {
                    send({
                        'type': 'dymaic_method_with_model',
                        'module_name': module.name,
                        'module_base': module_base,
                        'method_signature': prettyMethod(this.arg0, 1),
                        'method_offset': method_offset,
                        'method_addr': method_addr
                    });
                }, SEND_INTERVAL);
            } else {
                console.log('<anonymous> method_name =>', readStdString(string), ', addr =>', ptr(retval))
                setTimeout(() => {
                    send({
                        'type': 'dymaic_method_with_anonymous',
                        'module_name': "<anonymous>",
                        'method_signature': readStdString(string),
                        'method_addr': ptr(retval)
                    });
                }, SEND_INTERVAL);
            }
        }
    });
}


function loadAllModules(){

}

function hook_RegisterNative() {
    var libart = Process.findModuleByName('libart.so')
    var symbols = libart.enumerateSymbols()
    for (var i = 0; i < symbols.length; i++) {
        if (symbols[i].name.indexOf('RegisterNative') > -1 && symbols[i].name.indexOf('ArtMethod') > -1 && symbols[i].name.indexOf('RuntimeCallbacks') < 0) {
            //art::RuntimeCallbacks::RegisterNativeMethod(art::ArtMethod*, void const*, void**)
            attach(symbols[i].address)
        }
    }

}

function start() {
   setImmediate(hook_RegisterNative)
}

//setImmediate(hook_RegisterNative);

rpc.exports = {
    start: start
}
