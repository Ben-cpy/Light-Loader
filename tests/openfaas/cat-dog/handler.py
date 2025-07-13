import time
init_st = time.time() * 1000
import json
import torch
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image
init_ed = time.time() * 1000
import io
import base64
import os
# Load the pre-trained model and weights
weights = ResNet18_Weights.DEFAULT
model = resnet18(weights=weights)
model.eval()

# Get the preprocessing method
preprocess = weights.transforms()

# Get the class labels
class_labels = weights.meta['categories']

def handle(req):


    # Specify the path to the image
    image_path = '/home/app/function/cat.jpg'

    # Open and convert the image
    image = Image.open(image_path).convert('RGB')
    # Apply preprocessing
    image = preprocess(image).unsqueeze(0)
    # Perform inference
    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)
        predicted_class = class_labels[predicted.item()]
        predicted_class_lower = predicted_class.lower()
        if 'dog' in predicted_class_lower:
            label = 'dog'
        elif 'cat' in predicted_class_lower:
            label = 'cat'
        else:
            label = 'neither'
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