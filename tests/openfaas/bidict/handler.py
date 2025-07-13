import time
init_st = time.time() * 1000
from bidict import bidict
init_ed = time.time() * 1000

def handle(req):
    # Create a bidict object
    my_bidict = bidict({'a': 1, 'b': 2, 'c': 3})
    # Access value by key
    value_of_a = my_bidict['a']
    # Access key by value
    key_of_2 = my_bidict.inverse[2]
    # Add a new key-value pair
    my_bidict['d'] = 4

    # Delete a key-value pair
    del my_bidict['b']

    # Check if a key exists
    key_exists = 'a' in my_bidict

    # Check if a value exists
    value_exists = 3 in my_bidict.inverse

    # Get the number of items in the bidict
    num_items = len(my_bidict)

    # Return a formatted string with the results
    result = f"""
    Value of 'a': {value_of_a}
    Key of 2: {key_of_2}
    Key 'd' added: {my_bidict}
    Key 'b' deleted: {my_bidict}
    Key 'a' exists: {key_exists}
    Value 3 exists: {value_exists}
    Number of items: {num_items}
    Latency is {init_ed - init_st}ms
    """
    
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