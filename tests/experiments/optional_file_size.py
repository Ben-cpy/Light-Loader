# Select 6 files to show the size of their redundant files.
import os
import shutil

assetsDir = {
    "ignorDir": ["__pycache__", "tests", ".serverless", "pip", "pkg_resources", "setuptools", "wheel", "_distutils_hack", "test"],
    "ignorSpeDir": [".dist-info"],
    "ignorFile": [".pyc", ".pyi", ".pth", ".virtualenv", "_virtualenv.py", ".md"],
}

def get_redundant_size(path, visited):
    redundant_size = 0
    for root, dirs, files in os.walk(path):
        if root in visited:
            continue
        visited.add(root)
        for dir in list(dirs):  # Iterate over a copy to safely modify dirs
            if dir in assetsDir["ignorDir"]:
                redundant_size += get_directory_size(os.path.join(root, dir))
            for dirhouzhui in assetsDir["ignorSpeDir"]:
                if dir.endswith(dirhouzhui):
                    redundant_size += get_directory_size(os.path.join(root, dir))
        for name in files:
            for houzhui in assetsDir["ignorFile"]:
                if name.endswith(houzhui):
                    file_path = os.path.join(root, name)
                    redundant_size += os.path.getsize(file_path)
    return redundant_size


def get_directory_size(path):
    total_size = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
    return total_size


def format_size(size):
    """Format size in MB."""
    return f"{size / (1024 * 1024):.2f} MB"


if __name__ == '__main__':
    directory_paths = ["/home/chenpengyu/openfaas-la/app5", "/home/chenpengyu/openfaas-la/app6", "/home/chenpengyu/openfaas-la/app7","/home/chenpengyu/openfaas-la/app8","/home/chenpengyu/openfaas-la/app10","/home/chenpengyu/openfaas-la/marshal", "/home/chenpengyu/openfaas-la/pdfminer"]  
    total_redundant_size = 0
    total_directory_size = 0
    visited = set()
    for path in directory_paths:
        redundant_size = get_redundant_size(path, visited)
        directory_size = get_directory_size(path)  
        total_redundant_size += redundant_size
        total_directory_size += directory_size
        print(f"Directory: {path}")
        print(f"Redundant size: {format_size(redundant_size)}")
        print(f"Total size (after removing redundant files): {format_size(directory_size)}")

    if total_directory_size > 0:
        proportion = (total_redundant_size / total_directory_size) * 100
        print("\nOverall:")
        print(f"Total redundant size: {format_size(total_redundant_size)}")
        print(f"Total directory size: {format_size(total_directory_size)}")
        print(f"Proportion of redundant files: {proportion:.2f}%")
    else:
        print("\nOverall: Total directory size is zero.")

