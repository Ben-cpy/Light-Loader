#!/bin/bash

# 配置部分
FUNCTIONS=("matrix-non" "app5-non" "app8-non" "cvs-non" "image-non" "marshal-non" )  # 在这里添加你的所有函数名称
TIMEOUT=300                         # 超时时间，单位：秒
INTERVAL=2                         # 每次检查的间隔时间，单位：秒

for FUNCTION_NAME in "${FUNCTIONS[@]}"; do
    YAML_FILE="${FUNCTION_NAME}.yml"      # 部署文件路径
    
    # 记录开始时间
    start_time=$(date +%s.%N)
    echo "开始部署函数 ${FUNCTION_NAME}，时间戳：${start_time}"

    # 部署函数
    echo "执行: faas-cli deploy -f ${YAML_FILE}"
    faas-cli deploy -f "${YAML_FILE}"

    # 循环等待对应 pod 出现并进入就绪状态
    elapsed=0
    pod_ready=false

    echo "开始轮询检查 pod 状态..."
    while [ ${elapsed%.*} -lt ${TIMEOUT} ]; do
        pod_name=$(kubectl get pods -l "faas_function=${FUNCTION_NAME}" -o jsonpath="{.items[0].metadata.name}" 2>/dev/null)
        
        if [ -n "$pod_name" ]; then
            ready_status=$(kubectl get pod "${pod_name}" -o jsonpath="{.status.conditions[?(@.type=='Ready')].status}" 2>/dev/null)
            if [ "$ready_status" == "True" ]; then
                echo "Pod ${pod_name} 已经就绪。"
                pod_ready=true
                break
            else
                echo "Pod ${pod_name} 状态未就绪，当前状态：${ready_status}"
            fi
        else
            echo "还未获取到 pod，等待中..."
        fi
        
        sleep ${INTERVAL}
        elapsed=$(awk "BEGIN {print $(date +%s.%N) - ${start_time}}")
    done

    end_time=$(date +%s.%N)
    if [ "${pod_ready}" = true ]; then
        total_time=$(awk "BEGIN {printf \"%.3f\", ${end_time} - ${start_time}}")
        echo "函数 ${FUNCTION_NAME} pod 就绪所花费的时间：${total_time} 秒。"
    else
        echo "超时！在 ${TIMEOUT} 秒内未检测到函数 ${FUNCTION_NAME} pod 就绪。"
    fi

    echo "----------------------------------------"
done
