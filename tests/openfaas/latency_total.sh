#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <function-name>"
  exit 1
fi

FUNCTION_NAME=$1

TOTAL_RESPONSE_TIME=0
ITERATIONS=10

for i in $(seq 1 $ITERATIONS)
do
    START_TIME=$(date +%s%N)
    RESPONSE=$(curl -s "${OPENFAAS_URL}/function/${FUNCTION_NAME}")
    END_TIME=$(date +%s%N)

    RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))

    echo "Iteration $i: Response time is ${RESPONSE_TIME} milliseconds"

    TOTAL_RESPONSE_TIME=$(( TOTAL_RESPONSE_TIME + RESPONSE_TIME ))
    if [ $i -lt $ITERATIONS ]; then
        sleep 0.1
    fi
done

AVERAGE_RESPONSE_TIME=$(echo "scale=1; $TOTAL_RESPONSE_TIME / $ITERATIONS" | bc)

echo "Average response time over $ITERATIONS iterations: ${AVERAGE_RESPONSE_TIME} milliseconds"
