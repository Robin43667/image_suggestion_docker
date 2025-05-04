# manager/services/image_service.py
import os
import base64
from config import IMAGE_DIRECTORY

def list_all_images():
    image_list = []

    for filename in os.listdir(IMAGE_DIRECTORY):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_data = encode_image(filename)
            image_list.append(image_data)

    return image_list

def encode_image(filename):
    filepath = os.path.join(IMAGE_DIRECTORY, filename)
    with open(filepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        mime_type = "image/jpeg" if filename.lower().endswith(("jpg", "jpeg")) else "image/png"
        
        return {
            "filename": filename,
            "content": encoded_string,
            "mimeType": mime_type
        }