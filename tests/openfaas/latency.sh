#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <function-name>"
  exit 1
fi

FUNCTION_NAME=$1

TOTAL_LATENCY=0
ITERATIONS=10

for i in $(seq 1 $ITERATIONS)
do

    # call the function and get the latency
    RESPONSE=$(curl -s "${OPENFAAS_URL}/function/${FUNCTION_NAME}")
    LATENCY=$(echo "$RESPONSE" | grep -o 'latency is [0-9]*\.[0-9]*' | awk '{print $3}')

    if [ -z "$LATENCY" ]; then
        echo "Iteration $i: Failed to extract latency."
        continue
    fi

    echo "Iteration $i: Latency is ${LATENCY} ms"

    TOTAL_LATENCY=$(echo "$TOTAL_LATENCY + $LATENCY" | bc)
    if [ $i -lt $ITERATIONS ]; then
        sleep 0.1
    fi
done

AVERAGE_LATENCY=$(echo "scale=1; $TOTAL_LATENCY / $ITERATIONS" | bc)

echo "Average latency over $ITERATIONS iterations: ${AVERAGE_LATENCY} ms"
