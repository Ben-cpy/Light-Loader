import os
import shutil
import rm_unused_pack
assetsDir = {
    "ignorDir" : ["__pycache__", "tests", ".serverless", "pip", "pkg_resources", "setuptools", "wheel", "_distutils_hack", "test"], 

    "ignorSpeDir": [".dist-info"],  
    
    "ignorFile": [".pyc", ".pyi", ".pth", ".virtualenv","_virtualenv.py",".md"],
}

def remove_option(path):
    total_size = 0
    for root , dirs, files in os.walk(path):
        for dir in dirs:
            if dir in assetsDir["ignorDir"]:
                shutil.rmtree(os.path.join(root, dir))
            for dirhouzhui in assetsDir["ignorSpeDir"]:
                if dir.endswith(dirhouzhui):
                    shutil.rmtree(os.path.join(root, dir))

        for name in files:
            for houzhui in assetsDir["ignorFile"]:
                if name.endswith(houzhui):
                    os.remove(os.path.join(root, name))

def get_directory_size(path):
    total_size = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
    return total_size

def remove_unused_pack():
    with open('/home/app/function/handler.py', 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = rm_unused_pack.remove_unused_imports(content)
    with open('/home/app/python/handler.py', 'w', encoding='utf-8') as f1, open('/home/app/function/handler.py', 'w', encoding='utf-8') as f2:
        f1.write(new_content)
        f2.write(new_content)

if __name__ == '__main__':
    pass