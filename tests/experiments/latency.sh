total_latency=0

for i in {1..30}
do
    # 清除pycache
    find /home/app -type d -name "__pycache__" -exec rm -rf {} +  && t1=$(date +%s%3N)
    # t1=$(date +%s%3N)
    # 记录当前时间 t1
    

    # 使用 curl 向 localhost:8080 发送请求，并捕获标准输出中的时间 t2
    # t2=$(curl -s http://172.24.58.115:31112/function/oriapp8  | grep -o 'func ready, now time is [0-9]*' | tail -1 | awk '{print $NF}')
    t2=$(curl -s localhost:8080  | grep -o 'func ready, now time is [0-9]*' | tail -1 | awk '{print $NF}')

    # 计算时间差
    latency=$((t2 - t1))

    # 输出本次循环时间差
    echo "Iteration $i: Latency is $latency ms"

    # 累加总时延
    total_latency=$((total_latency + latency))
done

# 计算平均时延
average_latency=$((total_latency / 30))

echo "Average latency over 30 iterations: $average_latency ms"


