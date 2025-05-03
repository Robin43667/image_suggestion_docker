from flask import Flask, request, jsonify
import os
import requests
from mysql.connector import connect, Error
from PIL import Image

app = Flask(__name__)

DB_HOST = "mariadb"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "imageDB"

TARGET_WIDTH = 512
TARGET_HEIGHT = 512
IMAGE_QUALITY = 85  # Compression JPEG
MAX_IMAGE_SIZE_BYTES = 20 * 1024 * 1024  

def get_db_connection():
    return connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def save_image_url_to_db(image_url):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO images (url) VALUES (%s)", (image_url,))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Erreur DB : {e}")

def resize_image(image_path):
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img_resized = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
            img_resized.save(image_path, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
            print(f"Redimensionnée : {image_path}")
    except Exception as e:
        print(f"Erreur redimensionnement {image_path} : {e}")

@app.route("/collect", methods=["POST"])
def collect():
    data = request.get_json()
    urls = data.get("urls", [])
    prefix = data.get("prefix", "img")
    dossier_telechargement = "/app/images/"

    os.makedirs(dossier_telechargement, exist_ok=True)

    for i, url_image in enumerate(urls):
        try:
            headers = {'User-Agent': 'MonProgrammePython/1.0 (test@example.com)'}
            response = requests.get(url_image, stream=True, headers=headers)
            response.raise_for_status()

            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > MAX_IMAGE_SIZE_BYTES:
                print(f"Ignorée (trop grosse - {int(content_length) / (1024*1024):.2f} Mo) : {url_image}")
                continue

            filename = os.path.join(dossier_telechargement, f"{prefix}_{i+1}.jpg")
            total_bytes = 0
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    total_bytes += len(chunk)
                    if total_bytes > MAX_IMAGE_SIZE_BYTES:
                        print(f"Abandonnée (taille > 5 Mo en cours de téléchargement) : {url_image}")
                        f.close()
                        os.remove(filename)
                        break
                    f.write(chunk)
                else:
                    resize_image(filename)
                    save_image_url_to_db(url_image)
                    print(f"Téléchargée et redimensionnée : {filename}")

        except Exception as e:
            print(f"Erreur téléchargement {url_image} : {e}")

    return jsonify({"status": "success", "message": f"{len(urls)} images traitées"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
