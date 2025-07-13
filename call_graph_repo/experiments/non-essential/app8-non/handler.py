import time
init_st = time.time() * 1000
import PIL
import cv2
import numpy
init_ed = time.time() * 1000

def handle(req):
    fun_st = time.time() * 1000
    print("cv2")
    fun_ed = time.time() * 1000
    return f"lantency is {init_ed-init_st}ms"
