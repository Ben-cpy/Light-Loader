import os
import sys
import ast
import subprocess
import re
import shutil

from . import generate_input

def repair_folder(modified_folder_path, original_folder_path): #"/home/app/copy", "/home/app/python"
    generate_input.generate_user_input("/home/app/function/handler.py", "/home/app/copy/handler_copy.py")
    run_and_fix_folder("/home/app/copy/handler_copy.py",modified_folder_path, original_folder_path)

def extract_imports(code) -> list:
    tree = ast.parse(code)
    
    import_nodes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_nodes.append(node)
    
    return import_nodes
def extract_import_names(file_path: str) -> list:
    with open(file_path, 'r') as file:
        source_code = file.read()

    import_names = []
    import_names.extend(extract_imports(source_code))
    return import_names

def create_import_file(import_nodes, file_path):
    with open(file_path, 'w') as file:
        for node in import_nodes:
            file.write(ast.unparse(node) + '\n')

def run_and_fix_folder(copyed_import_file_path,modified_folder_path, original_folder_path):
    cnt = 1
    recover_stack = []
    other_error_info = None # for other error, identify whether is the same error
    error_counter = {
        "NameError": 0,
        "ImportError": 0,
        "AttributeError": 0,
        "OtherError": 0
    }
    while True:
        cnt += 1
        if cnt > 500 :
            break
        try:
            # Run Python file
            result = subprocess.run(['python', copyed_import_file_path], check=True, text=True, capture_output=True,cwd=modified_folder_path)
            print(error_counter)
            break  # Exit the loop if no error occurred
        except subprocess.CalledProcessError as e:
            # Output exception information
            if "NameError" in e.stderr:
                """
                e.g.
"/home/chenpengyu/lazy_import/output/pdfminer/cryptography/hazmat/primitives/ciphers/base.py", line 109, in <module>
    CipherContext.register(rust_openssl.ciphers.CipherContext)
NameError: name 'rust_openssl' is not defined
                expected output
                1.import_name: rust_openssl
                2.error_file(choose the closest one): /home/chenpengyu/lazy_import/output/pdfminer/cryptography/hazmat/primitives/ciphers/base.py
                """     
                error_counter["NameError"] += 1
                recover_stack.clear()
                print("Name Error:")
                print(e.stderr)
                key_info_of_error = extract_from_name_error(e.stderr)
                repair_name_error(key_info_of_error,modified_folder_path,original_folder_path)
                
            elif "ImportError" in e.stderr:
                """
                e.g.
ImportError: cannot import name 'HTTPException' from 'urllib3.connection' (/home/chenpengyu/lazy_import/output/app5/urllib3/connection.py)
                expected output
                1.import_name: HTTPException
                2.import_from: urllib3.connection
                3.error_file: /home/chenpengyu/lazy_import/output/app5/urllib3/connection.py
                """
                error_counter["ImportError"] += 1
                print("Import Error:")
                print(e.stderr)
                recover_stack.clear()
                key_info_of_error = extract_from_import_error(e.stderr)
                repair_import_error(key_info_of_error,modified_folder_path,original_folder_path)
            
            elif "AttributeError" in e.stderr:
                print("Attribute Error:")
                print(e.stderr)
                error_counter["AttributeError"] += 1
                recover_stack.clear()
                key_info_of_error = extract_from_special_attribute_error(e.stderr)
                repair_special_attribute_error(key_info_of_error,modified_folder_path,original_folder_path)
            else: # other error, recover the error file
                # AttributeError
                error_counter["OtherError"] += 1
                
                print("Other Error")
                print(e.stderr)

                key_info_of_error = extract_from_other_error(e.stderr)
                error_msg = key_info_of_error["error_message"]
                
                if len(recover_stack) <= 0:  
                    # first time
                    recover_stack = key_info_of_error["file_paths"]

                if other_error_info == error_msg: 
                    reach_bottom = recover_error_file(recover_stack[-1],modified_folder_path,original_folder_path)
                    # reach the stack bottom, and the error is still not fixed
                    if reach_bottom == -1 and "AttributeError" in e.stderr:
                        # fixing method like `import error`
                        key_info_of_error = extract_from_special_attribute_error(e.stderr)
                        repair_special_attribute_error(key_info_of_error,modified_folder_path,original_folder_path)
                else: # new error type,update the stack and error info
                    recover_stack = key_info_of_error["file_paths"]
                    recover_error_file(recover_stack[-1],modified_folder_path,original_folder_path)
                    other_error_info = key_info_of_error["error_message"]

                recover_stack.pop()

def extract_from_name_error(error_message: str) -> dict:
    """
    Extract relevant information from a complete NameError traceback.
    
    Returns:
        dict: A dictionary containing the extracted information.
    """
    result = {
        "undefined_name": None,
        "file_paths": [],
        "line_numbers": []
    }
    
    lines = error_message.strip().split('\n')
    
    # Extract NameError details
    name_error_line = next((line for line in lines if line.startswith('NameError:')), None)
    if name_error_line:
        name_match = re.search(r"name '(\w+)' is not defined", name_error_line)
        if name_match:
            result["undefined_name"] = name_match.group(1)
    
    # Extract all file paths and line numbers from the traceback
    for line in lines:
        file_match = re.search(r'File "(.+)", line (\d+)', line)
        if file_match:
            result["file_paths"].append(file_match.group(1))
            result["line_numbers"].append(int(file_match.group(2)))
    
    return result

def insert_absent_package(error_file_path: str, absent_import_node: ast.AST) -> None:
    with open(error_file_path, 'r') as file:
        source_code = file.read()

    tree = ast.parse(source_code)
    
    # Check for __future__ imports
    future_import_index = -1
    for i, node in enumerate(tree.body):
        if isinstance(node, ast.ImportFrom) and node.module == '__future__':
            future_import_index = i
            break
    
    # Convert the absent_import_node to a string
    import_statement = ast.unparse(absent_import_node)
    
    if future_import_index != -1:
        # Insert after the last __future__ import
        insert_position = tree.body[future_import_index].end_lineno
        lines = source_code.splitlines()
        lines.insert(insert_position, import_statement)
        modified_content = '\n'.join(lines)
    else:
        # Insert at the beginning of the file
        modified_content = import_statement + '\n' + source_code
    
    with open(error_file_path, 'w') as file:
        file.write(modified_content)

    print(f"Added import to {error_file_path}")

def repair_name_error(key_info_of_error, modified_folder_path, original_folder_path):
    error_file_path = key_info_of_error["file_paths"][-1]
    relative_path = os.path.relpath(error_file_path, modified_folder_path)
    original_file_path = os.path.join(original_folder_path, relative_path)

    with open(original_file_path, 'r') as file:
        source_code = file.read()
    
    undefined_name = key_info_of_error["undefined_name"]
    absent_import_node = find_import_node_by_name(source_code, undefined_name)
    
    if absent_import_node:
        insert_absent_package(error_file_path, absent_import_node)
    else:
        print(f"Import for {undefined_name} not found in the original file.")

# Reuse the existing find_import_node_by_name function
def extract_from_import_error(error_message: str) -> dict:
    """
    Extract relevant information from a complete ImportError traceback.
    
    Returns:
        dict: A dictionary containing the extracted information.
    """
    result = {
        "import_name": None,
        "import_from": None,
        "error_file": None,
    }
    
    lines = error_message.strip().split('\n')
    
    # Extract import error details
    import_error_line = next((line for line in reversed(lines) if line.startswith('ImportError:')), None)
    if import_error_line:
        import_match = re.search(r"cannot import name '(\w+)' from '([\w\.]+)'", import_error_line)
        if import_match:
            result["import_name"] = import_match.group(1)
            result["import_from"] = import_match.group(2)
        
        file_match = re.search(r"\((.+?)\)", import_error_line)
        if file_match:
            result["error_file"] = file_match.group(1)
    return result

def repair_import_error(key_info_of_error, modified_folder_path,original_folder_path):
    error_file_path = key_info_of_error["error_file"]
    relative_path = os.path.relpath(error_file_path, modified_folder_path)
    original_file_path = os.path.join(original_folder_path, relative_path)

    with open(original_file_path, 'r') as file:
        source_code = file.read()
    absent_import_node = find_import_node_by_name(source_code, key_info_of_error["import_name"])
    
    if absent_import_node:
        insert_absent_package(error_file_path, absent_import_node)
    else:
        print(f"Import for {key_info_of_error['import_name']} not found in the original file.")
        
def find_import_node_by_name(source_code, import_name):
    tree = ast.parse(source_code)
    
    wildcard_nodes = []
    
    # first traversal: find exact match
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # check 'from x import y' and 'from x import y as z'
            for alias in node.names:
                if alias.name == import_name or alias.asname == import_name:
                    return node
            # collect wildcard imports
            if any(alias.name == '*' for alias in node.names):
                wildcard_nodes.append(node)
        elif isinstance(node, ast.Import):
            # check 'import x' and 'import x as y'
            for alias in node.names:
                if alias.name == import_name or alias.asname == import_name:
                    return node
                # check if it's a submodule import
                if alias.name.startswith(import_name + '.'):
                    return node
    
    # second traversal: handle wildcard imports
    for node in wildcard_nodes:
        # due to complexity, simplified to not return here
        pass  # you can add specific check logic here
    
    # if no exact match, return partial match
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and import_name.startswith(node.module + '.'):
                return node
    
    return None

def extract_from_other_error(error_message: str) -> dict:
    result = {
        "error_type": None,
        "file_paths": [],
        "error_message": None
    }
    
    lines = error_message.strip().split('\n')
    
    error_line = lines[-1]
    error_match = re.match(r"(\w+Error): (.+)", error_line)
    if error_match:
        result["error_type"] = error_match.group(1)
        result["error_message"] = error_match.group(2)
    
    # Extract file paths from the traceback
    for line in lines:
        file_match = re.search(r'File "(.+)", line', line)
        if file_match:
            result["file_paths"].append(file_match.group(1))
    
    return result

# recover the single file
def recover_error_file(error_file_path, modified_folder_path,original_folder_path):
    relative_path = os.path.relpath(error_file_path, modified_folder_path)
    original_file_path = os.path.join(original_folder_path, relative_path)
    # judge whether original_file_path exist
    if not os.path.exists(original_file_path):
        return -1  # not exist
    # read from the origin, and write to the error_file_path
    with open(original_file_path, 'r') as file:
        source_code = file.read()
    with open(error_file_path, 'w') as file:
        file.write(source_code)

def extract_from_special_attribute_error(error_message: str) -> dict:
    result = {
        "module_name": None,
        "attribute_name": None,
        "error_file": None
    }
    
    lines = error_message.strip().split('\n')
    
    attr_error_line = next((line for line in reversed(lines) if line.startswith('AttributeError:')), None)
    if attr_error_line:
        # use non-greedy match to capture the module and attribute names
        attr_match = re.search(r"module '(.+?)' has no attribute '(.+?)'", attr_error_line)
        if attr_match:
            result["module_name"] = attr_match.group(1)
            result["attribute_name"] = attr_match.group(2)
        else:
            # Handle the new pattern
            attr_match = re.search(r"'(.+?)' object has no attribute '(.+?)'", attr_error_line)
            if attr_match:
                result["module_name"] = attr_match.group(1)
                result["attribute_name"] = attr_match.group(2)
    
    for line in reversed(lines):
        if line.strip().startswith('File '):
            file_match = re.search(r'File "(.+?)"', line)
            if file_match:
                result["error_file"] = file_match.group(1)
                break
    
    return result

def repair_special_attribute_error(key_info_of_error, modified_folder_path, original_folder_path):
    module_name = key_info_of_error["module_name"]
    attribute_name = key_info_of_error["attribute_name"]
    
    # Convert module name to file path
    module_path = module_name.replace('.', os.path.sep) + '.py'
    
    # Construct paths for both modified and original files
    modified_file_path = os.path.join(modified_folder_path, module_path)
    original_file_path = os.path.join(original_folder_path, module_path)
    
    # Ensure the original file exists
    if not os.path.exists(original_file_path):
        print(f"Original file not found: {original_file_path}")
        return
    
    # Read the original file content
    with open(original_file_path, 'r') as file:
        source_code = file.read()
    
    # Find the import node for the attribute
    absent_import_node = find_import_node_by_name(source_code, attribute_name)
    
    if absent_import_node:
        # Insert the absent import into the modified file
        insert_absent_package(modified_file_path, absent_import_node)
        print(f"Added import for {attribute_name} to {modified_file_path}")
    else:
        print(f"Import for {attribute_name} not found in the original file: {original_file_path}")
