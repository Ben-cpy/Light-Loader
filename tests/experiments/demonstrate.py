import importlib
import time
import sys
import cProfile
import pstats
import sysconfig

def main():
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
    
    after_import_modules = set(sys.modules.keys())
    print(f"Modules loaded after import(contains duplicated): {len(after_import_modules)}")
    new_modules = after_import_modules - initial_modules # containes duplicated items
    
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
    print(f"Number of modules used(contain duplicated module): {len(used_modules)}")
    
    redundant_files = set(filename_to_new_modules.keys()) - used_file_set
    print('the size of unused modules', len(redundant_files))
    
    # 114 / 157
    print("Rate: unused module/new imported module = ",len(redundant_files)/len(filename_to_new_modules) * 100, "%")
    # get corresponding module 
    redundant_modules = set()
    for file in redundant_files:
        modules = filename_to_new_modules.get(file, set())
        redundant_modules.update(modules)



if __name__ == "__main__":
    main()
