#!/bin/bash

run_test() {
    local total_time=0
    local runs=50

    for i in $(seq 1 $runs); do
        output=$(python3 handler.py)
        echo "$output"
        time=$(echo "$output" | tail -n 1 | sed 's/lantency is //; s/ms//')
        total_time=$(echo "$total_time + $time" | bc -l)
    done

    local average_time=$(echo "scale=2; $total_time / $runs" | bc -l)
    echo "$average_time"
}

clear_cache() {
    find . -name "__pycache__" -type d -exec rm -r {} +
    find . -name "*.pyc" -type f -delete
}

# Test with pycache
echo "Running test with pycache..."
with_pycache=$(run_test)
echo "Average Time with pycache: $with_pycache ms"

# Test without pycache
echo "Running test without pycache..."
total_time_without_cache=0
runs=50

for i in $(seq 1 $runs); do
    clear_cache
    output=$(python3 handler.py)
    echo "$output"
    time=$(echo "$output" | tail -n 1 | sed 's/lantency is //; s/ms//')
    total_time_without_cache=$(echo "$total_time_without_cache + $time" | bc -l)
done

without_pycache=$(echo "scale=2; $total_time_without_cache / $runs" | bc -l)
echo "Average Time without pycache: $without_pycache ms"

echo "Summary:"
echo "With pycache: $with_pycache ms"
echo "Without pycache: $without_pycache ms"
