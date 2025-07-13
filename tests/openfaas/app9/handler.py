# handler.py
import json
import time
import os
init_st = time.time() * 1000
import pandas as pd
import numpy as np
import pickle
import logging
init_ed = time.time() * 1000

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 加载模型
MODEL_PATH = '/home/app/function/model.pkl'

def load_model():
    logger.info("Loading into memory...")
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

model = load_model()


def handle(req):
    fun_st = time.time() * 1000
    event = {
        "fixed acidity": 7.4,
        "volatile acidity": 0.7,
        "citric acid": 0.0,
        "residual sugar": 1.9,
        "chlorides": 0.076,
        "free sulfur dioxide": 11.0,
        "total sulfur dioxide": 34.0,
        "density": 0.9978,
        "pH": 3.51,
        "sulphates": 0.56,
        "alcohol": 9.4
    }
    # Ensure all input features are floating point numbers (this step is still important)
    input_features = {key: [float(value)] for key, value in event.items()}

    input_df = pd.DataFrame(input_features)

    logger.info("input is ")
    logger.info(str(input_df))

    logger.info("Predicting wine quality...")
    predicted_quality = model.predict(input_df)
    prediction = str(np.round(predicted_quality[0], 1))
    logger.info(f"Prediction result: {prediction}")

    fun_ed = time.time() * 1000
    response = {
        "prediction": prediction,
        "InitStart": init_st,
        "InitEnd": init_ed,
        "FunctionStart": fun_st,
        "FunctionEnd": fun_ed
    }
    # simulate_cold_start()  
    # return json.dumps(response)
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

# example input
# {
#     "fixed acidity": 7.4,
#     "volatile acidity": 0.7,
#     "citric acid": 0.0,
#     "residual sugar": 1.9,
#     "chlorides": 0.076,
#     "free sulfur dioxide": 11.0,
#     "total sulfur dioxide": 34.0,
#     "density": 0.9978,
#     "pH": 3.51,
#     "sulphates": 0.56,
#     "alcohol": 9.4
# }