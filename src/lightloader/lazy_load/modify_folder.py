# change the folder's package file to lazy load pattern
import os
import shutil
from . import post_package

copy_dir = '/home/app/copy' # would containing error after the first lazy load

current_dir = os.path.dirname(os.path.abspath(__file__))
# read the special file
target_file_path = os.path.join(current_dir, 'special_file.txt')
ignore_file = ['__init__.py', 'six.py','certs.py','_npyio_impl.py']
target_folder = ['pandas.core','numpy.core','skimage.segmentation','numpy._core']

def should_skip_folder(path, target_folders):
    path_parts = path.split(os.sep)
    return any(all(part in path_parts for part in folder.split('.')) for folder in target_folders)

def should_skip_file(file_path, name_lists, relative_path_list):
    file_name = os.path.basename(file_path)
    if file_name in name_lists:
        return True
    
    relative_path = os.path.relpath(file_path, copy_dir)
    relative_path_without_ext = os.path.splitext(relative_path)[0].replace(os.sep, '.')
    return any(relative_path_without_ext == target for target in relative_path_list)

def read_target_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def lazy_load_the_folder(package_path):
    shutil.copytree(package_path, copy_dir)
    target_file = read_target_file(target_file_path)

    for subdir, dirs, files in os.walk(copy_dir):
        # Skip processing if the current subdirectory is in target_folder
        if should_skip_folder(subdir, target_folder):
            dirs[:] = []  # Clear dirs to prevent further recursion into this folder
            continue

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(subdir, file)
                
                if should_skip_file(file_path, ignore_file, target_file):
                    print(f"Skipped file: {file_path}")
                    continue

                try:
                    with open(file_path, 'r') as f:
                        source_code = f.read()
                    
                    modified_code = post_package.transform_code(source_code)

                    with open(file_path, 'w') as f:
                        f.write(modified_code)
                        
                    print(f"Processed and modified: {file_path}")
                except Exception as e:
                    print(f"Error processing file: {file_path}")
                    print(f"Error message: {str(e)}")
