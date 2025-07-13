import time
init_st = time.time() * 1000
import audioread
import numpy as np
init_ed = time.time() * 1000


def handle(req):
    with audioread.audio_open('/home/app/function/demo.mp3') as f:
        print(f"Channels: {f.channels}")
        print(f"Sample Rate: {f.samplerate} Hz")
        print(f"Duration: {f.duration} seconds")

        for buf in f:
            audio_data = np.frombuffer(buf, dtype=np.int16)
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