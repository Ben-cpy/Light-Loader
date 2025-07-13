import time
init_st = time.time() * 1000
import cv2
init_ed = time.time() * 1000
# detect the edge in an image
image_path = "/home/app/function/cat.jpg"
def handle(req):
        
    image = cv2.imread(image_path)
    
    # Check if the image was successfully loaded
    if image is None:
        print("Error: Could not open or find the image.")
        return
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Canny edge detection
    edges = cv2.Canny(gray_image, 100, 200)
    cv2.imwrite("./cat_edges.jpg", edges)
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