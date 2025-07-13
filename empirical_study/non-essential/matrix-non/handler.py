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
