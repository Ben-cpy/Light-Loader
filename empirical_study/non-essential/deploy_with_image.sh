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
    echo "=== 开始第 ${test} 次测试 ==="
    
    echo "开始部署函数并测量时延..."
    START_DEPLOY=$(get_time_milliseconds)
    faas-cli deploy -f ${FUNCTION_NAME}.yml

    echo "等待 Pod 创建..."
    RETRIES=30
    SLEEP_INTERVAL=2
    POD_NAME=""
    for ((i=1;i<=RETRIES;i++)); do
        POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l "faas_function=${FUNCTION_NAME}" -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || true)
        if [[ -n "$POD_NAME" ]]; then
            echo "找到 Pod: $POD_NAME"
            break
        fi
        echo "等待 Pod 创建中... (${i}/${RETRIES})"
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
    
    # 累加部署时间
    TOTAL_DEPLOY_TIME=$(echo "scale=3; ${TOTAL_DEPLOY_TIME} + ${DEPLOY_DURATION}" | bc)
    
    # 删除函数
    echo "删除函数..."
    faas-cli remove ${FUNCTION_NAME}
    
    # 如果不是最后一次测试，等待一段时间再进行下一次测试
    if [ $test -lt $TOTAL_TESTS ]; then
        echo "等待 20 秒后进行下一次测试..."
        sleep 60
    fi
done

# 计算平均部署时间
AVERAGE_DEPLOY_TIME=$(echo "scale=3; ${TOTAL_DEPLOY_TIME}/${TOTAL_TESTS}" | bc)

echo ""
echo "=== 测试结果汇总 ==="
echo "总测试次数: ${TOTAL_TESTS}"
echo "平均部署时延: ${AVERAGE_DEPLOY_TIME} 秒"