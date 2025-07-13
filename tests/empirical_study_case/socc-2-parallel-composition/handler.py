# =================================================================
# Helper functions are kept outside the 'handle' function.
# This aligns with your optimization of analyzing the function call graph
# without unnecessarily compiling/loading them at initialization.
# =================================================================

def get_time():
    """Helper function to get current time in milliseconds."""
    # Note: I'm importing 'time' here to demonstrate that helper functions
    # can also have their own localized imports if needed, though for standard
    # libraries it's often fine to import them once inside handle().
    import time
    return int(round(time.time() * 1000))

def alu_fan_out(times, parallel_index, target_function_url, requests_session):
    """
    Orchestrates parallel calls to the target ALU function.
    Uses a shared requests.Session for connection pooling and efficiency.
    """
    # Import 'threading' only when this orchestration logic is actually called.
    import threading
    
    # Calculate payload for each individual function call
    payload = f'{{"n": {times / parallel_index}}}'
    
    results = [''] * parallel_index  # Pre-allocate list for thread-safe assignment
    threads = []
    
    for i in range(parallel_index):
        # Create and start a thread for each parallel call
        thread = threading.Thread(
            target=single_alu_call, 
            args=(payload, results, requests_session, target_function_url, i)
        )
        threads.append(thread)
        thread.start()
        
    for thread in threads:
        thread.join() # Wait for all threads to complete

    return str(results)

def single_alu_call(payload, results, requests_session, target_url, client_id):
    """
    Makes a single HTTP POST call to the target OpenFaaS function.
    This function replaces the original AWS Lambda 'boto3.invoke' logic.
    """
    # Import 'json' here as it's only needed for parsing the response.
    import json
    
    print(f"Client {client_id}: Starting call to {target_url}")
    client_start_time = get_time()
    
    try:
        # Use the provided session to make the POST request
        response = requests_session.post(target_url, data=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        client_end_time = get_time()
        client_exec_time = client_end_time - client_start_time

        # Assuming the target function returns a JSON with 'execTime'
        result_data = response.json()
        # Store the execution time reported by the downstream function
        results[client_id] = str(result_data.get('execTime', 'Error: execTime not in response'))
        
        print(f"Client {client_id}: Finished in {client_exec_time}ms. Downstream time: {results[client_id]}ms.")

    except Exception as e:
        print(f"Client {client_id}: Error during request - {e}")
        results[client_id] = "Error"


# =================================================================
# OpenFaaS Entry Point
# =================================================================

def handle(req):
    """
    Handle a request to the function. This is the main entry point for OpenFaaS.
    It orchestrates parallel calls to another function (e.g., 'do-alu').

    Args:
        req (str): Request body, expected to be a JSON string.
                   Example: '{"n": 1000, "parallelIndex": 10}'
    """
    # -----------------------------------------------------------------
    # 1. Deferred Imports: All imports are placed inside the handler.
    # This directly supports your optimization goal by avoiding import
    # costs during the cold start's initialization phase.
    # -----------------------------------------------------------------
    import json
    import os
    import requests

    # -----------------------------------------------------------------
    # 2. Configuration via Environment Variables
    # This is more flexible than hardcoding and standard practice in containers.
    # -----------------------------------------------------------------
    # The gateway URL is automatically available in OpenFaaS
    gateway_url = os.getenv("OPENFAAS_GATEWAY", "http://gateway.openfaas:8080")
    # You should define 'ALU_FUNCTION_NAME' in your stack.yml
    alu_function_name = os.getenv("ALU_FUNCTION_NAME", "do-alu")
    target_function_url = f"{gateway_url}/function/{alu_function_name}"
    
    # Start timer for the orchestrator function itself
    start_time = get_time()

    # -----------------------------------------------------------------
    # 3. Input Parsing
    # -----------------------------------------------------------------
    try:
        event = json.loads(req)
        times = int(event['n'])
        parallel_index = int(event['parallelIndex'])
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        error_message = f"Invalid input. Expected JSON with 'n' and 'parallelIndex'. Error: {e}"
        print(error_message)
        # Return a structured error message
        response_data = {"error": error_message}
        return json.dumps(response_data, indent=2)

    # -----------------------------------------------------------------
    # 4. Core Logic
    # Using a requests.Session() for connection pooling is more efficient
    # for making multiple requests to the same host.
    # -----------------------------------------------------------------
    with requests.Session() as session:
        # Call the fan-out orchestrator
        result_list_str = alu_fan_out(times, parallel_index, target_function_url, session)
    
    # Process the results
    # The result from alu_fan_out is a string representation of a list, e.g., "['123', '124', ...]"
    # We use eval() here to be consistent with the original code's logic.
    try:
        temp_dict = eval(result_list_str)
        total_exec_time = sum(int(t) for t in temp_dict if t.isdigit())
        avg_exec_time = total_exec_time / parallel_index if parallel_index > 0 else 0
    except Exception as e:
        print(f"Error processing results: {e}")
        total_exec_time = 0
        avg_exec_time = 0
    
    # -----------------------------------------------------------------
    # 5. Format Output
    # -----------------------------------------------------------------
    response_data = {
        'downstream_results': temp_dict,
        'downstream_avg_exec_time_ms': avg_exec_time,
        'total_iterations': times,
        'orchestrator_total_time_ms': get_time() - start_time
    }

    return json.dumps(response_data, indent=2)