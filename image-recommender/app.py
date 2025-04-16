from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import numpy as np
from sklearn.linear_model import Perceptron
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
        cursor.execute("SELECT username, avg_colors FROM profiles")
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
        cursor.execute("SELECT filename, colors FROM files")
        metadata = cursor.fetchall()
        cursor.close()
        conn.close()
        return metadata
    except Error as e:
        logging.error(f"Erreur chargement métadonnées images : {e}")
        return []

def flatten_colors(colors):
    """Transforme une liste de couleurs RGB [[r,g,b], ...] en un seul vecteur 1D"""
    flat = np.array(colors).flatten()
    if len(flat) < 15:  # 5 couleurs * 3 composantes = 15
        flat = np.pad(flat, (0, 15 - len(flat)), 'constant')
    elif len(flat) > 15:
        flat = flat[:15]
    return flat

def recommend_images_for_user(profile, images_metadata):
    try:
        top_colors = json.loads(profile["avg_colors"])
        X_train = []
        y_train = []

        # On crée un vecteur d'entraînement "positif" basé sur le profil
        profile_vector = flatten_colors(top_colors)
        X_train.append(profile_vector)
        y_train.append(1)  # classe positive : correspond au profil

        # Ajout d’un vecteur "négatif" bidon pour permettre apprentissage minimal
        X_train.append(np.random.rand(15))  # bruit
        y_train.append(0)

        clf = Perceptron(max_iter=1000, tol=1e-3)
        clf.fit(X_train, y_train)

        scores = []

        for image in images_metadata:
            image_colors = json.loads(image["colors"])
            if not image_colors:
                continue
            image_vector = flatten_colors(image_colors)
            score = clf.decision_function([image_vector])[0]
            scores.append((image["filename"], score))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_filenames = [filename for filename, _ in scores[:5]]

        logging.info(f"[{profile['username']}] Recommandations : {top_filenames}")
        return top_filenames
    except Exception as e:
        logging.error(f"Erreur dans recommend_images_for_user : {e}")
        return []

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
