#!/bin/bash
# Filename: app_deps_size.sh

# Input file (from strace output)
INPUT_FILE="./strace_so_list.txt"  # Replace with your actual file path

# Generate dependency library report
echo "===== Application Direct Dependency Library Analysis =====" > deps_report.txt

# Step 1: Filter system libraries and deduplicate (exclude Python local modules)
grep -E '^(/lib|/usr/lib|/lib64|/usr/lib64)' "$INPUT_FILE" | sort -u > system_deps.txt

# Step 2: Parse symbolic links to get real paths
declare -A real_paths  # Use associative array for deduplication
while IFS= read -r line
do
    # Skip non-existent files (like ld.so.cache)
    [ -e "$line" ] || continue

    # Parse real path
    real_path=$(readlink -f "$line")

    # Deduplication processing
    if [ -n "$real_path" ] && [ ! -d "$real_path" ]; then
        real_paths["$real_path"]=1
    fi
done < system_deps.txt

# Step 3: Calculate total size and generate details
total=0
echo "Dependency library details:" >> deps_report.txt
printf "%-60s %s\n" "Library Path" "Size (Bytes)" >> deps_report.txt
printf "%-60s %s\n" "------------" "------------" >> deps_report.txt

for path in "${!real_paths[@]}"; do
    size=$(du -b "$path" 2>/dev/null | awk '{print $1}')
    if [ -n "$size" ]; then
        printf "%-60s %'d\n" "$path" "$size" >> deps_report.txt
        total=$((total + size))
    fi
done

# Generate summary information
echo "" >> deps_report.txt
echo "Summary statistics:" >> deps_report.txt
echo "Total dependency libraries: ${#real_paths[@]}" >> deps_report.txt
echo "Total size (Bytes): $total" >> deps_report.txt
echo "Converted size: $(echo "$total" | awk '{printf "%.2f MB\n", $1/1024/1024}')" >> deps_report.txt

# Output report
cat deps_report.txt
