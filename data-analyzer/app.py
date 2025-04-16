# DATA ANALYZER

from flask import Flask, jsonify
import os
import cv2
import json
import exifread
import mysql.connector
from mysql.connector import Error
from PIL import Image
from sklearn.cluster import KMeans

app = Flask(__name__)

DB_HOST = "mariadb"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "imageDB"

IMAGE_FOLDER = "/app/images/"

# Connexion
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# Création de la table enrichie
def create_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) UNIQUE NOT NULL,
                format VARCHAR(50),
                width INT,
                height INT,
                colors TEXT,
                tags TEXT,
                exifs TEXT
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Table 'files' vérifiée/créée.")
    except Error as e:
        print(f"Erreur lors de la création de la table : {e}")

# Analyse couleurs
def get_dominant_colors(image_path, k=5):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image introuvable : {image_path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (100, 100), interpolation=cv2.INTER_LINEAR)
        image = image.reshape((-1, 3))
        kmeans = KMeans(n_clusters=k, random_state=0, n_init=5)
        kmeans.fit(image)
        colors = kmeans.cluster_centers_.astype(int)
        return [(int(c[0]), int(c[1]), int(c[2])) for c in colors]
    except Exception as e:
        print(f"Erreur analyse couleur {image_path} : {e}")
        return [(0, 0, 0)] * k

# Tags
def generate_tags(metadata):
    tags = set()
    if metadata.get("width") and metadata.get("height"):
        tags.add("#paysage" if metadata["width"] > metadata["height"] else "#portrait")
    if metadata.get("format"):
        tags.add(f"#{metadata['format'].lower()}")
    if "Make" in metadata.get("exifs", {}):
        tags.add(f"#{metadata['exifs']['Make'].lower()}")
    return list(tags)

# Analyse et insertion
def analyze_and_store_files():
    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    files = os.listdir(IMAGE_FOLDER)
    total_processed = 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for file in files:
            if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            full_path = os.path.join(IMAGE_FOLDER, file)
            if not os.path.isfile(full_path):
                continue

            metadata = {
                "filename": file,
                "format": "",
                "width": None,
                "height": None,
                "colors": [],
                "tags": [],
                "exifs": {}
            }

            # PIL pour dimensions/format
            try:
                with Image.open(full_path) as img:
                    metadata["width"], metadata["height"] = img.size
                    metadata["format"] = img.format
            except Exception as e:
                print(f"Erreur ouverture image {file} : {e}")

            # EXIF
            try:
                with open(full_path, 'rb') as f:
                    tags = exifread.process_file(f)
                    for tag in ['Image Make', 'Image Model', 'EXIF DateTimeOriginal']:
                        if tag in tags:
                            key = tag.split()[-1]
                            metadata['exifs'][key] = str(tags[tag])
            except Exception as e:
                print(f"Erreur EXIF {file} : {e}")

            # Couleurs dominantes
            metadata["colors"] = get_dominant_colors(full_path, k=5)
            metadata["tags"] = generate_tags(metadata)

            try:
                cursor.execute("""
                    INSERT INTO files (filename, format, width, height, colors, tags, exifs)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE format=VALUES(format), width=VALUES(width),
                        height=VALUES(height), colors=VALUES(colors), tags=VALUES(tags), exifs=VALUES(exifs)
                """, (
                    metadata["filename"],
                    metadata["format"],
                    metadata["width"],
                    metadata["height"],
                    json.dumps(metadata["colors"]),
                    json.dumps(metadata["tags"]),
                    json.dumps(metadata["exifs"])
                ))
                total_processed += 1
            except Error as e:
                print(f"Erreur DB insertion {file} : {e}")

        conn.commit()
        cursor.close()
        conn.close()

    except Error as e:
        print(f"Erreur connexion DB : {e}")

    return total_processed

@app.route("/analyze", methods=["GET"])
def analyze():
    create_table()
    count = analyze_and_store_files()
    return jsonify({"status": "success", "files_analyzed": count})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
