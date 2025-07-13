import os
import subprocess
import json
import re
from pathlib import Path

# --- 配置 ---
APP_DIR_NAME = "app7"  # app5
HANDLER_SCRIPT = "handler.py"
# ---

# 获取脚本所在的目录，即项目根目录
project_root = Path(__file__).parent.resolve()
app_dir = project_root / APP_DIR_NAME
handler_path = app_dir / HANDLER_SCRIPT

def run_command(command, cwd, env=None):
    """辅助函数，用于执行 shell 命令并返回输出"""
    print(f"\n[INFO] Running command: `{' '.join(command)}` in `{cwd}`")
    try:
        # 创建一个新的环境字典，继承当前环境
        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            env=process_env
        )
        print("[SUCCESS] Command executed successfully.")
        # print("STDOUT:\n" + result.stdout)
        # if result.stderr:
        #     print("STDERR:\n" + result.stderr)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed with exit code {e.returncode}")
        print("STDOUT:\n" + e.stdout)
        print("STDERR:\n" + e.stderr)
        return None
    except FileNotFoundError:
        print(f"[ERROR] Command not found: {command[0]}. Is it installed and in your PATH?")
        return None


def run_coverage_analysis():
    """
    步骤 1 & 2: 运行 coverage 并生成 JSON 报告
    """
    print("\n" + "="*20 + " Step 1: Running Coverage Analysis " + "="*20)
    
    # 设置 PYTHONPATH 环境变量，让 Python 能找到 app5 下的模块
    env = {"PYTHONPATH": str(app_dir)}

    # 1. 运行 coverage run
    coverage_run_cmd = [
        "coverage", "run",
        f"--source={APP_DIR_NAME}",
        str(handler_path)
    ]
    if run_command(coverage_run_cmd, cwd=project_root, env=env) is None:
        print("[FATAL] Coverage run failed. Aborting.")
        return None

    # 2. 生成 JSON 报告
    coverage_json_cmd = ["coverage", "json", "-o", "coverage_report.json"]
    if run_command(coverage_json_cmd, cwd=project_root) is None:
        print("[FATAL] Coverage JSON report generation failed. Aborting.")
        return None

    # 3. 读取并返回数据
    try:
        with open(project_root / "coverage_report.json", 'r') as f:
            coverage_data = json.load(f)
        print("[INFO] Successfully parsed coverage_report.json")
        return coverage_data['files']
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to read or parse coverage_report.json: {e}")
        return None

def run_strace_analysis():
    """
    步骤 3: 运行 strace 并解析日志
    """
    print("\n" + "="*20 + " Step 2: Running strace Analysis " + "="*20)
    strace_log_path = app_dir / "strace.log"
    
    # 1. 运行 strace
    # 注意：需要以 root 权限或具有 ptrace 能力的用户运行 strace
    # 我们使用 python3，请根据您的环境修改
    strace_cmd = [
        "strace",
        "-e", "trace=open,openat",
        "-o", str(strace_log_path),
        "python3", HANDLER_SCRIPT
    ]
    # 在 app5 目录内执行
    if run_command(strace_cmd, cwd=app_dir) is None:
        print("[FATAL] strace command failed. Aborting. (Did you run as root?)")
        return set()

    # 2. 解析 strace 日志
    opened_files = set()
    # 正则表达式匹配 open/openat 系统调用中成功打开的文件
    # 例: openat(AT_FDCWD, "/usr/lib/python3.10/...", O_RDONLY|O_CLOEXEC) = 3
    # 只关心返回文件描述符 (>= 0) 的成功调用
    pattern = re.compile(r'(?:open|openat)\(.*?,\s*"(.*?)"[^)]*\)\s*=\s*\d+')
    
    try:
        with open(strace_log_path, 'r') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    filepath = match.group(1)
                    # 我们只关心 app5 目录下的 .py 文件
                    # 使用 resolve() 来处理相对路径 '..'
                    abs_path = Path(app_dir / filepath).resolve()
                    if app_dir in abs_path.parents and abs_path.suffix == '.py':
                         # 转换为相对于项目根目录的路径，以便与 coverage 数据匹配
                        relative_path_to_root = abs_path.relative_to(project_root)
                        opened_files.add(str(relative_path_to_root))
        
        print(f"[INFO] Parsed strace.log. Found {len(opened_files)} relevant .py files opened.")
        return opened_files
    except FileNotFoundError:
        print(f"[ERROR] strace.log not found at {strace_log_path}")
        return set()


def analyze_and_report(coverage_files, strace_files):
    """
    步骤 4: 综合分析并生成最终报告
    """
    print("\n" + "="*25 + " Final Analysis Report " + "="*25)
    
    if not coverage_files:
        print("\n[WARNING] No coverage data available. Cannot generate a meaningful report.")
        return

    report_data = []
    total_size = 0
    total_wasted_size = 0
    
    # 新增计数器
    total_modules_analyzed = 0
    unused_modules_count = 0

    for filepath_str, stats in coverage_files.items():
        filepath = Path(filepath_str)
        
        # 跳过 handler 脚本本身
        if filepath == handler_path.relative_to(project_root):
            continue

        summary = stats['summary']
        num_statements = summary['num_statements']
        if num_statements == 0:
            continue
        
        # 计入总模块数
        total_modules_analyzed += 1
            
        covered_lines = summary['covered_lines']
        coverage_percent = covered_lines / num_statements

        try:
            file_size = os.path.getsize(project_root / filepath_str)
        except FileNotFoundError:
            continue

        # 估算浪费的空间
        wasted_size = file_size * (1 - coverage_percent)
        
        total_size += file_size
        total_wasted_size += wasted_size

        # 首先根据 coverage 百分比确定主要分类
        status_category = ""
        if coverage_percent == 0:
            status_category = "Loaded but COMPLETELY UNUSED"
            unused_modules_count += 1 # 计入未使用的模块
        elif coverage_percent < 0.3:
            status_category = "Partially Used (Low)"
        elif coverage_percent < 0.8:
            status_category = "Partially Used (Medium)"
        else:
            status_category = "Heavily Used"
            
        # 添加 strace 是否记录的辅助说明
        strace_note = ""
        if filepath_str not in strace_files:
            strace_note = " (not traced by strace)"
        
        full_status = status_category + strace_note

        report_data.append({
            "path": filepath_str,
            "coverage": coverage_percent,
            "size_kb": file_size / 1024,
            "wasted_kb": wasted_size / 1024,
            "status": full_status,
            "status_category": status_category # 保留分类用于排序和分组
        })

    # 按浪费空间从大到小排序
    report_data.sort(key=lambda x: x['wasted_kb'], reverse=True)

    # 调整列宽以适应更长的状态字符串
    print(f"\n{'Status':<35} | {'Module Path':<50} | {'Coverage':>10} | {'Size (KB)':>12} | {'Wasted (KB)':>14}")
    print("-" * 135) # 调整分隔线长度
    
    # 打印最典型的“未使用”模块
    print("\n--- Modules Loaded but COMPLETELY UNUSED (0% Coverage) ---")
    has_unused_modules = False
    for item in report_data:
        if item['status_category'] == "Loaded but COMPLETELY UNUSED":
            print(f"{item['status']:<35} | {item['path']:<50} | {item['coverage']:>9.1%} | {item['size_kb']:>11.2f} | {item['wasted_kb']:>13.2f}")
            has_unused_modules = True
    if not has_unused_modules:
        print("    None found.")
            
    # 打印其他模块
    print("\n--- Other Modules (sorted by wasted space) ---")
    has_other_modules = False
    for item in report_data:
        if item['status_category'] != "Loaded but COMPLETELY UNUSED":
             print(f"{item['status']:<35} | {item['path']:<50} | {item['coverage']:>9.1%} | {item['size_kb']:>11.2f} | {item['wasted_kb']:>13.2f}")
             has_other_modules = True
    if not has_other_modules and not has_unused_modules: # 如果既没有未使用也没有其他模块（可能只有handler）
        print("    No other modules found.")
    elif not has_other_modules: # 如果有未使用，但没有其他
         print("    None found.")


    print("\n" + "="*30 + " Summary " + "="*30)
    if total_modules_analyzed > 0:
        utilization = (total_size - total_wasted_size) / total_size
        print(f"Total size of analyzed dependencies: {total_size / 1024:.2f} KB")
        print(f"Estimated wasted size (unused code): {total_wasted_size / 1024:.2f} KB")
        print(f"Overall Code Utilization in dependencies: {utilization:.2%}")
        
        print(f"\nTotal modules analyzed: {total_modules_analyzed}")
        print(f"Modules loaded but COMPLETELY UNUSED (0% coverage): {unused_modules_count}")
        if total_modules_analyzed > 0:
            unused_proportion = unused_modules_count / total_modules_analyzed
            print(f"Proportion of unused modules: {unused_proportion:.2%}")
        else:
            print("Proportion of unused modules: N/A (No modules analyzed)")
    else:
        print("No dependency files were analyzed.")


if __name__ == "__main__":
    # 确保依赖已安装
    try:
        import coverage
    except ImportError:
        print("[ERROR] `coverage` is not installed. Please run `pip install coverage`.")
        exit(1)

    # 步骤 1: 运行 Coverage
    coverage_data = run_coverage_analysis()
    
    # 步骤 2: 运行 strace
    strace_opened_files = run_strace_analysis()

    # 步骤 3: 分析和报告
    if coverage_data is not None:
        analyze_and_report(coverage_data, strace_opened_files)
    
    # 清理生成的文件
    print("\n[INFO] Cleaning up generated files...")
    for f in ["coverage_report.json", ".coverage", str(app_dir / "strace.log")]:
        p = project_root / f
        if p.exists():
            p.unlink()