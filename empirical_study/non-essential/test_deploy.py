#!/bin/bash

# Configuration section
FUNCTION_NAME="your_function_name"  # Replace with your function name
YAML_FILE="${FUNCTION_NAME}.yml"      # Deployment file path
TIMEOUT=300                         # Timeout in seconds
INTERVAL=2                          # Check interval in seconds

# Record start time
start_time=$(date +%s)
echo "Starting deployment of function ${FUNCTION_NAME}, timestamp: ${start_time}"

# Deploy function
echo "Executing: faas-cli deploy -f ${YAML_FILE}"
faas-cli deploy -f "${YAML_FILE}"

# Loop waiting for corresponding pod to appear and become ready
elapsed=0
pod_ready=false

echo "Starting polling to check pod status..."
while [ ${elapsed} -lt ${TIMEOUT} ]; do
    # OpenFaaS deployment usually labels pods with faas_function=<function_name>
    pod_name=$(kubectl get pods -l "faas_function=${FUNCTION_NAME}" -o jsonpath="{.items[0].metadata.name}" 2>/dev/null)

    if [ -n "$pod_name" ]; then
        # Query pod's Ready condition
        ready_status=$(kubectl get pod "${pod_name}" -o jsonpath="{.status.conditions[?(@.type=='Ready')].status}" 2>/dev/null)
        if [ "$ready_status" == "True" ]; then
            echo "Pod ${pod_name} is ready."
            pod_ready=true
            break
        else
            echo "Pod ${pod_name} is not ready, current status: ${ready_status}"
        fi
    else
        echo "Pod not found yet, waiting..."
    fi

    sleep ${INTERVAL}
    elapsed=$(( $(date +%s) - ${start_time} ))
done

end_time=$(date +%s)
if [ "${pod_ready}" = true ]; then
    total_time=$(( end_time - start_time ))
    echo "Time taken for function pod to be ready: ${total_time} seconds."
else
    echo "Timeout! Function pod not ready within ${TIMEOUT} seconds."
fi
