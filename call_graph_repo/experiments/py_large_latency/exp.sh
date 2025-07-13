#!/bin/bash

# 配置变量
GATEWAY_URL="http://YOUR_OPENFAAS_URL"  # 替换为您的 OpenFaaS 网关 URL
FUNCTIONS=("hello-python" "hello-node" "hello-go")  # 函数名称
SCALE_DOWN_DELAY=10  # 缩放到零后等待的时间（秒）
TEST_RUNS=5  # 每个函数的测试次数

# 检查是否安装 kubectl
if ! command -v kubectl &> /dev/null
then
    echo "kubectl 未安装。请安装 kubectl 并配置访问权限。"
    exit 1
fi

# 运行测试
for FUNC in "${FUNCTIONS[@]}"; do
    echo "开始测试函数: $FUNC"
    
    for ((i=1;i<=TEST_RUNS;i++)); do
        echo "测试运行 #$i 对函数 $FUNC"

        # 缩放函数到零副本
        kubectl scale deployment "$FUNC" --replicas=0 -n openfaas-fn
        echo "缩放函数 $FUNC 到零副本。等待 $SCALE_DOWN_DELAY 秒..."
        sleep $SCALE_DOWN_DELAY

        # 发起请求并测量响应时间
        START_TIME=$(date +%s%3N)  # 毫秒级时间戳
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY_URL/function/$FUNC")
        END_TIME=$(date +%s%3N)
        DURATION=$((END_TIME - START_TIME))

        # 检查响应状态码
        if [ "$RESPONSE" -ne 200 ]; then
            echo "请求失败，状态码: $RESPONSE"
        else
            echo "请求成功，响应时间: ${DURATION}ms"
        fi

        # 记录结果
        echo "$FUNC, Run $i, Response Time: ${DURATION}ms" >> cold_start_results.csv
    done
    echo "完成函数 $FUNC 的测试。"
done

echo "所有测试完成。结果保存在 cold_start_results.csv"
