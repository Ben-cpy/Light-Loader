import importlib
import time
import sys
import cProfile
import pstats
import sysconfig
import tracemalloc

def main():
    tracemalloc.start(50)
    std_lib_path = sysconfig.get_paths()["stdlib"]
    initial_modules = set(sys.modules.keys())
    initial_memory = tracemalloc.get_traced_memory()[0] / (1024 * 1024)
    print(f"Initial memory usage: {initial_memory:.2f} MB")

    # Import the modules
    init_st = time.time() * 1000
    try:
        requests = importlib.import_module('requests')
        html = importlib.import_module('lxml.html')
    except ImportError as e:
        print(f"Error importing modules: {e}")
        sys.exit(1)
    after_import_modules = set(sys.modules.keys())

    after_import_memory = tracemalloc.get_traced_memory()[0] / (1024 * 1024)
    print(f"Memory usage after import: {after_import_memory:.2f} MB") # 7.67MB


    #--------------------------------
    def handle():
        start = time.time() * 1000
        url = "https://www.baidu.com/"
        response = requests.get(url)
        tree = html.fromstring(response.content)
        end = time.time() * 1000
        return f'Latency is {end - start:.2f}ms'
    
    before_handle_snapshot = tracemalloc.take_snapshot()
    profiler = cProfile.Profile()
    profiler.enable()
    handle_result = handle()
    profiler.disable()
    after_handle_snapshot = tracemalloc.take_snapshot()  # Snapshot before analysis
    ps = pstats.Stats(profiler)

    # ----------------------------------
    total_memory_after_handle = tracemalloc.get_traced_memory()[0] / (1024 * 1024)
    print(f"\nTotal memory usage after handle(): {total_memory_after_handle:.2f} MB")

    new_modules = after_import_modules - initial_modules

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
            filename_to_new_modules.setdefault(filename, set()).add(name)

    # Map filenames to module names
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

    # Collect used modules based on profiling stats
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

    # Determine redundant files and modules
    redundant_files = set(filename_to_new_modules.keys()) - used_file_set # 114 slightly more due to trace existence
    print('The size of redundant_files:', len(redundant_files))
    redundant_modules = set()
    for file in redundant_files:
        modules = filename_to_new_modules.get(file, set())
        redundant_modules.update(modules)


    # Calculate redundant memory usage by iterating over redundant_files
    redundant_memory = 0
    for file in redundant_files:
        allocations = after_handle_snapshot.filter_traces((
            tracemalloc.Filter(True, file),
        ))
        mod_memory = sum(trace.size for trace in allocations.traces)
        redundant_memory += mod_memory
        # Get module names for the file
        module_names = filename_to_new_modules.get(file, [])
        module_names_str = ', '.join(module_names)
        print(f"File: {file}, Modules: {module_names_str}, Estimated Memory Usage: {mod_memory/(1024 * 1024) :.2f} MB")

    redundant_memory_mb = redundant_memory / (1024 * 1024)
    print(f"\nTotal redundant modules memory usage: {redundant_memory_mb:.2f} MB")

    # Compute total memory increase from initial
    total_memory_increase = after_import_memory - initial_memory
    if total_memory_increase > 0:
        percentage = (redundant_memory_mb / total_memory_increase) * 100
        print(f"Redundant modules occupy {percentage:.2f}% of the total memory increase.")
    else:
        print("Total memory did not increase after handle().")

    tracemalloc.stop()

if __name__ == "__main__":
    main()
