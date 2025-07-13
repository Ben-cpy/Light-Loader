import os
import ast
import coverage
import importlib.util
import sys
import timeit
import shutil

class RemoveUnusedFunctions(ast.NodeTransformer):
    def __init__(self, unused_functions):
        super().__init__()
        self.unused_functions = unused_functions
    
    def visit_FunctionDef(self, node):
        func_key = (node.lineno, node.name)
        if func_key in self.unused_functions:
            return None  # Remove function
        return node
    
    def visit_AsyncFunctionDef(self, node):
        func_key = (node.lineno, node.name)
        if func_key in self.unused_functions:
            return None  # Remove function
        return node

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

def get_covered_functions(cov, directory):
    covered_functions = set()
    directory = os.path.abspath(directory)
    for file in cov.get_data().measured_files():
        if file.startswith(directory):
            with open(file, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read(), filename=file)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            # Get the line number of the function definition
                            func_line = node.lineno
                            # Check if the line is covered
                            analysis = cov.analysis(file)
                            executed_lines = analysis[1]
                            if func_line in executed_lines:
                                covered_functions.add((file, func_line, node.name))
                except SyntaxError as e:
                    print(f"Syntax error in {file}: {e}")
    return covered_functions

def measure_import_time(module_path):
    setup_code = f"""
import sys
import importlib.util

spec = importlib.util.spec_from_file_location("handler", "{module_path}")
handler = importlib.util.module_from_spec(spec)
sys.modules["handler"] = handler
"""
    test_code = """
spec.loader.exec_module(handler)
"""
    time = timeit.timeit(stmt=test_code, setup=setup_code, number=1)
    return time

def remove_unused_functions_from_file(filepath, unused_functions):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    tree = ast.parse(source, filename=filepath)
    transformer = RemoveUnusedFunctions(unused_functions)
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    
    new_source = ast.unparse(new_tree)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_source)

def main(directory):
    directory = os.path.abspath(directory)
    print("Analyzing all defined functions...")
    all_defined_functions = get_all_functions(directory)
    print(f"Total number of defined functions: {len(all_defined_functions)}")
    
    # Start coverage
    cov = coverage.Coverage(source=[directory])
    cov.start()
    
    # Import and run handler
    handler_path = os.path.join(directory, 'handler.py')
    if not os.path.isfile(handler_path):
        print(f"handler.py not found in {directory}")
        return
    
    spec = importlib.util.spec_from_file_location("handler", handler_path)
    handler = importlib.util.module_from_spec(spec)
    sys.modules["handler"] = handler
    spec.loader.exec_module(handler)
    
    if hasattr(handler, 'handle'):
        handler.handle()
    else:
        print("No 'handle' function found in handler.py")
    
    # Stop coverage
    cov.stop()
    cov.save()
    
    print("Extracting covered functions from coverage data...")
    covered_functions = get_covered_functions(cov, directory)
    print(f"Total number of covered functions: {len(covered_functions)}")
    
    unused_functions = all_defined_functions - covered_functions
    print(f"Number of unused functions: {len(unused_functions)}")
    
    if unused_functions:
        print("\nUnused functions:")
        for func in sorted(unused_functions):
            print(f"{func[0]}:{func[1]} - {func[2]}")
        
        # Copy codebase to optimized directory
        optimized_dir = directory + "_optimized"
        if os.path.exists(optimized_dir):
            shutil.rmtree(optimized_dir)
        shutil.copytree(directory, optimized_dir)
        print(f"Copied original code to {optimized_dir}. Removing unused functions...")
        
        # Remove unused functions
        for filepath, lineno, func_name in unused_functions:
            remove_unused_functions_from_file(filepath, [(lineno, func_name)])
            print(f"Removed {func_name} from {filepath}")
        
        # Measure import time
        original_handler = handler_path
        optimized_handler = os.path.join(optimized_dir, 'handler.py')
        
        original_time = measure_import_time(original_handler)
        optimized_time = measure_import_time(optimized_handler)
        
        print(f"\nImport time (original): {original_time:.6f} seconds")
        print(f"Import time (optimized): {optimized_time:.6f} seconds")
        print(f"Time difference: {original_time - optimized_time:.6f} seconds")
    else:
        print("All functions are used. No optimization needed.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze Python functions usage with coverage and measure compile time impact.")
    parser.add_argument("directory", help="Path to the main directory containing Python packages and handler.py")
    
    args = parser.parse_args()
    main(args.directory)
