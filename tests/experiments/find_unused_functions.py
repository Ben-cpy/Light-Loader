import os
import ast
import cProfile
import pstats
import sys
import importlib.util

def get_all_functions(directory):
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
                    except SyntaxError as e:
                        print(f"Syntax error in {filepath}: {e}")
        
    return all_functions

# def run_handler_with_profile(handler_path):
#     profiler = cProfile.Profile()
#     profiler.enable()
    
#     # Dynamically import handler.py and execute it
#     spec = importlib.util.spec_from_file_location("handler", handler_path)
#     handler = importlib.util.module_from_spec(spec)
#     sys.modules["handler"] = handler
#     spec.loader.exec_module(handler)
    
#     profiler.disable()
    
#     return profiler

def run_handler_with_profile(handler_path):
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Dynamically import handler.py
    spec = importlib.util.spec_from_file_location("handler", handler_path)
    handler = importlib.util.module_from_spec(spec)
    sys.modules["handler"] = handler
    spec.loader.exec_module(handler)
    
    # Call the handler function
    if hasattr(handler, 'handle'):
        handler.handle()
    else:
        print("No 'handle' function found in handler.py")
    
    profiler.disable()
    
    return profiler


def extract_called_functions(profiler, directory):
    called_functions = set()
    directory = os.path.abspath(directory)
    ps = pstats.Stats(profiler)
    
    for func in ps.stats:
        filename, line_number, func_name = func
        filename = os.path.abspath(filename)
        if filename.startswith(directory):
            called_functions.add((filename, line_number, func_name))
    return called_functions

def main(directory):
    directory = os.path.abspath(directory)
    print("Analyzing all defined functions...")
    all_defined_functions = get_all_functions(directory)
    print(f"Total number of defined functions: {len(all_defined_functions)}")
    
    handler_path = os.path.join(directory, 'handler.py')
    if not os.path.isfile(handler_path):
        print(f"handler.py not found in {directory}")
        return
    
    print("Running handler.py with profiling...")
    profiler = run_handler_with_profile(handler_path)
    print("Extracting called functions from profiling data...")
    called_functions = extract_called_functions(profiler, directory)
    print(f"Total number of called functions: {len(called_functions)}")

    sorted_called_functions = sorted(list(called_functions))
    print("\nFirst 30 called functions (or fewer if there are less than 30):")
    for func in sorted_called_functions[:50]:
        print(f"{func[0]}:{func[1]} - {func[2]}")
    
    # unused_functions = all_defined_functions - called_functions
    print(f"Number of unused functions: {len(all_defined_functions) - len(called_functions)}")
    
    # if unused_functions:
    #     print("\nUnused functions:")
    #     for func in sorted(unused_functions):
    #         print(f"{func[0]}:{func[1]} - {func[2]}")
    # else:
    #     print("All functions were used.")

if __name__ == "__main__":
    import argparse
    # Change cwd into /home/chenpengyu/openfaas-la/app5
    os.chdir("/home/chenpengyu/openfaas-la/app5")
    parser = argparse.ArgumentParser(description="Analyze Python functions usage.")
    parser.add_argument("directory", help="Path to the main directory containing Python packages and handler.py")
    
    args = parser.parse_args()
    main(args.directory)
