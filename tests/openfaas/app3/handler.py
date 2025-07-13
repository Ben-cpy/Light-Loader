import time
init_st = time.time() * 1000
import numpy as np
import pandas as pd
init_ed = time.time() * 1000

def handle(req):
    lib_version = {'numpy': np.__version__, 'pandas': pd.__version__}

    sales = [{'account': 'Jones LLC', 'Jan': 150, 'Feb': 200, 'Mar': 140},
             {'account': 'Alpha Co', 'Jan': 200, 'Feb': 210, 'Mar': 215},
             {'account': 'Blue Inc', 'Jan': 50, 'Feb': 90, 'Mar': 95}]
    df = pd.DataFrame(sales)
    # print(df)
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