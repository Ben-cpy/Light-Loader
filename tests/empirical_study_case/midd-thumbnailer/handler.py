# {"filename": "cat.jpg","width": 150,"height": 150}
import datetime
import io
import json
import os
from os import path 
from PIL import Image

SCRIPT_DIR = path.abspath(path.join(path.dirname(__file__)))

# The image processing function remains the same, it's already well-optimized.
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
    OpenFaaS handler that resizes a local image file packaged with the function.
    It reads an image from the local filesystem, resizes it, and returns the
    raw image bytes in the HTTP response. Performance metrics are returned
    in the HTTP headers.

    Args:
        req (str): A JSON string specifying the local filename and dimensions.
                   Example:
                   {
                       "filename": "cat.jpg",
                       "width": 150,
                       "height": 150
                   }
    """
    try:
        # --- 1. Parse Input ---
        event = json.loads(req)
        filename = event.get('filename')
        width = int(event.get('width', 100))
        height = int(event.get('height', 100))

        if not filename:
            return json.dumps({"status": "error", "message": "Parameter 'filename' is required."}), 400

        # Define the path where images are stored inside the container
        # This path is relative to the function's root directory
        image_path = os.path.join(SCRIPT_DIR, filename)

        if not os.path.exists(image_path):
            return json.dumps({"status": "error", "message": f"File not found: {filename}"}), 404

        # --- 2. Core Logic & Performance Measurement ---
        # Measure local file read time
        read_begin = datetime.datetime.now()
        with open(image_path, 'rb') as f:
            original_image_bytes = f.read()
        read_end = datetime.datetime.now()

        # Measure image processing time
        process_begin = datetime.datetime.now()
        resized_image_buffer = resize_image(original_image_bytes, width, height)
        process_end = datetime.datetime.now()

        # --- 3. Prepare Response ---
        read_time_ms = (read_end - read_begin).total_seconds() * 1000
        process_time_ms = (process_end - process_begin).total_seconds() * 1000
        
        # Get the raw bytes to return
        image_data = resized_image_buffer.getvalue()

        # Create custom headers for performance metrics
        headers = {
            'Content-Type': 'image/jpeg',
            'X-Read-Time-Ms': str(read_time_ms),
            'X-Compute-Time-Ms': str(process_time_ms),
            'X-Original-Size-Bytes': str(len(original_image_bytes)),
            'X-Resized-Size-Bytes': str(len(image_data))
        }

        # Return raw image data with a 200 OK status and custom headers
        return image_data, 200, headers

    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "Invalid JSON input."}), 400
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}), 500