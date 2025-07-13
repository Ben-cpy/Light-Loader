# generate different py file
import time
import py_compile



def generate_class_definition(class_name):
    return f"""
class {class_name}:
    def __init__(self, name):
        self.name = name

    def meow(self):
        return f'{{self.name}} says meow!'

    def purr(self):
        return f'{{self.name}} is purring.'

    def sleep(self):
        return f'{{self.name}} is sleeping.'
"""

# generate different py file
import time
import py_compile



def generate_class_definition(class_name):
    return f"""
class {class_name}:
    def __init__(self, name):
        self.name = name

    def meow(self):
        return f'{{self.name}} says meow!'

    def purr(self):
        return f'{{self.name}} is purring.'

    def sleep(self):
        return f'{{self.name}} is sleeping.'
"""


def generate_python_file(file_name, num_classes):
    with open(file_name, 'w') as f:
        for i in range(1, num_classes + 1):
            class_name = f"CuteCat{i}"
            class_definition = generate_class_definition(class_name)
            f.write(class_definition)


# -----------------------------
# for test 
def measure_compile_time(file_path):
    start_time = time.time()
    py_compile.compile(file_path)
    end_time = time.time()
    return (end_time - start_time) * 1000  # milliseconds



if __name__ == "__main__":
    # generate_python_file("/home/chenpengyu/cute500.py", 500)
    cute50_time = measure_compile_time("/home/chenpengyu/cute50.py")
    cute500_time = measure_compile_time("/home/chenpengyu/cute500.py")

    print(f"Compile time for cute50.py: {cute50_time:.6f} ms")
    print(f"Compile time for cute500.py: {cute500_time:.6f} ms")
