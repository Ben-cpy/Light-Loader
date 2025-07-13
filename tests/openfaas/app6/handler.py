import time
init_st = time.time() * 1000
import numpy
import pandas
init_ed = time.time() * 1000

def handle(req):
	fun_st = time.time() * 1000
	s = pandas.Series(numpy.random.randn(5), index=['a', 'b', 'c', 'd', 'e'])
	fun_ed = time.time() * 1000
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