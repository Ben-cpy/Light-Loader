# 2
from time import sleep

def handle(req):
    # start timing
    sleep(req)
    return { 'result': req }
