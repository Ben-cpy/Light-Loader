import os
import ast
import cProfile
import pstats
import sys
import importlib.util
import json
import argparse

def get_input_for_function(function_name):
    """
    根据函数名称返回特定的输入数据。
    您可以在这里硬编码所有函数的输入。
    """
    print(f"为函数 '{function_name}' 查找特定输入...")

    # 将 Python 字典转换为 JSON 字符串作为输入
    if function_name == "midd-compression":
        input_data = {"url": "http://ipv4.download.thinkbroadband.com/5MB.zip"}
        print(f"找到输入: {input_data}")
        return json.dumps(input_data)
        
    elif function_name == "midd-thumbnailer":
        # 这是一个示例，您需要根据实际情况提供一个可访问的图片URL
        input_data = {"image_url": "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"}
        print(f"找到输入: {input_data}")
        return json.dumps(input_data)

    elif function_name == "midd-video-processing":
        # 这是一个示例，您需要提供一个有效的视频URL
        input_data = {"video_url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"}
        print(f"找到输入: {input_data}")
        return json.dumps(input_data)
        
    # 如果没有找到匹配的函数，则返回一个默认的空输入
    else:
        print("未找到特定输入，使用默认的空输入。")
        return "" # OpenFaaS handler 通常接收字符串或字节流，空字符串是安全的默认值

def get_all_functions(directory):
    all_functions = set()
    directory = os.path.abspath(directory)
    
    for root, _, files in os.walk(directory):
        # 动态将子目录添加到Python路径中，以便正确解析导入
        sys.path.insert(0, root)
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
                    except SyntaxError as e:
                        print(f"Syntax error in {filepath}: {e}")
        # 清理路径，避免影响下一个函数的分析
        sys.path.pop(0)
        
    return all_functions

def run_handler_with_profile(handler_path, function_name):
    profiler = cProfile.Profile()
    
    # 获取此函数的特定输入
    event_input = get_input_for_function(function_name)
    
    # 动态导入 handler.py
    # 将包含 handler.py 的目录添加到 sys.path
    handler_dir = os.path.dirname(handler_path)
    if handler_dir not in sys.path:
        sys.path.insert(0, handler_dir)

    spec = importlib.util.spec_from_file_location("handler", handler_path)
    handler = importlib.util.module_from_spec(spec)
    sys.modules["handler"] = handler
    
    print("开始运行 handler.handle 并进行性能分析...")
    profiler.enable()
    
    spec.loader.exec_module(handler)
    
    # 使用获取到的特定输入调用 handler 函数
    if hasattr(handler, 'handle'):
        handler.handle(event_input)
    else:
        print("错误: 在 handler.py 中没有找到 'handle' 函数")
    
    profiler.disable()
    print("性能分析结束。")
    
    # 恢复 sys.path
    if handler_dir in sys.path:
        sys.path.remove(handler_dir)
        
    return profiler


def extract_called_functions(profiler, directory):
    called_functions = set()
    directory = os.path.abspath(directory)
    ps = pstats.Stats(profiler)
    
    for func in ps.stats:
        # func 的结构是 (filename, line_number, func_name)
        filename, line_number, func_name = func
        
        # pstats 可能会返回相对路径或奇怪的路径，需要进行规范化
        if not os.path.isabs(filename):
            # 尝试在 sys.path 中找到这个文件来获取绝对路径
            for path_dir in sys.path:
                abs_path_candidate = os.path.abspath(os.path.join(path_dir, filename))
                if os.path.exists(abs_path_candidate):
                    filename = abs_path_candidate
                    break
        
        filename = os.path.abspath(filename)

        if filename.startswith(directory):
            called_functions.add((filename, line_number, func_name))
            
    return called_functions

def main(directory):
    # 将目录路径规范化为绝对路径
    directory = os.path.abspath(directory)
    # 从目录路径中提取函数名
    function_name = os.path.basename(directory)

    print(f"\n===== 开始分析函数: {function_name} =====")
    print(f"目标目录: {directory}")

    # 将主函数目录添加到 sys.path 的最前面，确保依赖包能被优先找到
    sys.path.insert(0, directory)

    print("\n步骤 1: 分析所有已定义的函数...")
    all_defined_functions = get_all_functions(directory)
    print(f"已定义的函数总数: {len(all_defined_functions)}")
    
    handler_path = os.path.join(directory, 'handler.py')
    if not os.path.isfile(handler_path):
        print(f"错误: 在目录 {directory} 中未找到 handler.py")
        # 清理路径并退出
        sys.path.pop(0)
        return
    
    print("\n步骤 2: 运行 handler.py 并进行性能分析...")
    profiler = run_handler_with_profile(handler_path, function_name)

    print("\n步骤 3: 从性能分析数据中提取被调用的函数...")
    called_functions = extract_called_functions(profiler, directory)
    print(f"被调用的函数总数: {len(called_functions)}")

    sorted_called_functions = sorted(list(called_functions))
    print("\n被调用的前 50 个函数 (如果总数小于50则显示全部):")
    for func in sorted_called_functions[:50]:
        # 打印相对路径以保持简洁
        relative_path = os.path.relpath(func[0], directory)
        print(f"  - {relative_path}:{func[1]} - {func[2]}")
    
    unused_functions = all_defined_functions - called_functions
    print(f"\n未使用的函数数量: {len(unused_functions)}")
    
    print(f"===== 函数 {function_name} 分析完毕 =====\n")

    # 清理 sys.path，移除刚刚添加的目录
    sys.path.pop(0)

if __name__ == "__main__":
    # 注意：移除了硬编码的 os.chdir()，使脚本更通用
    parser = argparse.ArgumentParser(description="分析本地 OpenFaaS 函数的 Python 代码使用情况。")
    parser.add_argument("directory", help="包含 Python 包和 handler.py 的主函数目录的路径。")
    
    args = parser.parse_args()
    main(args.directory)