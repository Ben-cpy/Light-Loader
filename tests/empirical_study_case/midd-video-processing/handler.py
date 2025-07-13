# {"filename": "cat.jpg", "width": 150, "height": 150}
import datetime
import io
import json
import os
from PIL import Image

# The image processing function remains the same.
def resize_image(image_bytes, w, h):
    """Resizes an image using Pillow, operating entirely in memory."""
    with Image.open(io.BytesIO(image_bytes)) as image:
        image.thumbnail((w, h))
        out_buffer = io.BytesIO()
        image.save(out_buffer, format='JPEG')
        out_buffer.seek(0)
        return out_buffer

def handle(req):
    """
    OpenFaaS handler that processes a file from a fixed path (/home/app/) inside the container.
    If the file is an image, it resizes it. Otherwise, it returns the raw file.
    Performance metrics are returned in the HTTP headers.
    """
    try:
        # --- 1. Parse Input ---
        event = json.loads(req)
        filename = event.get('filename')

        if not filename:
            return json.dumps({"status": "error", "message": "Parameter 'filename' is required."}), 400

        # MODIFICATION: Use a fixed, absolute base path.
        BASE_PATH = '/home/app/function'
        file_path = os.path.join(BASE_PATH, filename)

        if not os.path.exists(file_path):
            return json.dumps({"status": "error", "message": f"File not found at: {file_path}"}), 404

        # --- 2. Read File & Measure Read Time ---
        read_begin = datetime.datetime.now()
        with open(file_path, 'rb') as f:
            original_file_bytes = f.read()
        read_end = datetime.datetime.now()
        read_time_ms = (read_end - read_begin).total_seconds() * 1000

        # --- 3. Conditional Processing ---
        output_data = None
        process_time_ms = 0
        content_type = 'application/octet-stream' # Default content type

        # MODIFICATION: Check if the requested file is an image
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif')
        if filename.lower().endswith(image_extensions):
            # It's an image, so process it
            width = int(event.get('width', 100))
            height = int(event.get('height', 100))
            
            process_begin = datetime.datetime.now()
            resized_image_buffer = resize_image(original_file_bytes, width, height)
            process_end = datetime.datetime.now()
            
            process_time_ms = (process_end - process_begin).total_seconds() * 1000
            output_data = resized_image_buffer.getvalue()
            content_type = 'image/jpeg'
        else:
            # It's not a recognized image, return the original file bytes
            output_data = original_file_bytes
            # Set content type for other known types
            if filename.lower().endswith('.mp3'):
                content_type = 'audio/mpeg'

        # --- 4. Prepare Response ---
        headers = {
            'Content-Type': content_type,
            'X-Read-Time-Ms': str(read_time_ms),
            'X-Compute-Time-Ms': str(process_time_ms),
            'X-Original-Size-Bytes': str(len(original_file_bytes)),
            'X-Processed-Size-Bytes': str(len(output_data))
        }

        return output_data, 200, headers

    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "Invalid JSON input."}), 400
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}), 500