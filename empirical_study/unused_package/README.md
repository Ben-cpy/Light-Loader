放在openfaas-la 目录下, 指定函数运行即可
统计package level module 初始化情况


当然，非常乐意为您详细讲解这个脚本的逻辑、设计思路以及相关工具的对比。
脚本核心逻辑讲解
这个脚本的设计思路是模拟并监控您应用在真实冷启动时发生的一切，然后通过两层过滤（文件访问层和代码执行层）来精确识别“浪费”。
1. 两层监控体系 (strace + coverage)
我们为什么要用两个工具，而不是一个？因为它们回答了两个不同但互补的问题：
strace (文件访问层): 回答 “哪些模块文件被Python解释器尝试打开并读取了？”
当您 import requests 时，Python会根据其搜索路径查找 requests 包。它会打开 requests/__init__.py。这个 __init__.py 文件又会 import 其他模块，Python会继续打开这些文件。
strace 能捕获所有这些 open/openat 系统调用，给我们一个 “被加载到内存的模块” 的完整列表。这是我们的分析基础。
coverage.py (代码执行层): 回答 “在被打开的文件中，哪些代码行被真正执行了？”
一个文件被打开并读入内存，不代表里面的所有代码都会运行。例如，requests/auth.py 可能被 requests 的初始化过程导入，但如果您的代码没有进行任何认证操作，auth.py 里的类和函数定义会被解析，但永远不会被调用。
coverage 精确追踪了从 handler.py 开始的整个调用链，记录下每一行被执行的代码。
这个组合是合理的，而且非常强大。strace 圈定了一个范围（所有被碰过的文件），coverage 在这个范围内进行了精细的“着色”（哪些代码行被执行了）。
2. 脚本执行流程
run_coverage_analysis() 函数:
环境设置 (export PYTHONPATH): 这是关键一步。我们必须在项目根目录运行，并告诉Python：“当你要导入模块时，请把 app5 目录也当作一个源头”。这样 import requests 才能成功。
coverage run --source=app5: 告诉 coverage：“你的监控范围是 app5 目录下的所有 .py 文件”。
coverage json: 将收集到的二进制数据转换成机器可读的 JSON 格式，方便后续在Python脚本中处理。
run_strace_analysis() 函数:
cd app5: strace 需要在 app5 目录内运行，因为 handler.py 是以它在 app5 内的相对路径来导入依赖的。
strace -e trace=open,openat ...: 监控所有文件打开操作，并将日志输出到 strace.log。
日志解析: 脚本读取 strace.log，用正则表达式提取所有被成功打开的文件路径。它会进行路径规范化，确保能和 coverage 的报告对得上。
analyze_and_report() 函数 (核心分析逻辑):
遍历 coverage 数据: coverage 的JSON报告是分析的核心，它包含了每个文件的总代码行数和被覆盖的行数。
计算覆盖率和浪费空间:
coverage_percent = covered_lines / total_lines
wasted_size = file_size * (1 - coverage_percent)
这个“浪费空间”是一个非常直观的、基于“代码行数 ≈ 磁盘占用”的线性估算模型。虽然不完全精确（例如，注释也占空间），但对于量化比较已经足够好。
定义模块状态 (Status): 这是最关键的逻辑判断。
if filepath in strace_files and coverage_percent == 0:
解读: 这个文件被 strace 记录到（说明Python解释器加载了它），但是 coverage 显示它的执行覆盖率为0。
结论: 这就是最典型的 “被初始化，但完全未被使用” 的模块。
elif coverage_percent > 0:
解读: 文件被加载，并且有部分代码被执行了。
结论: 这是 “部分使用” 的模块，我们根据覆盖率高低再细分为 Low, Medium, Heavily Used，方便观察。
排序和打印: 将结果按“浪费空间”从大到小排序，这样您能一眼看到最大的优化目标。报告被分成了“完全未使用”和“部分使用”两部分，非常清晰。