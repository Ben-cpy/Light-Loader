import os
import time

def measure_compile_time(filepath):
    try:
        start_time = time.time()
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            code = file.read()
        compile(code, filepath, 'exec')
        end_time = time.time()
        return (end_time - start_time) * 1000  # Convert to milliseconds
    except Exception as e:
        print(f"Error compiling {filepath}: {e}")
        return 0

def main():
    base_dir = '/home/app/python'  # modify to your project root directory according to actual situation
    num_tests = 10
    total_compile_times = []

    for test in range(num_tests):
        print(f"Test {test + 1} of {num_tests}")
        total_compile_time = 0

        # measure compilation time of main.py
        main_file = os.path.join(base_dir, 'main.py')
        if os.path.exists(main_file):
            main_compile_time = measure_compile_time(main_file)
            total_compile_time += main_compile_time
            print(f"Time to compile main.py: {main_compile_time:.2f} ms")
        else:
            print("main.py not found.")

        # traverse directory to find all .py files in packages
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.py') and file != 'main.py':
                    filepath = os.path.join(root, file)
                    compile_time = measure_compile_time(filepath)
                    total_compile_time += compile_time
                    print(f"Time to compile {filepath}: {compile_time:.2f} ms")

        print(f"Total compile time for test {test + 1}: {total_compile_time:.2f} ms")
        total_compile_times.append(total_compile_time)

    average_compile_time = sum(total_compile_times) / num_tests
    print(f"Average compile time over {num_tests} tests: {average_compile_time:.2f} ms")

if __name__ == "__main__":
    main()
