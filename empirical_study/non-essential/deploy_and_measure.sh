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

# echo "开始构建函数镜像..."
# START_BUILD=$(get_time_milliseconds)
# faas-cli build -f ${FUNCTION_NAME}.yml
# END_BUILD=$(get_time_milliseconds)
# BUILD_DURATION=$(echo "scale=3; ($END_BUILD - $START_BUILD)/1000" | bc)
# echo "构建完成，耗时 ${BUILD_DURATION} 秒"

# echo "开始推送镜像到仓库..."
# START_PUSH=$(get_time_milliseconds)
# faas-cli push -f ${FUNCTION_NAME}.yml
# END_PUSH=$(get_time_milliseconds)
# PUSH_DURATION=$(echo "scale=3; ($END_PUSH - $START_PUSH)/1000" | bc)
# echo "推送完成，耗时 ${PUSH_DURATION} 秒"

# echo "开始部署函数并测量时延..."
# START_DEPLOY=$(get_time_milliseconds)
# faas-cli deploy -f ${FUNCTION_NAME}.yml

# echo "等待 Pod 创建..."
# RETRIES=30
# SLEEP_INTERVAL=2
# POD_NAME=""
# for ((i=1;i<=RETRIES;i++)); do
#     POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l "faas_function=${FUNCTION_NAME}" -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || true)
#     if [[ -n "$POD_NAME" ]]; then
#         echo "找到 Pod: $POD_NAME"
#         break
#     fi
#     echo "等待 Pod 创建中... (${i}/${RETRIES})"
#     sleep ${SLEEP_INTERVAL}
# done

# if [[ -z "$POD_NAME" ]]; then
#     echo "Error: 在等待 $((RETRIES * SLEEP_INTERVAL)) 秒后仍未找到 Pod。"
#     exit 1
# fi

# echo "等待 Pod 就绪..."
# kubectl wait --for=condition=ready pod/"${POD_NAME}" -n "${NAMESPACE}" --timeout=300s
# END_DEPLOY=$(get_time_milliseconds)
# DEPLOY_DURATION=$(echo "scale=3; ($END_DEPLOY - $START_DEPLOY)/1000" | bc)
# echo "函数部署完成，耗时 ${DEPLOY_DURATION} 秒"
# echo "=== 部署时延 ==="
# echo "构建时延: ${BUILD_DURATION} 秒"
# echo "推送时延: ${PUSH_DURATION} 秒"
# echo "部署时延: ${DEPLOY_DURATION} 秒"

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

echo "开始测试函数部署时延，重复 ${REPETITIONS} 次..."

total_deploy_duration=0

for ((i=1; i<=REPETITIONS; i++)); do
    echo "=== 第 ${i} 次部署 ==="

    # Remove the docker image to simulate cold start
    # localhost:5000/app5-non:latest
    IMAGE_NAME="localhost:5000/${FUNCTION_NAME}:${IMAGE_TAG}"
    # IMAGE_NAME="ghcr.io/lzzzzl/openfaas-${FUNCTION_NAME}:${IMAGE_TAG}"
    docker rmi ${IMAGE_NAME} 2>/dev/null || true
    docker image prune -f 
    echo "删除镜像 ${IMAGE_NAME} (如果存在)"

    echo "开始构建函数镜像..."
    START_BUILD=$(get_time_milliseconds)
    faas-cli build -f ${FUNCTION_NAME}.yml
    END_BUILD=$(get_time_milliseconds)
    BUILD_DURATION=$(echo "scale=3; ($END_BUILD - $START_BUILD)/1000" | bc)
    echo "构建完成，耗时 ${BUILD_DURATION} 秒"

    echo "开始推送镜像到仓库..."
    START_PUSH=$(get_time_milliseconds)
    faas-cli push -f ${FUNCTION_NAME}.yml
    END_PUSH=$(get_time_milliseconds)
    PUSH_DURATION=$(echo "scale=3; ($END_PUSH - $START_PUSH)/1000" | bc)
    echo "推送完成，耗时 ${PUSH_DURATION} 秒"

    echo "开始部署函数并测量时延..."
    START_DEPLOY=$(get_time_milliseconds)
    faas-cli deploy -f ${FUNCTION_NAME}.yml

    echo "等待 Pod 创建..."
    RETRIES=30
    SLEEP_INTERVAL=2
    POD_NAME=""
    for ((j=1;j<=RETRIES;j++)); do
        POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l "faas_function=${FUNCTION_NAME}" -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || true)
        if [[ -n "$POD_NAME" ]]; then
            echo "找到 Pod: $POD_NAME"
            break
        fi
        echo "等待 Pod 创建中... (${j}/${RETRIES})"
        sleep ${SLEEP_INTERVAL}
    done

    if [[ -z "$POD_NAME" ]]; then
        echo "Error: 在等待 $((RETRIES * SLEEP_INTERVAL)) 秒后仍未找到 Pod。"
        exit 1
    fi

    echo "等待 Pod 就绪..."
    kubectl wait --for=condition=ready pod/"${POD_NAME}" -n "${NAMESPACE}" --timeout=300s
    END_DEPLOY=$(get_time_milliseconds)
    DEPLOY_DURATION=$(echo "scale=3; ($END_DEPLOY - $START_DEPLOY)/1000" | bc)
    echo "函数部署完成，耗时 ${DEPLOY_DURATION} 秒"
    echo "=== 第 ${i} 次部署时延 ==="
    echo "构建时延: ${BUILD_DURATION} 秒"
    echo "推送时延: ${PUSH_DURATION} 秒"
    echo "部署时延: ${DEPLOY_DURATION} 秒"

    total_deploy_duration=$(echo "$total_deploy_duration + $DEPLOY_DURATION" | bc)

    # remove the function after deployment
    faas-cli remove  ${FUNCTION_NAME}
    # wait for the pod to be deleted, means we could not use kubeclt get to get the pod name
    echo "等待 Pod 删除..."
    while true; do
        POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l "faas_function=${FUNCTION_NAME}" -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || true)
        if [[ -z "$POD_NAME" ]]; then
            echo "Pod 已删除"
            break
        fi
        echo "等待 Pod 删除中..."
        sleep ${SLEEP_INTERVAL}
    done
done

average_deploy_duration=$(echo "scale=3; $total_deploy_duration / $REPETITIONS" | bc)
echo "=== 平均部署时延 ==="
echo "平均部署时延: ${average_deploy_duration} 秒"
echo "测试完成."
