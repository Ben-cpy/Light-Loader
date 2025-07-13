# import os
# import ast
# import cProfile
# import pstats
# import sys
# import importlib.util

# def get_all_functions(directory):
#     all_functions = set()
#     directory = os.path.abspath(directory)
    
#     for root, _, files in os.walk(directory):
#         for file in files:
#             if file.endswith('.py'):
#                 filepath = os.path.abspath(os.path.join(root, file))
#                 with open(filepath, 'r', encoding='utf-8') as f:
#                     try:
#                         tree = ast.parse(f.read(), filename=filepath)
#                         for node in ast.walk(tree):
#                             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
#                                 func_tuple = (filepath, node.lineno, node.name)
#                                 all_functions.add(func_tuple)
#                     except SyntaxError as e:
#                         print(f"Syntax error in {filepath}: {e}")
        
#     return all_functions

# # def run_handler_with_profile(handler_path):
# #     profiler = cProfile.Profile()
# #     profiler.enable()
    
# #     # Dynamically import handler.py and execute it
# #     spec = importlib.util.spec_from_file_location("handler", handler_path)
# #     handler = importlib.util.module_from_spec(spec)
# #     sys.modules["handler"] = handler
# #     spec.loader.exec_module(handler)
    
# #     profiler.disable()
    
# #     return profiler

# def run_handler_with_profile(handler_path):
#     profiler = cProfile.Profile()
#     profiler.enable()
    
#     # Dynamically import handler.py
#     spec = importlib.util.spec_from_file_location("handler", handler_path)
#     handler = importlib.util.module_from_spec(spec)
#     sys.modules["handler"] = handler
#     spec.loader.exec_module(handler)
    
#     # Call the handler function
#     if hasattr(handler, 'handle'):
#         handler.handle()
#     else:
#         print("No 'handle' function found in handler.py")
    
#     profiler.disable()
    
#     return profiler


# def extract_called_functions(profiler, directory):
#     called_functions = set()
#     directory = os.path.abspath(directory)
#     ps = pstats.Stats(profiler)
    
#     for func in ps.stats:
#         filename, line_number, func_name = func
#         filename = os.path.abspath(filename)
#         if filename.startswith(directory):
#             called_functions.add((filename, line_number, func_name))
#     return called_functions

# def main(directory):
#     directory = os.path.abspath(directory)
#     print("Analyzing all defined functions...")
#     all_defined_functions = get_all_functions(directory)
#     print(f"Total number of defined functions: {len(all_defined_functions)}")
    
#     handler_path = os.path.join(directory, 'handler.py')
#     if not os.path.isfile(handler_path):
#         print(f"handler.py not found in {directory}")
#         return
    
#     print("Running handler.py with profiling...")
#     profiler = run_handler_with_profile(handler_path)
#     print("Extracting called functions from profiling data...")
#     called_functions = extract_called_functions(profiler, directory)
#     print(f"Total number of called functions: {len(called_functions)}")

#     sorted_called_functions = sorted(list(called_functions))
#     print("\nFirst 30 called functions (or fewer if there are less than 30):")
#     for func in sorted_called_functions[:50]:
#         print(f"{func[0]}:{func[1]} - {func[2]}")
    
#     # unused_functions = all_defined_functions - called_functions
#     print(f"Number of unused functions: {len(all_defined_functions) - len(called_functions)}")
    
#     # if unused_functions:
#     #     print("\nUnused functions:")
#     #     for func in sorted(unused_functions):
#     #         print(f"{func[0]}:{func[1]} - {func[2]}")
#     # else:
#     #     print("All functions were used.")

# if __name__ == "__main__":
#     import argparse
#     # Change cwd into /home/chenpengyu/openfaas-la/app5
#     os.chdir("/home/chenpengyu/openfaas-la/app9")
#     parser = argparse.ArgumentParser(description="Analyze Python functions usage.")
#     parser.add_argument("directory", help="Path to the main directory containing Python packages and handler.py")
    
#     args = parser.parse_args()
#     main(args.directory)

import os
import ast
import cProfile
import pstats
import sys
import importlib.util
import argparse
import json  # 新增：导入 json 库以处理 JSON 输入

def get_input_for_function(function_name):
    """
    根据函数名称返回特定的、预先构建好的输入数据。
    这里是所有特殊输入的配置中心。
    """
    print(f"INFO: 为函数 '{function_name}' 查找特定输入...")

    # 为 midd-uploader 提供特定输入
    if function_name == "midd-uploader":
        # 注意：您提供的示例输入看起来更像压缩或下载任务，但遵循您的要求将其用于 uploader
        input_data = {"url": "http://ipv4.download.thinkbroadband.com/5MB.zip"}
        json_input = json.dumps(input_data)
        print(f"INFO: 找到特定输入: {json_input}")
        return json_input

    # 为 midd-graph-pagerank 提供特定输入
    elif function_name == "midd-graph-pagerank":
        input_data = {"size": 10000, "seed": 42}
        json_input = json.dumps(input_data)
        print(f"INFO: 找到特定输入: {json_input}")
        return json_input

    elif function_name == "midd-compression":
        input_data = {"num_files": 10, "file_size_kb": 128}
        json_input = json.dumps(input_data)
        print(f"INFO: 找到特定输入: {json_input}")
        return json_input    
    
    elif function_name == "midd-dynamic-html":
        input_data = {"username": "Alex", "random_len": 10}
        json_input = json.dumps(input_data)
        print(f"INFO: 找到特定输入: {json_input}")
        return json_input    
    
    elif function_name == "midd-sleep":
        return '1'

    elif function_name == "midd-thumbnailer":
        input_data = {
                       "filename": "cat.jpg",
                       "width": 150,
                       "height": 150
                   }
        json_input = json.dumps(input_data)
        print(f"INFO: 找到特定输入: {json_input}")
        return json_input    
    
    elif function_name == "midd-video-processing":
        input_data = {"filename": "cat.jpg", "width": 150, "height": 150}
        json_input = json.dumps(input_data)
        print(f"INFO: 找到特定输入: {json_input}")
        return json_input     
    # 您可以在这里添加更多的 elif 条件来支持其他函数
    # elif function_name == "another-function":
    #     return '{"key": "some_other_value"}'

    # 如果没有找到匹配的函数，则返回一个默认的空字符串输入
    else:
        print("INFO: 未找到特定输入，使用默认的空字符串输入。")
        return ""

def get_all_functions(directory):
    # ... 此函数无需改动 ...
    all_functions = set()
    directory = os.path.abspath(directory)
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.abspath(os.path.join(root, file))
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read(), filename=filepath)
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                func_tuple = (filepath, node.lineno, node.name)
                                all_functions.add(func_tuple)
                    except UnicodeDecodeError as e:
                        print(f"Skipping {filepath}: {e}")
                    except SyntaxError as e:
                        print(f"Syntax error in {filepath}: {e}")
    return all_functions

def run_handler_with_profile(handler_path, function_name): # 修改：增加了 function_name 参数
    profiler = cProfile.Profile()
    
    # 新增：根据函数名获取定制化的输入
    event_input = get_input_for_function(function_name)
    
    profiler.enable()
    
    spec = importlib.util.spec_from_file_location("handler", handler_path)
    handler = importlib.util.module_from_spec(spec)
    sys.modules["handler"] = handler
    spec.loader.exec_module(handler)
    
    if hasattr(handler, 'handle'):
        # 修改：将获取到的特定输入传递给 handle 函数
        print(f"INFO: 调用 handle 函数，输入为: '{event_input[:100]}...'") # 打印输入的前100个字符
        handler.handle(event_input) 
    else:
        print("ERROR: 在 handler.py 中未找到 'handle' 函数")
    
    profiler.disable()
    
    return profiler

def extract_called_functions(profiler, directory):
    # ... 此函数无需改动 ...
    called_functions = set()
    directory = os.path.abspath(directory)
    ps = pstats.Stats(profiler)
    
    for func in ps.stats:
        filename, line_number, func_name = func
        if not os.path.isabs(filename) and '<' not in filename:
             filename = os.path.abspath(os.path.join(directory, filename))
        else:
             filename = os.path.abspath(filename)

        if filename.startswith(directory):
            called_functions.add((filename, line_number, func_name))
            
    return called_functions

def main(directory):
    directory = os.path.abspath(directory)
    # 新增：从目录路径中提取函数名
    function_name = os.path.basename(directory)

    print(f"--- Analyzing Function: {function_name} | Directory: {directory} ---")

    sys.path.insert(0, directory)
    
    try:
        print("\n[Step 1] Analyzing all defined functions...")
        all_defined_functions = get_all_functions(directory)
        print(f"Total number of defined functions: {len(all_defined_functions)}")
        
        handler_path = os.path.join(directory, 'handler.py')
        if not os.path.isfile(handler_path):
            print(f"ERROR: handler.py not found in {directory}")
            return
        
        print("\n[Step 2] Running handler.py with profiling...")
        # 修改：将 function_name 传递给分析函数
        profiler = run_handler_with_profile(handler_path, function_name)

        print("\n[Step 3] Extracting called functions from profiling data...")
        called_functions = extract_called_functions(profiler, directory)
        print(f"Total number of called functions: {len(called_functions)}")

        sorted_called_functions = sorted(list(called_functions))
        print("\nFirst 50 called functions (or fewer):")
        for func in sorted_called_functions[:50]:
            relative_path = os.path.relpath(func[0], directory)
            print(f"  - {relative_path}:{func[1]} - {func[2]}")
        
        print(f"\nResult: Number of unused functions is {len(all_defined_functions) - len(called_functions)}")

    finally:
        if sys.path and sys.path[0] == directory:
            sys.path.pop(0)
        print(f"--- Analysis for {function_name} finished ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Python functions usage with custom inputs for specific functions.")
    parser.add_argument("directory", help="Path to the main directory containing Python packages and handler.py")
    
    args = parser.parse_args()
    main(args.directory)