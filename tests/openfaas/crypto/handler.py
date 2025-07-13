import time
init_st = time.time() * 1000
from cryptography.fernet import Fernet
init_ed = time.time() * 1000
def handle(req):
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(b"a secret message")
    decoded_msg = f.decrypt(token)
    # print(decoded_msg)
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

handle("1")