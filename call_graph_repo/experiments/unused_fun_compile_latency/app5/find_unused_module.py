# import sys
# import importlib
# import os

# def main():
#     # --- 步骤 1：统计导入阶段新增的第三方模块 ---
#     initial_modules = set(sys.modules.keys())
    
#     # 用户代码中的导入
#     import requests
#     from lxml import html
    
#     # 强制加载模块，确保捕捉所有依赖模块
#     importlib.import_module('requests')
#     importlib.import_module('lxml')

#     # 获取当前脚本的目录
#     current_dir = os.path.dirname(os.path.abspath(__file__))

#     # 获取新增模块
#     new_modules = set(sys.modules.keys()) - initial_modules
#     third_party = set()

#     for name in new_modules:
#         module = sys.modules.get(name)
#         if module and hasattr(module, '__file__') and module.__file__:
#             module_path = module.__file__
            
#             # 如果模块路径位于当前脚本所在目录
#             if os.path.commonpath([current_dir, os.path.abspath(module_path)]) == current_dir:
#                 third_party.add(name)

#     print(f"[Import阶段] 新增第三方模块: {len(third_party)}")
#     print("模块列表:", third_party)
    
#     # --- 步骤 2：跟踪 handle() 中的模块使用情况 ---
#     def handle():
#         url = "https://www.baidu.com/"
#         response = requests.request("GET", url)
#         tree = html.fromstring(response.content)
#         return 'latency is ...ms'
    
#     called_modules = set()
    
#     def trace_calls(frame, event, arg):
#         if event == 'call':
#             # 获取被调用函数的模块
#             module_name = frame.f_globals.get('__name__')
#             if module_name:
#                 called_modules.add(module_name)
#         return trace_calls
    
#     sys.settrace(trace_calls)
#     try:
#         handle()
#     finally:
#         sys.settrace(None)
    
#     # 计算交集
#     used = third_party & called_modules
#     print(f"[handle()阶段] 实际使用模块: {len(used)}")
#     print("模块列表:", used)
    
#     # 防止 ZeroDivisionError
#     if len(third_party) > 0:
#         print(f"占比: {len(used)/len(third_party):.2%}")
#     else:
#         print("占比: 0% (没有新增第三方模块)")

# if __name__ == "__main__":
#     main()


import sys
import importlib
import os

def main():
    # --- 步骤 1：统计导入阶段新增的第三方模块 ---
    initial_modules = set(sys.modules.keys())
    
    # 用户代码中的导入
    import requests
    from lxml import html
    
    # 强制加载模块，确保捕捉所有依赖模块
    importlib.import_module('requests')
    importlib.import_module('lxml')

    # 获取当前脚本的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 获取新增模块
    new_modules = set(sys.modules.keys()) - initial_modules
    third_party = set()

    for name in new_modules:
        module = sys.modules.get(name)
        if module and hasattr(module, '__file__') and module.__file__:
            module_path = module.__file__
            
            # 如果模块路径位于当前脚本所在目录
            if os.path.commonpath([current_dir, os.path.abspath(module_path)]) == current_dir:
                third_party.add(name)

    print(f"[Import阶段] 新增第三方模块: {len(third_party)}")
    print("模块列表:", third_party)
    
    # --- 步骤 2：跟踪 handle() 中的模块使用情况 ---
    def handle():
        url = "https://www.baidu.com/"
        response = requests.request("GET", url)
        tree = html.fromstring(response.content)
        return 'latency is ...ms'
    
    called_modules = set()
    
    def trace_calls(frame, event, arg):
        if event == 'call':
            # 获取被调用函数的模块
            module_name = frame.f_globals.get('__name__')
            if module_name:
                called_modules.add(module_name)
        return trace_calls
    
    sys.settrace(trace_calls)
    try:
        handle()
    finally:
        sys.settrace(None)
    
    # 去除重复的子模块
    root_modules = {'requests', 'lxml'}
    filtered_third_party = {mod for mod in third_party if not any(mod.startswith(root) for root in root_modules)}
    
    # 计算交集
    used = filtered_third_party & called_modules
    print(f"[handle()阶段] 实际使用模块: {len(used)}")
    print("模块列表:", used)
    
    # 防止 ZeroDivisionError
    if len(filtered_third_party) > 0:
        print(f"占比: {len(used)/len(filtered_third_party):.2%}")
    else:
        print("占比: 0% (没有新增第三方模块)")

if __name__ == "__main__":
    main()
