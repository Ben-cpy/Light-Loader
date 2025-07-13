#!/bin/bash
# Filename: system_lib_size.sh

# Define standard system library directories
SYSTEM_LIB_DIRS=("/lib" "/lib64" "/usr/lib" "/usr/lib64")

# Calculate total size of all system libraries (excluding symbolic links)
total_size=$(find "${SYSTEM_LIB_DIRS[@]}" -type f -name "*.so*" -exec du -b {} + 2>/dev/null | awk '{sum += $1} END {print sum}')

# Convert to human-readable format (MB)
human_size=$(echo "$total_size" | awk '{printf "%.2f MB\n", $1/1024/1024}')

# Generate report
echo "===== System Library Total Size Report ====="
echo "Scanned directories: ${SYSTEM_LIB_DIRS[*]}"
echo "Total file count: $(find "${SYSTEM_LIB_DIRS[@]}" -type f -name "*.so*" 2>/dev/null | wc -l)"
echo "Total size (Bytes): $total_size"
echo "Converted size: $human_size"
