import os
import json
import torch
from torchvision import transforms
from torchvision.models import resnet50
from PIL import Image

# 本地文件路径
local_path = "/home/app/"  # 根据您的环境调整
# local_path = "/home/chenpengyu/openfaas-la/img-recg"
model = None
idx2label = None

def initialize():
    global model, idx2label
    # 加载数据集
    with open(os.path.join(local_path, "imagenet_class_index.json"), 'r') as f:
        class_idx = json.load(f)
    idx2label = [class_idx[str(k)][1] for k in range(len(class_idx))]

    # 加载模型
    model = resnet50(pretrained=False)
    model.load_state_dict(torch.load(os.path.join(local_path, "resnet50.pth"), map_location=torch.device('cpu')))
    model.eval()

def handle(req):
    global model, idx2label

    # 如果模型尚未加载，则初始化
    if model is None:
        initialize()

    # 加载图像
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
    input_batch = input_tensor.unsqueeze(0)  # 创建 mini-batch

    with torch.no_grad():
        output = model(input_batch)

    _, index = torch.max(output, 1)
    ret = idx2label[index.item()]
    results = f"Prediction: index {index.item()}, class {ret}"

    return {
        "result": results
    }

# 初始化模型和数据集
initialize()

if __name__ == "__main__":
    print(handle(None))
