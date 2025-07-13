import time
import os
import tempfile
init_st = time.time() * 1000
from skimage import io
import requests
import skimage.segmentation as segmentation
import numpy as np
init_ed = time.time() * 1000

def handle(req):
    # get from internet
    # url = 'https://pics4.baidu.com/feed/279759ee3d6d55fb477bdf1aab3f914720a4dd7d.jpeg@f_auto?token=b6acb14069bb0ed844eee5353aec95f1'
    # response = requests.get(url)
    
    # with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
    #     temp_file.write(response.content)
    #     temp_file_path = temp_file.name
    
    # get from local
    temp_file_path = "./cat.jpg"
    
    img = io.imread(temp_file_path)
    os.unlink(temp_file_path)  # 
    # Use Felzenszwalb's algorithm for image segmentation
    segments = segmentation.felzenszwalb(img, scale=100, sigma=0.5, min_size=50)
    
    # Calculate the number of segmented regions
    num_segments = len(np.unique(segments))
    
    # Create a boundary image from the segmentation result
    boundaries = segmentation.mark_boundaries(img, segments)
    
    # Save the result to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as output_file:
        io.imsave(output_file.name, (boundaries * 255).astype(np.uint8))
        output_path = output_file.name
    # simulate_cold_start() 
    # return f'Image segmented into {num_segments} regions. Segmentation result saved at {output_path}. Latency is {init_ed - init_st}ms'
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