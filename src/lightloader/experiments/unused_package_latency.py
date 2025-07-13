"""
Calculate the latency occupied by unused modules in the total.
"""
import importlib
import time
import sys
import cProfile
import pstats
import sysconfig
import builtins
from functools import wraps

# global dictionary for storing load time of each module (milliseconds)
module_load_times = {}

def track_imports():
    """
    set a hook to trace load time
    """
    original_import = __import__

    def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
        start_time = time.time()
        module = original_import(name, globals, locals, fromlist, level)
        end_time = time.time()
        load_time = (end_time - start_time) * 1000  # convert to milliseconds
        module_load_times[name] = load_time
        return module

    builtins_import = __import__
    sys.modules_import = builtins_import
    builtins.__import__ = custom_import

def restore_imports():
    """
    Restore the original import function.
    """
    if hasattr(sys, 'modules_import'):
        builtins.__import__ = sys.modules_import

def main():
    # setup import tracking
    track_imports()

    std_lib_path = sysconfig.get_paths()["stdlib"]
    builtin_modules = set(sys.builtin_module_names)
    
    initial_modules = set(sys.modules.keys())
    print("Initial modules count: {}".format(len(initial_modules)))
    init_st = time.time() * 1000
    
    try:
        requests = importlib.import_module('requests')
        html = importlib.import_module('lxml.html')
    except ImportError as e:
        sys.exit(1)
    init_ed = time.time() * 1000 

    print(f"Module load time: {init_ed - init_st:.2f}ms")
    init_module_load_time  = init_ed - init_st
    after_import_modules = set(sys.modules.keys())
    print(f"Modules loaded after import (contains duplicated): {len(after_import_modules)}")
    new_modules = after_import_modules - initial_modules # contains duplicates
    
    filename_to_new_modules = {}
    for name in new_modules:
        module = sys.modules.get(name)
        if module is None:
            continue
        filename = getattr(module, '__file__', None)
        if filename:
            filename = filename.replace('\\', '/')
            if filename.endswith(('.pyc', '.pyo')):
                filename = filename[:-1]
            filename_to_new_modules.setdefault(filename, set()).add(name) # filename is unique
    
    print(f"Unique files for new modules: {len(filename_to_new_modules)}")
    
    def handle():
        start = time.time() * 1000 
        url = "https://www.baidu.com/"
        response = requests.get(url)
        tree = html.fromstring(response.content)
        end = time.time() * 1000 
        return f'Latency is {end - start:.2f}ms'
    
    profiler = cProfile.Profile()
    profiler.enable()
    handle()
    profiler.disable()
    
    ps = pstats.Stats(profiler)
    
    filename_to_module = {}
    for name, module in sys.modules.items():
        if module is None:
            continue
        filename = getattr(module, '__file__', None)
        if filename:
            filename = filename.replace('\\', '/')
            if filename.endswith(('.pyc', '.pyo')):
                filename = filename[:-1]
            filename_to_module.setdefault(filename, set()).add(name)
    
    used_modules = set()
    used_file_set = set()
    for func in ps.stats:
        filename = func[0]
        if not filename:
            continue
        filename = filename.replace('\\', '/')
        module_names = filename_to_module.get(filename, None)
        if module_names:
            used_modules.update(module_names)
            used_file_set.add(filename)
    
    print("\nProfiling Results:")
    print(f"Number of unique function files used: {len(used_file_set)}")
    print(f"Number of modules used (contain duplicated modules): {len(used_modules)}")
    
    redundant_files = set(filename_to_new_modules.keys()) - used_file_set
    print('The number of unused module files:', len(redundant_files))
    
    # calculate redundant module ratio
    print("Rate: unused module/new imported module = {:.2f}%".format(
        len(redundant_files) / len(filename_to_new_modules) * 100 if filename_to_new_modules else 0
    ))
    
    # 获取对应的模块
    redundant_modules = set()
    for file in redundant_files:
        modules = filename_to_new_modules.get(file, set())
        redundant_modules.update(modules)
    
    # calculate total load time and corresponding module names for redundant modules
    redundant_load_time = 0.0
    redundant_modules_names = []  # 用于存储冗余模块的名称
    for mod in redundant_modules:
        load_time = module_load_times.get(mod, 0)
        redundant_load_time += load_time
        redundant_modules_names.append(mod) # 添加模块名

    # 将冗余模块名写入文件
    with open("redundant_modules.txt", "w") as f:
        for mod in redundant_modules_names:
            f.write(f"{mod}\n")
    
    # 计算所有新导入模块的总加载时间和对应模块名称
    total_load_time = 0.0
    new_modules_names = []
    for mod in new_modules:
        load_time = module_load_times.get(mod, 0)
        total_load_time += load_time
        new_modules_names.append(mod)

    # write all newly imported module names to file
    with open("new_modules.txt", "w") as f:
        for mod in new_modules_names:
            f.write(f"{mod}\n")
    
    print(f"Calculated total_load_time: {total_load_time:.2f}ms")  # 添加这一行

    # 计算冗余模块加载时延占比
    redundant_ratio = (redundant_load_time / total_load_time) * 100

    
    print(f"Redundant modules load time: {redundant_load_time:.2f}ms")
    print(f"Total new modules load time: {total_load_time:.2f}ms")
    print(f"Redundant modules load time ratio: {redundant_ratio:.2f}%")
    
    # restore original import function
    restore_imports()

if __name__ == "__main__":
    main()
