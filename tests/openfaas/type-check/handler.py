import time
init_st = time.time() * 1000
import cerberus
init_ed = time.time() * 1000
def handle(req):
    schema = {
    'name': {'type': 'string', 'required': True},
    'age': {'type': 'integer', 'required': True},
    }
    validator = cerberus.Validator(schema)
    document = {'name': 'John', 'age': 30}
    validator.validate(document)
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