

import os
import ast
import cProfile
import pstats
import sys
import importlib.util
import argparse
import json  # New: Import json library to handle JSON input

def get_input_for_function(function_name):
    """
    Return specific, pre-built input data based on function name.
    This is the configuration center for all special inputs.
    """
    print(f"INFO: Finding specific input for function '{function_name}'...")

    # Provide specific input for midd-uploader
    if function_name == "midd-uploader":
        # Note: The input you provided looks more like compression or download tasks, but following your requirements to use for uploader
        input_data = {"url": "http://ipv4.download.thinkbroadband.com/5MB.zip"}
        json_input = json.dumps(input_data)
        print(f"INFO: Found specific input: {json_input}")
        return json_input

    # Provide specific input for midd-graph-pagerank
    elif function_name == "midd-graph-pagerank":
        input_data = {"size": 10000, "seed": 42}
        json_input = json.dumps(input_data)
        print(f"INFO: Found specific input: {json_input}")
        return json_input

    elif function_name == "midd-compression":
        input_data = {"num_files": 10, "file_size_kb": 128}
        json_input = json.dumps(input_data)
        print(f"INFO: Found specific input: {json_input}")
        return json_input    
    
    elif function_name == "midd-dynamic-html":
        input_data = {"username": "Alex", "random_len": 10}
        json_input = json.dumps(input_data)
        print(f"INFO: Found specific input: {json_input}")
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
        print(f"INFO: Found specific input: {json_input}")
        return json_input    
    
    elif function_name == "midd-video-processing":
        input_data = {"filename": "cat.jpg", "width": 150, "height": 150}
        json_input = json.dumps(input_data)
        print(f"INFO: Found specific input: {json_input}")
        return json_input     
    # You can add more elif conditions here to support other functions
    # elif function_name == "another-function":
    #     return '{"key": "some_other_value"}'

    # If no matching function is found, return a default empty string input
    else:
        print("INFO: No specific input found, using default empty string input.")
        return ""

def get_all_functions(directory):
    # ... This function needs no modification ...
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

def run_handler_with_profile(handler_path, function_name): # Modified: Added function_name parameter
    profiler = cProfile.Profile()

    # New: Get customized input based on function name
    event_input = get_input_for_function(function_name)

    profiler.enable()

    spec = importlib.util.spec_from_file_location("handler", handler_path)
    handler = importlib.util.module_from_spec(spec)
    sys.modules["handler"] = handler
    spec.loader.exec_module(handler)

    if hasattr(handler, 'handle'):
        # Modified: Pass the obtained specific input to handle function
        print(f"INFO: Calling handle function with input: '{event_input[:100]}...'") # Print first 100 characters of input
        handler.handle(event_input)
    else:
        print("ERROR: 'handle' function not found in handler.py")

    profiler.disable()

    return profiler

def extract_called_functions(profiler, directory):
    # ... This function needs no modification ...
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
    # New: Extract function name from directory path
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
        # Modified: Pass function_name to analysis function
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