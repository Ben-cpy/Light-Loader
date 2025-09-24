# {"num_files": 10, "file_size_kb": 128}
import os
import json
import datetime
import shutil
import uuid

def parse_directory_size(directory):
    """Calculates the total size of all files in a directory."""
    size = 0
    for root, _, files in os.walk(directory):
        for file in files:
            size += os.path.getsize(os.path.join(root, file))
    return size

def handle(req):
    """
    Simulates a compression task by generating local files, compressing them,
    and measuring performance. This version has NO external storage dependency.
    Args:
        req (str): request body, expected to be a JSON string
                   e.g., {"num_files": 10, "file_size_kb": 128}
    """
    try:
        # 1. 解析输入，决定要创建多少以及多大的文件
        params = json.loads(req)
        num_files = params.get('num_files', 10)
        file_size_kb = params.get('file_size_kb', 128)
    except (json.JSONDecodeError, TypeError):
        return {"error": "Invalid JSON input. Please provide a JSON object like '{\"num_files\": 10, \"file_size_kb\": 128}'."}, 400

    # e.g., /tmp/compress-job-a1b2c3d4
    base_dir = f'/tmp/compress-job-{uuid.uuid4()}'
    archive_path_base = f'{base_dir}/archive' # shutil 会自动添加 .zip 后缀

    try:
        # 2. 生成模拟数据
        os.makedirs(base_dir, exist_ok=True)
        random_content = os.urandom(1024) # 1KB of random data
        for i in range(num_files):
            with open(os.path.join(base_dir, f'file_{i}.tmp'), 'wb') as f:
                for _ in range(file_size_kb):
                    f.write(random_content)
        
        original_size = parse_directory_size(base_dir)

        # 3. 执行核心压缩逻辑并计时
        compress_begin = datetime.datetime.now()
        shutil.make_archive(archive_path_base, 'zip', root_dir=base_dir)
        compress_end = datetime.datetime.now()

        archive_name = f'{os.path.basename(archive_path_base)}.zip'
        archive_size = os.path.getsize(f'{archive_path_base}.zip')

        process_time = (compress_end - compress_begin) / datetime.timedelta(microseconds=1)

        # 4. 构建返回结果
        return {
            'result': {
                'simulated': True,
                'original_files': num_files,
                'archive_name': archive_name
            },
            'measurement': {
                'download_time': 0, 
                'download_size': original_size, 
                'upload_time': 0, 
                'upload_size': archive_size, 
                'compute_time': process_time 
            }
        }
    finally:
        # 5. 清理临时文件和目录
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)