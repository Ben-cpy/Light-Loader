"""
Statistics of all irrelevant files occupying the project size.
"""


import os

def get_directory_size(directory):
    """
    Recursively calculate the total size of the directory including all subdirectories and files.
    """
    total = 0
    for root, dirs, files in os.walk(directory):
        for f in files:
            fp = os.path.join(root, f)
            try:
                if os.path.islink(fp):
                    continue  # skip symbolic links
                total += os.path.getsize(fp)
            except OSError as e:
                print(f"Cannot access file: {fp}. Error: {e}")
    return total

def calculate_size(directory, ignor_dir=None, ignor_spe_dir=None, ignor_file=None):
    if ignor_dir is None:
        ignor_dir = ["__pycache__", "tests", ".serverless", "pip", "pkg_resources", "setuptools", "wheel", "_distutils_hack"]
    if ignor_spe_dir is None:
        ignor_spe_dir = [".dist-info"]
    if ignor_file is None:
        ignor_file = [".pyc", ".pyi", ".pth", ".virtualenv", "_virtualenv.py", ".md"]

    total_size = 0
    relevant_size = 0

    for root, dirs, files in os.walk(directory):
        # Check if current directory is in ignore list
        current_dir = os.path.basename(root)
        dir_matched = False
        if current_dir in ignor_dir or any(spe in current_dir for spe in ignor_spe_dir):
            dir_size = get_directory_size(root)
            relevant_size += dir_size
            total_size += dir_size
            dir_matched = True
            # Stop traversing subdirectories and files in this directory
            dirs[:] = []
            continue

        # Filter out directories to ignore to avoid further traversal
        dirs_to_remove = []
        for d in dirs:
            if d in ignor_dir or any(spe in d for spe in ignor_spe_dir):
                dir_path = os.path.join(root, d)
                dir_size = get_directory_size(dir_path)
                relevant_size += dir_size
                total_size += dir_size
                dirs_to_remove.append(d)
        # Remove processed directories from dirs
        dirs[:] = [d for d in dirs if d not in dirs_to_remove]

        # 处理文件
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if os.path.islink(file_path):
                    continue  # skip symbolic links
                file_size = os.path.getsize(file_path)
                total_size += file_size
                if any(file.endswith(ext) for ext in ignor_file):
                    relevant_size += file_size
            except OSError as e:
                print(f"Cannot access file: {file_path}. Error: {e}")

    # 计算相关大小占比
    if total_size == 0:
        percentage = 0
    else:
        percentage = (relevant_size / total_size) * 100

    return relevant_size, total_size, percentage

def main(directory):
    ignor_dir = ["__pycache__", "tests", ".serverless", "pip", "pkg_resources", "setuptools", "wheel", "_distutils_hack"]
    ignor_spe_dir = [".dist-info"]
    ignor_file = [".pyc", ".pyi", ".pth", ".virtualenv", "_virtualenv.py", ".md"]

    relevant_size, total_size, percentage = calculate_size(
        directory,
        ignor_dir=ignor_dir,
        ignor_spe_dir=ignor_spe_dir,
        ignor_file=ignor_file
    )
    print(f"Total directory size: {total_size / (1024 * 1024):.2f} MB")
    print(f"Total size of matched files and directories: {relevant_size / (1024 * 1024):.2f} MB")
    print(f"Proportion of matched items in total directory size: {percentage:.2f}%")

if __name__ == "__main__":
    target_directory = input("Please enter directory path: ").strip()
    if os.path.isdir(target_directory):
        main(target_directory)
    else:
        print("Please enter a valid directory path.")
