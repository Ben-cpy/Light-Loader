#!/bin/bash

# Define directory names to exclude
EXCLUDE_DIRS=("info" "_yaml" "__pycache__")

# Initialize output header
printf "%-20s %-10s %-10s\n" "Directory" "LOC(k)" "Size"

# Iterate through all subdirectories in current directory
for dir in */; do
    # Remove trailing slash
    dir=${dir%/}

    # Check if current directory is in exclude list
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

    # Enter subdirectory
    pushd "$dir" > /dev/null

    # Run cloc and extract 'code' count from 'SUM' line
    cloc_output=$(cloc .)
    # Use awk to extract fourth column (code) from 'SUM' line
    code_lines=$(echo "$cloc_output" | awk '/SUM:/ {print $4}')

    # Check if code_lines was successfully extracted
    if [[ -z "$code_lines" ]]; then
        code_k="N/A"
    else
        # Convert code_lines to k, keeping one decimal place
        code_k=$(awk "BEGIN {printf \"%.1fk\", $code_lines/1000}")
    fi

    # Remove __pycache__ directories
    find . -type d -name "__pycache__" -exec rm -rf {} +

    # Get directory size
    dir_size=$(du -h . | tail -n 1 | awk '{print $1}')

    # Output results
    printf "%-20s %-10s %-10s\n" "$dir" "$code_k" "$dir_size"

    # Return to parent directory
    popd > /dev/null
done
