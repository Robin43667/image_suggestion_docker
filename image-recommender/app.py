from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
import json
import logging

app = Flask(__name__)

DB_HOST = "mariadb"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "imageDB"

logging.basicConfig(level=logging.INFO)

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def load_profiles():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT username, avg_width, avg_height, avg_colors FROM profiles")
        profiles = cursor.fetchall()
        cursor.close()
        conn.close()
        return profiles
    except Error as e:
        logging.error(f"Erreur chargement profils : {e}")
        return []

def load_images_metadata():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT filename, width, height, colors FROM files")
        metadata = cursor.fetchall()
        cursor.close()
        conn.close()
        return metadata
    except Error as e:
        logging.error(f"Erreur chargement métadonnées images : {e}")
        return []

def recommend_images_for_user(profile, images_metadata):
    top_colors = json.loads(profile["avg_colors"])
    top_colors_array = np.array(top_colors)

    if top_colors_array.shape[0] < 5:
        top_colors_array = np.tile(top_colors_array, (5 // len(top_colors), 1))[:5]
    elif top_colors_array.shape[0] > 5:
        top_colors_array = top_colors_array[:5]

    recommendations = []

    for image in images_metadata:
        image_colors = json.loads(image["colors"])
        if not image_colors:
            continue
        image_color_array = np.array(image_colors)
        distances = euclidean_distances(image_color_array, top_colors_array)
        score = np.mean(distances)
        recommendations.append((image["filename"], score))

    recommendations.sort(key=lambda x: x[1])
    top_filenames = [filename for filename, _ in recommendations[:5]]

    logging.info(f"[{profile['username']}] Recommandations : {top_filenames}")
    return top_filenames

@app.route("/recommend", methods=["GET"])
def recommend():
    profiles = load_profiles()
    images_metadata = load_images_metadata()

    if not profiles or not images_metadata:
        return jsonify({"status": "error", "message": "Pas de profils ou images disponibles"}), 500

    for profile in profiles:
        recommend_images_for_user(profile, images_metadata)

    return jsonify({"status": "success", "message": "Recommandations générées (voir logs)"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
