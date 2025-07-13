import time
init_st = time.time() * 1000
import easyocr
init_ed = time.time() * 1000
def handle(req):
    reader = easyocr.Reader(['ch_sim','en']) # this needs to run only once to load the model into memory
    result = reader.readtext('/home/app/signpost.jpg', detail = 0)
    print(result)
    return f'lantency is {init_ed - init_st}ms'