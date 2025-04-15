from flask import Flask, request, jsonify
import os
import requests
from mysql.connector import connect, Error

app = Flask(__name__)

DB_HOST = "mariadb"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "imageDB"

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

@app.route("/collect", methods=["POST"])
def collect():
    data = request.get_json()
    urls = data.get("urls", [])
    prefix = data.get("prefix", "img")
    dossier_telechargement = "./dataset/"

    os.makedirs(dossier_telechargement, exist_ok=True)

    for i, url_image in enumerate(urls):
        try:
            headers = {'User-Agent': 'MonProgrammePython/1.0 (test@example.com)'}
            response = requests.get(url_image, stream=True, headers=headers)
            response.raise_for_status()
            filename = os.path.join(dossier_telechargement, f"{prefix}_{i+1}.jpg")
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            save_image_url_to_db(url_image)
            print(f"Téléchargée : {filename}")
        except Exception as e:
            print(f"Erreur téléchargement {url_image} : {e}")

    return jsonify({"status": "success", "message": f"{len(urls)} images téléchargées"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
