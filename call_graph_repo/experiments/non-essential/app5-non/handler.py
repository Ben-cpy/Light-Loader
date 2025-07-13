import time
init_st = time.time() * 1000
import requests
from lxml import html
init_ed = time.time() * 1000
class MockResponse:
    def __init__(self, content):
        self.content = content

def handle(req):
    current_time = time.time() * 1000
    fun_st = time.time() * 1000
    url = "https://www.baidu.coms/"
    # response = requests.request("GET", url)
    mock_resp = MockResponse('dd')
    tree = html.fromstring(mock_resp.content)
    print(tree)
    fun_ed = time.time() * 1000
    return f'lantency is {init_ed - init_st}ms'
