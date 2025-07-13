# #!/bin/bash

# set -e

# # FUNCTION_NAME="matrix-non"
# # FUNCTION_NAME="cvs-non" 
# FUNCTION_NAME="image-non" 
# LANGUAGE="python"
# NAMESPACE="openfaas-fn"
# IMAGE_TAG="latest"

# FUNCTION_DIR="./${FUNCTION_NAME}"

# get_time_milliseconds() {
#     date +%s%3N
# }

# echo "Starting function image build..."
# START_BUILD=$(get_time_milliseconds)
# faas-cli build -f ${FUNCTION_NAME}.yml
# END_BUILD=$(get_time_milliseconds)
# BUILD_DURATION=$(echo "scale=3; ($END_BUILD - $START_BUILD)/1000" | bc)
# echo "Build completed, took ${BUILD_DURATION} seconds"

# echo "Starting image push to repository..."
# START_PUSH=$(get_time_milliseconds)
# faas-cli push -f ${FUNCTION_NAME}.yml
# END_PUSH=$(get_time_milliseconds)
# PUSH_DURATION=$(echo "scale=3; ($END_PUSH - $START_PUSH)/1000" | bc)
# echo "Push completed, took ${PUSH_DURATION} seconds"

# echo "Starting function deployment and measuring latency..."
# START_DEPLOY=$(get_time_milliseconds)
# faas-cli deploy -f ${FUNCTION_NAME}.yml

# echo "Waiting for Pod creation..."
# RETRIES=30
# SLEEP_INTERVAL=2
# POD_NAME=""
# for ((i=1;i<=RETRIES;i++)); do
#     POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l "faas_function=${FUNCTION_NAME}" -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || true)
#     if [[ -n "$POD_NAME" ]]; then
#         echo "Found Pod: $POD_NAME"
#         break
#     fi
#     echo "Waiting for Pod creation... (${i}/${RETRIES})"
#     sleep ${SLEEP_INTERVAL}
# done

# if [[ -z "$POD_NAME" ]]; then
#     echo "Error: Pod not found after waiting $((RETRIES * SLEEP_INTERVAL)) seconds."
#     exit 1
# fi

# echo "Waiting for Pod to be ready..."
# kubectl wait --for=condition=ready pod/"${POD_NAME}" -n "${NAMESPACE}" --timeout=300s
# END_DEPLOY=$(get_time_milliseconds)
# DEPLOY_DURATION=$(echo "scale=3; ($END_DEPLOY - $START_DEPLOY)/1000" | bc)
# echo "Function deployment completed, took ${DEPLOY_DURATION} seconds"
# echo "=== Deployment Latency ==="
# echo "Build latency: ${BUILD_DURATION} seconds"
# echo "Push latency: ${PUSH_DURATION} seconds"
# echo "Deploy latency: ${DEPLOY_DURATION} seconds"

# # remove the function after deployment
# faas-cli remove  ${FUNCTION_NAME}

#!/bin/bash

set -e


# FUNCTION_NAME="app5-non"
# FUNCTION_NAME="app8-non"  
# FUNCTION_NAME="image-non"
# FUNCTION_NAME="marshal-non"
FUNCTION_NAME="matrix-non"
# FUNCTION_NAME="cvs-non"
LANGUAGE="python"
NAMESPACE="openfaas-fn"
IMAGE_TAG="latest"
REPETITIONS=1
SLEEP_INTERVAL=2
FUNCTION_DIR="./${FUNCTION_NAME}"

get_time_milliseconds() {
    date +%s%3N
}

echo "Starting function deployment latency test, repeating ${REPETITIONS} times..."

total_deploy_duration=0

for ((i=1; i<=REPETITIONS; i++)); do
    echo "=== Deployment ${i} ==="

    # Remove the docker image to simulate cold start
    # localhost:5000/app5-non:latest
    IMAGE_NAME="localhost:5000/${FUNCTION_NAME}:${IMAGE_TAG}"
    # IMAGE_NAME="ghcr.io/lzzzzl/openfaas-${FUNCTION_NAME}:${IMAGE_TAG}"
    docker rmi ${IMAGE_NAME} 2>/dev/null || true
    docker image prune -f
    echo "Removed image ${IMAGE_NAME} (if exists)"

    echo "Starting function image build..."
    START_BUILD=$(get_time_milliseconds)
    faas-cli build -f ${FUNCTION_NAME}.yml
    END_BUILD=$(get_time_milliseconds)
    BUILD_DURATION=$(echo "scale=3; ($END_BUILD - $START_BUILD)/1000" | bc)
    echo "Build completed, took ${BUILD_DURATION} seconds"

    echo "Starting image push to repository..."
    START_PUSH=$(get_time_milliseconds)
    faas-cli push -f ${FUNCTION_NAME}.yml
    END_PUSH=$(get_time_milliseconds)
    PUSH_DURATION=$(echo "scale=3; ($END_PUSH - $START_PUSH)/1000" | bc)
    echo "Push completed, took ${PUSH_DURATION} seconds"

    echo "Starting function deployment and measuring latency..."
    START_DEPLOY=$(get_time_milliseconds)
    faas-cli deploy -f ${FUNCTION_NAME}.yml

    echo "Waiting for Pod creation..."
    RETRIES=30
    SLEEP_INTERVAL=2
    POD_NAME=""
    for ((j=1;j<=RETRIES;j++)); do
        POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l "faas_function=${FUNCTION_NAME}" -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || true)
        if [[ -n "$POD_NAME" ]]; then
            echo "Found Pod: $POD_NAME"
            break
        fi
        echo "Waiting for Pod creation... (${j}/${RETRIES})"
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
    echo "=== Deployment ${i} Latency ==="
    echo "Build latency: ${BUILD_DURATION} seconds"
    echo "Push latency: ${PUSH_DURATION} seconds"
    echo "Deploy latency: ${DEPLOY_DURATION} seconds"

    total_deploy_duration=$(echo "$total_deploy_duration + $DEPLOY_DURATION" | bc)

    # remove the function after deployment
    faas-cli remove  ${FUNCTION_NAME}
    # wait for the pod to be deleted, means we could not use kubeclt get to get the pod name
    echo "Waiting for Pod deletion..."
    while true; do
        POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l "faas_function=${FUNCTION_NAME}" -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || true)
        if [[ -z "$POD_NAME" ]]; then
            echo "Pod deleted"
            break
        fi
        echo "Waiting for Pod deletion..."
        sleep ${SLEEP_INTERVAL}
    done
done

average_deploy_duration=$(echo "scale=3; $total_deploy_duration / $REPETITIONS" | bc)
echo "=== Average Deployment Latency ==="
echo "Average deployment latency: ${average_deploy_duration} seconds"
echo "Test completed."
