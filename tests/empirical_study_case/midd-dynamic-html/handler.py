# {"username": "Alex", "random_len": 10}
import json
from datetime import datetime
from random import sample
from os import path
from jinja2 import Template

# SCRIPT_DIR 在 OpenFaaS 容器内通常是 /home/app
SCRIPT_DIR = path.abspath(path.join(path.dirname(__file__)))

def handle(req):
    """
    handle a request to the function
    Args:
        req (str): request body, expected to be a JSON string 
                   e.g., {"username": "Alex", "random_len": 10}
    """
    try:
        # 1. 解析来自请求体的 JSON 输入
        event = json.loads(req)
        name = event.get('username', 'Guest') # 提供一个默认值
        size = event.get('random_len', 5)     # 提供一个默认值
    except (json.JSONDecodeError, TypeError):
        # 如果输入不是有效的 JSON，返回错误信息
        return {"error": "Invalid JSON input. Please provide a JSON object with 'username' and 'random_len'."}, 400

    # 核心逻辑保持不变
    cur_time = datetime.now()
    random_numbers = sample(range(0, 1000000), size)
    
    # 2. 读取模板文件
    # 确保 templates 目录和 handler.py 在同一级
    template_path = path.join(SCRIPT_DIR, 'template.html')
    
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        # 如果模板文件不存在，返回清晰的错误
        return {"error": f"Template file not found at {template_path}. Ensure it is copied in the Dockerfile."}, 500

    template = Template(template_content)
    html = template.render(username=name, cur_time=cur_time, random_numbers=random_numbers)

    # 3. 返回结果 (直接返回 HTML 或包含在 JSON 中均可)
    # OpenFaaS 可以直接处理字符串作为响应体，并自动设置 Content-Type
    # 为了更清晰，我们也可以返回一个字典
    return {
        "result": html
    }