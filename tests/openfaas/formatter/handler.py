import time
init_st = time.time() * 1000
import black
init_ed = time.time() * 1000

# Example usage:
unformatted_code = """
def add(x ,y ):
    return x+ y
"""
# sample input 
# handle('req1')
def handle(req):
    mode = black.FileMode()
    # could use 'req` to replace the unformatted_code
    formatted_code = black.format_str(unformatted_code, mode=mode)
    print(f'formatted code {formatted_code}')
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