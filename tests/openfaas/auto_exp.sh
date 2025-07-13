#!/bin/bash

# The  initial simulate_cold_start() is commented out.

# 定义要测试的函数列表

# FUNCTIONS=("marshal" "graph" "game" "auth")
# FUNCTIONS=("formatter" "cli-application" "crypto" "type-check" "psutil")
# FUNCTIONS=("pdfminer" "app11" "opencv-img" "app9" "audio")
# FUNCTIONS=("app9" cat-dot" "nlp-ner") # only use package lazy load 
#   already tested
# FUNCTIONS=( "app3" "app6" "app13" "tinydb" "marshal" "graph" "game" "auth" ) 
# "app11" "audio"
# FUNCTIONS=("formatter" "crypto" "psutil" "pdfminer" "bidict")
# "app3" "app6" "app13" "tinydb" "marshal" "graph" "game" "auth" 
# "audio" "cli-application" "opencv-img"  "cat-dog" "app10" "app9"
# "nlp-ner"


#  "app3" "app6" "app13" "tinydb"   "marshal" "graph" "game"  "auth"  "formatter"  "crypto" "psutil" "cli-application"  "type-check"    这批测试完
FUNCTIONS=( "tinydb" )
# FUNCTIONS=("app10")
FUNCTIONS_NO_SLIM=("auth" "crypto" "graph" "formatter" "pdfminer" "cli-application" "app11" "marshal" "opencv-img" "app9")

# 测试次数
# ITERATIONS=20

# 日志文件
LOG_FILE="test_results.txt"

# 清空日志文件
> "$LOG_FILE"

function wait_for_function() {
    local func_name=$1
    local ready=false
    
    echo "start to test liveness for ${func_name}..."
    for _ in {1..20}; do
        RESPONSE=$(curl -s "${OPENFAAS_URL}/function/${func_name}")
        if echo "$RESPONSE" | grep -q "latency is"; then
            ready=true
            echo "-----Function $func_name is ready.------" 
            sleep 5
            break
        fi
        sleep 5
    done
    if [ "$ready" = false ]; then
        echo "-----Function $func_name not ready after retrying.------"
        exit 1
    fi
}

echo " -----both ----" >> "$LOG_FILE"

# 遍历每个函数
for FUNCTION_NAME in "${FUNCTIONS[@]}"; do
    echo "Processing function: $FUNCTION_NAME" >> "$LOG_FILE"

    # 部署函数（热启动）
    echo "Deploying $FUNCTION_NAME (Hot Start)..." >> "$LOG_FILE"
    if [[ " ${FUNCTIONS_NO_SLIM[@]} " =~ " ${FUNCTION_NAME} " ]]; then
        while faas list | grep -q "^$FUNCTION_NAME\s"; do
            faas-cli rm $FUNCTION_NAME
            echo "$(date) - Function '$FUNCTION_NAME' is already deployed. Waiting..." 
            sleep 2
        done
        faas-cli up -f ./$FUNCTION_NAME.yml
    else
        ./deploy_slim.sh "$FUNCTION_NAME"
    fi

    # 等待函数准备就绪
    echo "Waiting for $FUNCTION_NAME to be ready..." >> "$LOG_FILE"
    wait_for_function "$FUNCTION_NAME"

    # 测试导入时延 t1 (热启动)
    echo "--------Testing t1 (Hot Start) for $FUNCTION_NAME..." >> "$LOG_FILE"
    for i in {1..3}; do
        echo "Round$i:" >> "$LOG_FILE"
        ./latency.sh "$FUNCTION_NAME" >> "$LOG_FILE"
    done

    # 测试总时延 t2 (热启动)
    echo "--------Testing t2 E2E (Hot Start) for $FUNCTION_NAME..." >> "$LOG_FILE"
    for i in {1..3}; do
       echo "Round$i:" >> "$LOG_FILE"
        ./latency_total.sh "$FUNCTION_NAME" >> "$LOG_FILE"
    done

    # avoid same result
    faas-cli rm $FUNCTION_NAME
    sleep 10 # waitfor the function to be removed

    # 模拟冷启动
    echo "Simulating Cold Start for $FUNCTION_NAME..." >> "$LOG_FILE"
    # 修改 handler.py 启用 simulate_cold_start()
    sed -i 's/^\([[:space:]]*\)# simulate_cold_start()/\1simulate_cold_start()/' "./$FUNCTION_NAME/handler.py"    # 重新部署函数（冷启动）
    echo "Deploying $FUNCTION_NAME (Cold Start)..." >> "$LOG_FILE"
    if [[ " ${FUNCTIONS_NO_SLIM[@]} " =~ " ${FUNCTION_NAME} " ]]; then
        while faas list | grep -q "^$FUNCTION_NAME\s"; do
            faas-cli rm $FUNCTION_NAME
            echo "$(date) - Function '$FUNCTION_NAME' is already deployed. Waiting..." 
            sleep 2
        done
        faas-cli up -f ./$FUNCTION_NAME.yml
    else
        ./deploy_slim.sh "$FUNCTION_NAME"
    fi

    # 等待函数准备就绪
    echo "Waiting for $FUNCTION_NAME to be ready..." >> "$LOG_FILE"
    wait_for_function "$FUNCTION_NAME"

    # 测试导入时延 t1 (冷启动)
    echo "--------Testing t1 (Cold Start) for $FUNCTION_NAME..." >> "$LOG_FILE"
    for i in {1..3}; do
        echo "Round$i:" >> "$LOG_FILE"
        ./latency.sh "$FUNCTION_NAME" >> "$LOG_FILE"
    done

    # 测试总时延 t2 (冷启动)
    echo "--------Testing t2 E2E (Cold Start) for $FUNCTION_NAME..." >> "$LOG_FILE"
    for i in {1..3}; do
        echo "Round$i:" >> "$LOG_FILE"
        ./latency_total.sh "$FUNCTION_NAME" >> "$LOG_FILE"
    done

    # 恢复 handler.py 注释 simulate_cold_start()
    sed -i 's/^\([[:space:]]*\)simulate_cold_start()/\1# simulate_cold_start()/' "./$FUNCTION_NAME/handler.py"

    # 清理函数
    echo "Cleaning up $FUNCTION_NAME..." >> "$LOG_FILE"
    faas-cli rm $FUNCTION_NAME

    echo "----------------------------------------Next function----------------------------------------" >> "$LOG_FILE"
done

echo "All tests completed. Results saved to $LOG_FILE"