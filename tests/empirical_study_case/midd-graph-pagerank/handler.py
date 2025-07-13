# {"size": 10000,"seed": 42}
import datetime
import json
import igraph
import random

def handle(req):
    """
    OpenFaaS handler to generate a graph and compute its PageRank.

    Args:
        req (str): A JSON string with the following format:
                   {
                       "size": 10000,
                       "seed": 42
                   }
    """
    try:
        # 1. Parse the input request string into a dictionary
        event = json.loads(req)

        size = event.get('size')
        if not size:
            return json.dumps({"status": "error", "message": "Parameter 'size' is required."}), 400

        # 2. Set the random seed if provided, for reproducibility
        if "seed" in event:
            random.seed(event["seed"])

        # 3. Generate the graph (CPU-intensive)
        graph_generating_begin = datetime.datetime.now()
        # Create a Barabasi-Albert graph with 'size' nodes. 
        # The '10' is the number of outbound edges for each new node.
        graph = igraph.Graph.Barabasi(int(size), 10)
        graph_generating_end = datetime.datetime.now()

        # 4. Compute PageRank (CPU-intensive)
        process_begin = datetime.datetime.now()
        pagerank_result = graph.pagerank()
        process_end = datetime.datetime.now()

        # 5. Calculate metrics
        graph_generating_time = (graph_generating_end - graph_generating_begin) / datetime.timedelta(microseconds=1)
        process_time = (process_end - process_begin) / datetime.timedelta(microseconds=1)

        # 6. Format the response
        response = {
            # The full pagerank_result is a list of scores for all nodes. 
            # Returning a sample is usually sufficient.
            'result_sample': pagerank_result[0] if pagerank_result else None,
            'measurement': {
                'graph_generating_time': graph_generating_time,
                'compute_time': process_time
            }
        }
        
        return json.dumps(response), 200

    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "Invalid JSON input."}), 400
    except Exception as e:
        error_message = {"status": "error", "message": str(e)}
        return json.dumps(error_message), 500