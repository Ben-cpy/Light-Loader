from datetime import date
from pprint import pformat,pprint
import time

init_st = time.time() * 1000
from marshmallow import Schema, fields
init_ed = time.time() * 1000
class ArtistSchema(Schema):
    name = fields.Str()

class AlbumSchema(Schema):
    title = fields.Str()
    release_date = fields.Date()
    artist = fields.Nested(ArtistSchema())

# sample input
# handle('input1')
def handle(req):
    current_time = time.time() * 1000
    bowie = dict(name="David Bowie")
    album = dict(artist=bowie, title="Hunky Dory", release_date=date(1971, 12, 17))
    schema = AlbumSchema()
    result = schema.dump(album)
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