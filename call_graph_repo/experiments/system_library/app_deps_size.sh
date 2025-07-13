#!/bin/bash
# 文件名: app_deps_size.sh

# 输入文件（来自strace的输出）
INPUT_FILE="./strace_so_list.txt"  # 替换为你的实际文件路径

# 生成依赖库报告
echo "===== 应用直接依赖库分析 =====" > deps_report.txt

# 步骤1：筛选系统库并去重（排除Python本地模块）
grep -E '^(/lib|/usr/lib|/lib64|/usr/lib64)' "$INPUT_FILE" | sort -u > system_deps.txt

# 步骤2：解析符号链接获取真实路径
declare -A real_paths  # 使用关联数组去重
while IFS= read -r line
do
    # 跳过不存在的文件（如ld.so.cache）
    [ -e "$line" ] || continue
    
    # 解析真实路径
    real_path=$(readlink -f "$line")
    
    # 去重处理
    if [ -n "$real_path" ] && [ ! -d "$real_path" ]; then
        real_paths["$real_path"]=1
    fi
done < system_deps.txt

# 步骤3：计算总大小并生成明细
total=0
echo "依赖库明细：" >> deps_report.txt
printf "%-60s %s\n" "Library Path" "Size (Bytes)" >> deps_report.txt
printf "%-60s %s\n" "------------" "------------" >> deps_report.txt

for path in "${!real_paths[@]}"; do
    size=$(du -b "$path" 2>/dev/null | awk '{print $1}')
    if [ -n "$size" ]; then
        printf "%-60s %'d\n" "$path" "$size" >> deps_report.txt
        total=$((total + size))
    fi
done

# 生成汇总信息
echo "" >> deps_report.txt
echo "汇总统计：" >> deps_report.txt
echo "依赖库总数: ${#real_paths[@]}" >> deps_report.txt
echo "总大小 (Bytes): $total" >> deps_report.txt
echo "换算大小: $(echo "$total" | awk '{printf "%.2f MB\n", $1/1024/1024}')" >> deps_report.txt

# 输出报告
cat deps_report.txt
