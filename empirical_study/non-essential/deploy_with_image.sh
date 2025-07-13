#!/bin/bash

set -e

FUNCTION_NAME="cvs-non"
NAMESPACE="openfaas-fn"
TOTAL_TESTS=5
TOTAL_DEPLOY_TIME=0

get_time_milliseconds() {
    date +%s%3N
}

for ((test=1;test<=${TOTAL_TESTS};test++)); do
    echo "=== Starting test ${test} ==="

    echo "Starting function deployment and measuring latency..."
    START_DEPLOY=$(get_time_milliseconds)
    faas-cli deploy -f ${FUNCTION_NAME}.yml

    echo "Waiting for Pod creation..."
    RETRIES=30
    SLEEP_INTERVAL=2
    POD_NAME=""
    for ((i=1;i<=RETRIES;i++)); do
        POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l "faas_function=${FUNCTION_NAME}" -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || true)
        if [[ -n "$POD_NAME" ]]; then
            echo "Found Pod: $POD_NAME"
            break
        fi
        echo "Waiting for Pod creation... (${i}/${RETRIES})"
        sleep ${SLEEP_INTERVAL}
    done

    if [[ -z "$POD_NAME" ]]; then
        echo "Error: Pod not found after waiting $((RETRIES * SLEEP_INTERVAL)) seconds."
        exit 1
    fi

    echo "Waiting for Pod to be ready..."
    kubectl wait --for=condition=ready pod/"${POD_NAME}" -n "${NAMESPACE}" --timeout=300s
    END_DEPLOY=$(get_time_milliseconds)
    DEPLOY_DURATION=$(echo "scale=3; ($END_DEPLOY - $START_DEPLOY)/1000" | bc)
    echo "Function deployment completed, took ${DEPLOY_DURATION} seconds"

    # Accumulate deployment time
    TOTAL_DEPLOY_TIME=$(echo "scale=3; ${TOTAL_DEPLOY_TIME} + ${DEPLOY_DURATION}" | bc)

    # Remove function
    echo "Removing function..."
    faas-cli remove ${FUNCTION_NAME}

    # If not the last test, wait before next test
    if [ $test -lt $TOTAL_TESTS ]; then
        echo "Waiting 60 seconds before next test..."
        sleep 60
    fi
done

# Calculate average deployment time
AVERAGE_DEPLOY_TIME=$(echo "scale=3; ${TOTAL_DEPLOY_TIME}/${TOTAL_TESTS}" | bc)

echo ""
echo "=== Test Results Summary ==="
echo "Total test runs: ${TOTAL_TESTS}"
echo "Average deployment latency: ${AVERAGE_DEPLOY_TIME} seconds"