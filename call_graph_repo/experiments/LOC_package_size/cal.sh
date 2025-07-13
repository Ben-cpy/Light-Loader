#!/bin/bash

# 定义要排除的目录名称
EXCLUDE_DIRS=("info" "_yaml" "__pycache__")

# 初始化输出表头
printf "%-20s %-10s %-10s\n" "Directory" "LOC(k)" "Size"

# 遍历当前目录下的所有子目录
for dir in */; do
    # 去掉末尾的斜杠
    dir=${dir%/}

    # 检查当前目录是否在排除列表中
    skip=false
    for excl in "${EXCLUDE_DIRS[@]}"; do
        if [[ "$dir" == "$excl" ]]; then
            skip=true
            break
        fi
    done
    if $skip; then
        continue
    fi

    # 进入子目录
    pushd "$dir" > /dev/null

    # 运行 cloc 并提取 'SUM' 行的 'code' 数量
    cloc_output=$(cloc .)
    # 使用 awk 提取 'SUM' 行中的第四列（code）
    code_lines=$(echo "$cloc_output" | awk '/SUM:/ {print $4}')

    # 检查是否成功提取到 code_lines
    if [[ -z "$code_lines" ]]; then
        code_k="N/A"
    else
        # 将 code_lines 转换为 k，保留一位小数
        code_k=$(awk "BEGIN {printf \"%.1fk\", $code_lines/1000}")
    fi

    # 删除 __pycache__ 目录
    find . -type d -name "__pycache__" -exec rm -rf {} +

    # 获取目录大小
    dir_size=$(du -h . | tail -n 1 | awk '{print $1}')

    # 输出结果
    printf "%-20s %-10s %-10s\n" "$dir" "$code_k" "$dir_size"

    # 返回上一层目录
    popd > /dev/null
done
