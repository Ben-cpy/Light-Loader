import os
import json
import torch
from torchvision import transforms
from torchvision.models import resnet50
from PIL import Image

local_path = "/home/app/"  
# local_path = "/home/chenpengyu/openfaas-la/img-recg"
model = None
idx2label = None

def initialize():
    global model, idx2label
    with open(os.path.join(local_path, "imagenet_class_index.json"), 'r') as f:
        class_idx = json.load(f)
    idx2label = [class_idx[str(k)][1] for k in range(len(class_idx))]

    model = resnet50(pretrained=False)
    model.load_state_dict(torch.load(os.path.join(local_path, "resnet50.pth"), map_location=torch.device('cpu')))
    model.eval()

def handle(req):
    global model, idx2label

    if model is None:
        initialize()

    image_path = os.path.join(local_path, "tesla.jpg")
    input_image = Image.open(image_path).convert('RGB')

    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                             std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0)  

    with torch.no_grad():
        output = model(input_batch)

    _, index = torch.max(output, 1)
    ret = idx2label[index.item()]
    results = f"Prediction: index {index.item()}, class {ret}"

    return {
        "result": results
    }

# Initialize模型和数据集
initialize()

if __name__ == "__main__":
    print(handle(None))
