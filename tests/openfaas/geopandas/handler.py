import time
init_st = time.time() * 1000
import geopandas as gpd
init_ed = time.time() * 1000
def handle(req):
    shapefile_path = "/home/app/function/ne_10m_admin_0_countries.shp"
    gdf = gpd.read_file(shapefile_path)
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