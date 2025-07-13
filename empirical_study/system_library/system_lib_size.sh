#!/bin/bash
# 文件名: system_lib_size.sh

# 定义系统库标准目录
SYSTEM_LIB_DIRS=("/lib" "/lib64" "/usr/lib" "/usr/lib64")

# 计算所有系统库的总大小（排除符号链接）
total_size=$(find "${SYSTEM_LIB_DIRS[@]}" -type f -name "*.so*" -exec du -b {} + 2>/dev/null | awk '{sum += $1} END {print sum}')

# 转换为人类可读格式（MB）
human_size=$(echo "$total_size" | awk '{printf "%.2f MB\n", $1/1024/1024}')

# 生成报告
echo "===== 系统库总大小报告 ====="
echo "扫描目录: ${SYSTEM_LIB_DIRS[*]}"
echo "总文件数: $(find "${SYSTEM_LIB_DIRS[@]}" -type f -name "*.so*" 2>/dev/null | wc -l)"
echo "总大小 (Bytes): $total_size"
echo "换算大小: $human_size"
