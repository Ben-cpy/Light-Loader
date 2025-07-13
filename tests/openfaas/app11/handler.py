import time
import os
import pickle
import gzip
init_st = time.time() * 1000
import pandas as pd
import numpy as np
from sklearn import naive_bayes
from sklearn.metrics import confusion_matrix
from sklearn.feature_extraction.text import CountVectorizer
init_ed = time.time() * 1000
# 定义类别映射
CLASSES = {
    0: "negative",
    4: "positive"
}

# 模型文件路径
MODEL_FILE = '/home/app/function/model.dat.gz'


# 加载模型
with gzip.open(MODEL_FILE, 'rb') as f:
    MODEL = pickle.load(f, encoding='bytes')


def predict(text):
    x_vector = MODEL.vectorizer.transform([text])
    y_predicted = MODEL.predict(x_vector)
    return CLASSES.get(y_predicted[0], "unknown")

def handle(req):


    try:
        import json
        request_json = json.loads(req)
        text = request_json.get("text", "This function is awesome")
    except json.JSONDecodeError:
        # 如果解析失败，使用默认文本
        text = "This function is awesome"

    prediction = predict(text)
    print(f"Prediction: {prediction}")

    fun_ed = time.time() * 1000

    response = (
        f"Prediction:{prediction}"
    )
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