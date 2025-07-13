import requests
import time
import subprocess
import re
import csv

# --- 配置 ---
OPENFAAS_GATEWAY = "133.133.135.8:31112" # 修改为你的网关地址
FUNCTIONS_TO_TEST = ["baseline-py", "heavy-py"]
RUNS_PER_FUNCTION = 20 # 每个函数重复测试的次数
OUTPUT_FILE = "cold_start_results.csv"

def get_pod_name(function_name):
    """使用 kubectl 获取函数对应的 pod 名称"""
    cmd = f"kubectl get pods -n openfaas-fn -l faas_function={function_name} -o jsonpath='{{.items[0].metadata.name}}'"
    try:
        # shell=True is needed for complex commands
        pod_name = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
        return pod_name
    except subprocess.CalledProcessError:
        return None

def get_app_init_latency_from_logs(pod_name):
    """从 pod 日志中提取应用级时延"""
    # 等待日志出现
    time.sleep(2) 
    cmd = f"kubectl logs -n openfaas-fn {pod_name}"
    try:
        logs = subprocess.check_output(cmd, shell=True, text=True, timeout=10)
        match = re.search(r"APP_INIT_LATENCY_MS: ([\d\.]+)", logs)
        if match:
            return float(match.group(1))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"  > Could not retrieve logs for {pod_name}: {e}")
    return None

def run_test():
    results = []
    
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["function_name", "run", "total_latency_ms", "app_init_latency_ms", "platform_latency_ms"])

        for func in FUNCTIONS_TO_TEST:
            print(f"\n--- Testing function: {func} ---")
            for i in range(1, RUNS_PER_FUNCTION + 1):
                print(f" -> Run {i}/{RUNS_PER_FUNCTION}")

                # 1. 确保函数已缩容到 0 (等待 annotation 生效)
                # 这个等待时间要大于 stack.yml 中设置的 zero-duration
                print("  > Ensuring function is scaled to zero...")
                time.sleep(20)

                # 2. 准备调用并开始计时
                url = f"{OPENFAAS_GATEWAY}/function/{func}"
                total_latency_ms = -1
                app_init_latency_ms = -1
                
                try:
                    # 3. 发起调用并测量总时延
                    start_time = time.perf_counter()
                    response = requests.post(url, data="test", timeout=30)
                    end_time = time.perf_counter()

                    total_latency_ms = (end_time - start_time) * 1000
                    
                    if response.status_code != 200:
                        print(f"  > Error: Received status code {response.status_code}")
                        print(f"  > Response: {response.text}")
                        continue

                    # 4. 从容器日志中获取应用初始化时延
                    # Pod 创建需要时间，所以稍作等待
                    time.sleep(1)
                    pod_name = get_pod_name(func)
                    if pod_name:
                        app_init_latency_ms = get_app_init_latency_from_logs(pod_name)
                    else:
                        print("  > Could not find pod to fetch logs.")

                except requests.exceptions.RequestException as e:
                    print(f"  > Request failed: {e}")
                    continue
                
                # 5. 计算平台时延并记录结果
                platform_latency_ms = -1
                if total_latency_ms > 0 and app_init_latency_ms is not None and app_init_latency_ms > 0:
                    platform_latency_ms = total_latency_ms - app_init_latency_ms

                print(f"  > Total: {total_latency_ms:.2f}ms | App: {app_init_latency_ms or 'N/A'}ms | Platform: {platform_latency_ms:.2f}ms")
                writer.writerow([func, i, total_latency_ms, app_init_latency_ms, platform_latency_ms])
                f.flush() # 立即写入文件

if __name__ == "__main__":
    run_test()
    print(f"\nExperiment finished. Results saved to {OUTPUT_FILE}")