import time 
init_st = time.time() * 1000
import spacy
# named_entity_recognition
init_ed = time.time() * 1000
def handle(req):
    text = "Google was founded in 1998 by Larry Page and Sergey Brin in California."
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    print(entities)
    # simulate_cold_start()
    return f'latency is {init_ed-init_st} ms'

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
