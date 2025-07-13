import time
init_st = time.time() * 1000
import lightgbm as lgb
import numpy

init_ed = time.time() * 1000


def handle(req):
    fun_st = time.time() * 1000
    
    dataset = numpy.loadtxt("/home/app/function/pima-indians-diabetes.csv", delimiter=",")
    X = dataset[:, 0:8]
    Y = dataset[:, 8]

    bst = lgb.Booster(model_file='/home/app/function/model.txt')
    Ypred = bst.predict(X)
    print(numpy.mean((Ypred>0.5)==(Y==1)))
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