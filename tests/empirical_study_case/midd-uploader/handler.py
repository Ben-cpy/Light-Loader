# json format
# {"url": "http://ipv4.download.thinkbroadband.com/5MB.zip"}
import datetime
import hashlib
import json
import os
import urllib.request
import uuid

def handle(req):
    """
    OpenFaaS handler that downloads a file from a given URL, calculates its
    size and MD5 hash, and returns these metrics.

    Args:
        req (str): A JSON string with the following format:
                   {
                       "url": "http://ipv4.download.thinkbroadband.com/5MB.zip"
                   }
    """
    try:
        event = json.loads(req)
        url = event.get('url')

        if not url:
            return json.dumps({"status": "error", "message": "Parameter 'url' is required."}), 400

        # Create a unique temporary filename to avoid conflicts
        name = os.path.basename(url)
        download_path = f"/tmp/{uuid.uuid4()}-{name}"

        # --- Download Phase ---
        download_begin = datetime.datetime.now()
        urllib.request.urlretrieve(url, filename=download_path)
        download_end = datetime.datetime.now()
        
        # --- Analysis Phase ---
        # This part runs after download, we can call it 'compute'
        compute_begin = datetime.datetime.now()
        
        # Get file size
        file_size = os.path.getsize(download_path)
        
        # Calculate MD5 hash for integrity check
        md5_hash = hashlib.md5()
        with open(download_path, "rb") as f:
            # Read in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        file_hash = md5_hash.hexdigest()
        
        compute_end = datetime.datetime.now()

        # --- Cleanup ---
        # It's crucial to remove the temporary file
        os.remove(download_path)

        # --- Prepare Response ---
        download_time = (download_end - download_begin) / datetime.timedelta(microseconds=1)
        compute_time = (compute_end - compute_begin) / datetime.timedelta(microseconds=1)

        result = {
            'result': {
                'source_url': url,
                'file_size_bytes': file_size,
                'md5_hash': file_hash
            },
            'measurement': {
                'download_time': download_time,
                'compute_time': compute_time
            }
        }

        return json.dumps(result), 200

    except urllib.error.URLError as e:
        return json.dumps({"status": "error", "message": f"URL Error: {e.reason}"}), 400
    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "Invalid JSON input."}), 400
    except Exception as e:
        # Clean up in case of error after download but before remove
        if 'download_path' in locals() and os.path.exists(download_path):
            os.remove(download_path)
        return json.dumps({"status": "error", "message": str(e)}), 500