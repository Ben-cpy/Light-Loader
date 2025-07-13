import time
import mypy
import numpy
import django

def handle(req):
    startTime = time.time()

    print('Hello world\n')

    return{'startTime':int(round(startTime * 1000)),
           'retTime':int(round(time.time() * 1000))}