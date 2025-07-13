import time
init_st = time.time() * 1000
import requests
from lxml import html
init_ed = time.time() * 1000
def handle():
    url = "https://www.baidu.com/"
    response = requests.request("GET", url)
    tree = html.fromstring(response.content)
    return f'lantency is {init_ed - init_st}ms'
