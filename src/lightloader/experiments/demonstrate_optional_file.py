"""
统计所有无关文件占整个项目的大小.
"""


import os

def get_directory_size(directory):
    """
    递归计算目录的总大小（包括所有子目录和文件）。
    """
    total = 0
    for root, dirs, files in os.walk(directory):
        for f in files:
            fp = os.path.join(root, f)
            try:
                if os.path.islink(fp):
                    continue  # 跳过符号链接
                total += os.path.getsize(fp)
            except OSError as e:
                print(f"无法访问文件: {fp}. 错误: {e}")
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
        # 检查当前目录是否在忽略目录列表中
        current_dir = os.path.basename(root)
        dir_matched = False
        if current_dir in ignor_dir or any(spe in current_dir for spe in ignor_spe_dir):
            dir_size = get_directory_size(root)
            relevant_size += dir_size
            total_size += dir_size
            dir_matched = True
            # 不再遍历这个目录下的子目录和文件
            dirs[:] = []
            continue

        # 过滤掉需要忽略的子目录，避免进一步遍历
        dirs_to_remove = []
        for d in dirs:
            if d in ignor_dir or any(spe in d for spe in ignor_spe_dir):
                dir_path = os.path.join(root, d)
                dir_size = get_directory_size(dir_path)
                relevant_size += dir_size
                total_size += dir_size
                dirs_to_remove.append(d)
        # 从 dirs 中移除已处理的目录
        dirs[:] = [d for d in dirs if d not in dirs_to_remove]

        # 处理文件
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if os.path.islink(file_path):
                    continue  # 跳过符号链接
                file_size = os.path.getsize(file_path)
                total_size += file_size
                if any(file.endswith(ext) for ext in ignor_file):
                    relevant_size += file_size
            except OSError as e:
                print(f"无法访问文件: {file_path}. 错误: {e}")

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
    print(f"目录总大小: {total_size / (1024 * 1024):.2f} MB")
    print(f"匹配的文件和目录总大小: {relevant_size / (1024 * 1024):.2f} MB")
    print(f"匹配项占目录总大小的比例: {percentage:.2f}%")

if __name__ == "__main__":
    target_directory = input("请输入目录路径: ").strip()
    if os.path.isdir(target_directory):
        main(target_directory)
    else:
        print("请输入一个有效的目录路径。")
