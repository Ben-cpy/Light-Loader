# {"num_files": 10, "file_size_kb": 128}
import os
import json
import datetime
import shutil
import uuid

# 这个辅助函数来自原始代码，我们可以继续使用它
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

    # 创建一个唯一的临时目录用于本次执行
    # e.g., /tmp/compress-job-a1b2c3d4
    base_dir = f'/tmp/compress-job-{uuid.uuid4()}'
    # 压缩包的路径
    archive_path_base = f'{base_dir}/archive' # shutil 会自动添加 .zip 后缀

    try:
        # 2. 生成模拟数据
        os.makedirs(base_dir, exist_ok=True)
        # 生成一些随机内容用于填充文件
        random_content = os.urandom(1024) # 1KB of random data
        for i in range(num_files):
            with open(os.path.join(base_dir, f'file_{i}.tmp'), 'wb') as f:
                for _ in range(file_size_kb):
                    f.write(random_content)
        
        # 获取生成的数据的总大小
        original_size = parse_directory_size(base_dir)

        # 3. 执行核心压缩逻辑并计时
        compress_begin = datetime.datetime.now()
        shutil.make_archive(archive_path_base, 'zip', root_dir=base_dir)
        compress_end = datetime.datetime.now()

        archive_name = f'{os.path.basename(archive_path_base)}.zip'
        archive_size = os.path.getsize(f'{archive_path_base}.zip')

        # 计算处理时间
        process_time = (compress_end - compress_begin) / datetime.timedelta(microseconds=1)

        # 4. 构建返回结果
        return {
            'result': {
                'simulated': True,
                'original_files': num_files,
                'archive_name': archive_name
            },
            'measurement': {
                'download_time': 0, # 无下载
                'download_size': original_size, # 模拟的原始大小
                'upload_time': 0, # 无上传
                'upload_size': archive_size, # 压缩后的大小
                'compute_time': process_time # 核心的压缩时间
            }
        }
    finally:
        # 5. 清理临时文件和目录
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)