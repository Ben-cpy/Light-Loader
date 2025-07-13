import time
init_st = time.time() * 1000
import numpy
init_ed = time.time() * 1000
def handle(req):
    for i in range(1):
        for j in range(1):
            for k in range(2):
                s = numpy.array([[i, j, k], [k, j, i]])
                print(s)
    # simulate_cold_start()  
    return f'latency is {init_ed - init_st}ms'

def simulate_cold_start():
    import os
    import shutil
    pycache_dir = "/home/app"
    for root, dirs, files in os.walk(pycache_dir):
        if '__pycache__' in dirs:
            dir_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(dir_path)
                # print(f"Deleted directory: {dir_path}")
            except Exception as e:
                print(f"Error deleting directory {dir_path}: {e}")