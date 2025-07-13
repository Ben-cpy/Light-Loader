#!/bin/bash
# 批量删除函数

# Define an array of function names to be removed
functions=(
    "type-check"
    "psutil"
    "formatter"
    # Add more functions as needed
)
# each element add a `ori-` prefix
for i in "${!functions[@]}"; do
    functions[$i]="ori-${functions[$i]}"
done

# Loop through the array and remove each function
for func in "${functions[@]}"; do
    echo "Removing function: $func"
    faas-cli rm "$func"
done

echo "All functions have been removed"