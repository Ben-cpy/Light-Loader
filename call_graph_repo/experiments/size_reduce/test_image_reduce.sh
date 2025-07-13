#!/bin/bash

# output img.log
FUNCTIONS=("app3" "app6" "app13" "tinydb"  "marshal" "graph" "game"  "auth"  "formatter"  "crypto" "psutil" "cli-application"  "type-check" "tinydb" )

# Define log file
LOG_FILE="docker_slim_results.log"
echo "Docker-slim optimization results - $(date)" > "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"

# Function to convert size to MB
convert_to_mb() {
    local size=$1
    if [[ $size == *GB ]]; then
        echo "scale=2; ${size%GB} * 1024" | bc
    elif [[ $size == *MB ]]; then
        echo "${size%MB}"
    else
        echo "0"
    fi
}

# Function to calculate reduction ratio
calculate_ratio() {
    local original=$1
    local reduced=$2
    echo "scale=2; $original / $reduced" | bc
}

# Process each function
for func in "${FUNCTIONS[@]}"; do
    echo "Processing $func..."
    echo "Processing $func..." >> "$LOG_FILE"
    
    # Check if image exists
    original_image="localhost:5000/$func"
    if ! docker images "$original_image" | grep -q "$func"; then
        echo "Image $original_image not found, skipping..." >> "$LOG_FILE"
        continue
    fi

    # Get original size
    original_size=$(docker images "$original_image" --format "{{.Size}}")
    echo "Original size: $original_size" >> "$LOG_FILE"

    # Run docker-slim
    echo "Running docker-slim on $original_image..." >> "$LOG_FILE"
    docker-slim build --target "$original_image" --tag "${original_image}-slim"

    # Get new size
    new_size=$(docker images "${original_image}-slim" --format "{{.Size}}")
    echo "Optimized size: $new_size" >> "$LOG_FILE"

    # Calculate and display reduction ratio
    original_mb=$(convert_to_mb "$original_size")
    new_mb=$(convert_to_mb "$new_size")
    ratio=$(calculate_ratio "$original_mb" "$new_mb")
    
    echo "Reduction ratio: ${ratio}x" >> "$LOG_FILE"
    echo "----------------------------------------" >> "$LOG_FILE"

    # Remove the slimmed image
    docker rmi "${original_image}-slim"
    echo "Removed slimmed image ${original_image}-slim" >> "$LOG_FILE"
done

echo "Processing complete. Results saved to $LOG_FILE"