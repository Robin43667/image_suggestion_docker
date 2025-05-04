# from flask import Flask
# import mysql.connector
# from mysql.connector import Error
# import numpy as np
# from sklearn.linear_model import Perceptron
# import json
# import logging
# import redis
# import threading

# app = Flask(__name__)

# DB_CONFIG = {
#     "host": "mariadb",
#     "user": "root",
#     "password": "root",
#     "database": "imageDB"
# }

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# r = redis.Redis(host='redis', port=6379, decode_responses=True)

# def get_db_connection():
#     return mysql.connector.connect(**DB_CONFIG)

# def fetch_profiles_and_images():
#     """Charge tous les profils et métadonnées dimages en une seule fois"""
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
        
#         cursor.execute("SELECT username, avg_colors FROM profiles")
#         profiles = cursor.fetchall()
        
#         cursor.execute("SELECT filename, colors FROM files")
#         images_metadata = cursor.fetchall()
        
#         cursor.close()
#         conn.close()
#         return profiles, images_metadata
#     except Error as e:
#         logger.error(f"Erreur chargement DB : {e}")
#         return [], []

# def flatten_colors(colors):
#     """Transforme une liste de couleurs RGB [[r,g,b], ...] en un vecteur 1D de taille 15"""
#     flat = np.array(colors).flatten()
#     return np.pad(flat, (0, max(0, 15 - len(flat))))[:15]

# def generate_recommendations(user_id):
#     profiles, images_metadata = fetch_profiles_and_images()
#     logger.info(f"Recommandations pour user_id={user_id}")

#     profile = next((p for p in profiles if p["username"] == user_id), None)
#     if not profile:
#         logger.warning(f"Aucun profil trouvé pour user_id={user_id}")
#         return

#     try:
#         user_colors = json.loads(profile["avg_colors"])
#         user_vector = flatten_colors(user_colors)

#         X_train = [user_vector, np.random.rand(15)]
#         y_train = [1, 0]

#         clf = Perceptron(max_iter=1000, tol=1e-3)
#         clf.fit(X_train, y_train)

#         scores = []
#         for image in images_metadata:
#             image_colors = json.loads(image["colors"])
#             if not image_colors:
#                 continue
#             image_vector = flatten_colors(image_colors)
#             score = clf.decision_function([image_vector])[0]
#             scores.append((image["filename"], score))

#         scores.sort(key=lambda x: x[1], reverse=True)
#         top_filenames = [filename for filename, _ in scores[:5]]

#         logger.info(f"[{user_id}] Top recommandations : {top_filenames}")
#     except Exception as e:
#         logger.error(f"Erreur recommandation user_id={user_id} : {e}")

# def redis_listener():
#     pubsub = r.pubsub()
#     pubsub.subscribe('user.updated')
#     logger.info("Listening for user.updated events...")

#     for message in pubsub.listen():
#         if message['type'] == 'message':
#             user_id = message['data']
#             generate_recommendations(user_id)

# if __name__ == "__main__":
#     threading.Thread(target=redis_listener, daemon=True).start()
#     app.run(host="0.0.0.0", port=5005)




from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
import numpy as np
from sklearn.linear_model import Perceptron
import json
import logging
import redis
import threading

app = Flask(__name__)

# Configuration base de données MariaDB
DB_CONFIG = {
    "host": "mariadb",
    "user": "root",
    "password": "root",
    "database": "imageDB"
}

# Configuration Redis (cache)
REDIS_HOST = 'redis'
REDIS_PORT = 6379
RECOMMENDATION_TTL = 900  # secondes (15 minutes)

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connexion Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_profiles_and_images():
    """Charge tous les profils et métadonnées d'images en une seule fois"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT username, avg_colors FROM profiles")
        profiles = cursor.fetchall()

        cursor.execute("SELECT filename, colors FROM files")
        images_metadata = cursor.fetchall()

        cursor.close()
        conn.close()
        return profiles, images_metadata
    except Error as e:
        logger.error(f"Erreur chargement DB : {e}")
        return [], []

def flatten_colors(colors):
    """Transforme une liste de couleurs RGB [[r,g,b], ...] en un vecteur 1D de taille 15"""
    flat = np.array(colors).flatten()
    return np.pad(flat, (0, max(0, 15 - len(flat))))[:15]

def store_recommendations(user_id, recommendations):
    """Stocke les recommandations dans Redis avec expiration"""
    key = f"recommendations:{user_id}"
    r.setex(key, RECOMMENDATION_TTL, json.dumps(recommendations))
    logger.info(f"[{user_id}] Recommandations stockées dans Redis (clé={key})")

def get_recommendations(user_id):
    """Récupère les recommandations stockées pour un utilisateur"""
    key = f"recommendations:{user_id}"
    data = r.get(key)
    if data:
        return json.loads(data)
    return []

def generate_recommendations(user_id):
    profiles, images_metadata = fetch_profiles_and_images()
    logger.info(f"Recommandations pour user_id={user_id}")

    profile = next((p for p in profiles if p["username"] == user_id), None)
    if not profile:
        logger.warning(f"Aucun profil trouvé pour user_id={user_id}")
        return

    try:
        user_colors = json.loads(profile["avg_colors"])
        user_vector = flatten_colors(user_colors)

        X_train = [user_vector, np.random.rand(15)]
        y_train = [1, 0]

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

        logger.info(f"[{user_id}] Top recommandations : {top_filenames}")
        store_recommendations(user_id, top_filenames)
    except Exception as e:
        logger.error(f"Erreur recommandation user_id={user_id} : {e}")

def redis_listener():
    """Écoute les événements 'user.updated' dans Redis et génère les recommandations"""
    pubsub = r.pubsub()
    pubsub.subscribe('user.updated')
    logger.info("Listening for user.updated events...")

    for message in pubsub.listen():
        if message['type'] == 'message':
            user_id = message['data']
            logger.info(f"Événement reçu : user.updated -> {user_id}")
            generate_recommendations(user_id)

@app.route("/recommendations/<user_id>", methods=["GET"])
def recommendations_endpoint(user_id):
    """Endpoint pour récupérer les recommandations d'un utilisateur"""
    recos = get_recommendations(user_id)
    if not recos:
        logger.info(f"[{user_id}] Aucune recommandation trouvée dans Redis")
        return jsonify({"status": "empty", "recommendations": []}), 404
    logger.info(f"[{user_id}] Recommandations retournées au frontend : {recos}")
    return jsonify({"status": "ok", "recommendations": recos}), 200

if __name__ == "__main__":
    threading.Thread(target=redis_listener, daemon=True).start()
    app.run(host="0.0.0.0", port=5005)
