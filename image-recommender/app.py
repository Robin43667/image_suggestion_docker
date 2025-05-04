# from flask import Flask, jsonify
# import mysql.connector
# from mysql.connector import Error
# import numpy as np
# from sklearn.linear_model import Perceptron
# import json
# import logging
# import redis
# import threading

# app = Flask(__name__)

# # Configuration base de données MariaDB
# DB_CONFIG = {
#     "host": "mariadb",
#     "user": "root",
#     "password": "root",
#     "database": "imageDB"
# }

# # Configuration Redis (cache)
# REDIS_HOST = 'redis'
# REDIS_PORT = 6379
# RECOMMENDATION_TTL = 900  # secondes (15 minutes)

# # Logger
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Connexion Redis
# r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# def get_db_connection():
#     return mysql.connector.connect(**DB_CONFIG)

# def fetch_profiles_and_images():
#     """Charge tous les profils et métadonnées d'images en une seule fois"""
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

# def store_recommendations(user_id, recommendations):
#     """Stocke les recommandations dans Redis avec expiration"""
#     key = f"recommendations:{user_id}"
#     r.setex(key, RECOMMENDATION_TTL, json.dumps(recommendations))
#     logger.info(f"[{user_id}] Recommandations stockées dans Redis (clé={key})")

# def get_recommendations(user_id):
#     """Récupère les recommandations stockées pour un utilisateur"""
#     key = f"recommendations:{user_id}"
#     data = r.get(key)
#     if data:
#         return json.loads(data)
#     return []

# def generate_recommendations(user_id):
#     profiles, images_metadata = fetch_profiles_and_images()
#     logger.info(f"Recommandations pour user_id={user_id}")

#     profile = next((p for p in profiles if p["username"] == user_id), None)
#     logger.info(f"profil récupéré={profile}")
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
#         top_filenames = [scores[0][0]] if scores else []

#         logger.info(f"[{user_id}] Top recommandations : {top_filenames}")
#         store_recommendations(user_id, top_filenames)
#     except Exception as e:
#         logger.error(f"Erreur recommandation user_id={user_id} : {e}")

# def redis_listener():
#     """Écoute les événements 'user.updated' dans Redis et génère les recommandations"""
#     pubsub = r.pubsub()
#     pubsub.subscribe('user.updated')
#     logger.info("Listening for user.updated events...")

#     for message in pubsub.listen():
#         if message['type'] == 'message':
#             user_id = message['data']
#             logger.info(f"Événement reçu : user.updated -> {user_id}")
#             generate_recommendations(user_id)

# @app.route("/recommend/<user_id>", methods=["GET"])
# def recommendations_endpoint(user_id):
#     """Endpoint pour récupérer les recommandations d'un utilisateur"""
#     recos = get_recommendations(user_id)
#     if not recos:
#         logger.info(f"[{user_id}] Aucune recommandation trouvée dans Redis")
#         return jsonify({"status": "empty", "recommendations": []}), 404
#     logger.info(f"[{user_id}] Recommandations retournées au frontend : {recos}")
#     return jsonify({"status": "ok", "recommendations": recos}), 200

# if __name__ == "__main__":
#     threading.Thread(target=redis_listener, daemon=True).start()
#     app.run(host="0.0.0.0", port=5005)


from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
import numpy as np
from sklearn.neighbors import NearestNeighbors
import json
import logging
import redis
import threading
from datetime import datetime

app = Flask(__name__)

DB_CONFIG = {
    "host": "mariadb",
    "user": "root",
    "password": "root",
    "database": "imageDB"
}

REDIS_HOST = 'redis'
REDIS_PORT = 6379
RECOMMENDATION_TTL = 900
NUM_RECOMMENDATIONS = 1
HISTORY_TTL = 60 * 60 * 24 # 1 jours

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_profiles_and_images():
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
    flat = np.array(colors).flatten()
    return np.pad(flat, (0, max(0, 15 - len(flat))))[:15]

def store_recommendations(user_id, recommendations):
    key = f"recommendations:{user_id}"
    r.setex(key, RECOMMENDATION_TTL, json.dumps(recommendations))
    logger.info(f"[{user_id}] Recommandations stockées dans Redis (clé={key})")

def get_recommendations(user_id):
    key = f"recommendations:{user_id}"
    data = r.get(key)
    if data:
        recommendations = json.loads(data)
        history_key = f"history:{user_id}"
        for img in recommendations:
            r.zadd(history_key, {img: datetime.now().timestamp()})
        r.expire(history_key, HISTORY_TTL)
        return recommendations
    return []

def get_recommendation_history(user_id, max_items=50):
    history_key = f"history:{user_id}"
    history = r.zrange(history_key, 0, max_items-1, withscores=True)
    return [item[0] for item in history]

def generate_recommendations(user_id):
    profiles, images_metadata = fetch_profiles_and_images()
    logger.info(f"Recommandations pour user_id={user_id}")

    profile = next((p for p in profiles if p["username"] == user_id), None)
    logger.info(f"profil récupéré={profile}")
    if not profile:
        logger.warning(f"Aucun profil trouvé pour user_id={user_id}")
        return

    try:
        # Récupérer l'historique des images déjà recommandées
        history = get_recommendation_history(user_id)
        logger.info(f"[{user_id}] Historique de recommandations: {len(history)} images")
        
        user_colors = json.loads(profile["avg_colors"])
        user_vector = flatten_colors(user_colors)
        
        image_vectors = []
        image_filenames = []
        
        # Filtrer les images déjà recommandées
        for image in images_metadata:
            filename = image["filename"]
            # Exclure les images déjà vues dans l'historique
            if filename in history:
                continue
                
            image_colors = json.loads(image["colors"])
            if not image_colors:
                continue
            
            image_vector = flatten_colors(image_colors)
            image_vectors.append(image_vector)
            image_filenames.append(filename)
            
        if not image_vectors:
            logger.warning(f"[{user_id}] Toutes les images ont déjà été recommandées ou pas de données de couleur")
            # Si toutes les images ont déjà été vues, on réinitialise pour ne pas bloquer le système
            image_vectors = []
            image_filenames = []
            
            for image in images_metadata:
                image_colors = json.loads(image["colors"])
                if not image_colors:
                    continue
                image_vector = flatten_colors(image_colors)
                image_vectors.append(image_vector)
                image_filenames.append(image["filename"])
            
            logger.info(f"[{user_id}] Réinitialisation de l'historique de recommandation")
            
        if not image_vectors:
            logger.warning(f"[{user_id}] Aucune image avec des données de couleur")
            return
            
        image_vectors = np.array(image_vectors)
        
        k_neighbors = min(NUM_RECOMMENDATIONS, len(image_vectors))
        if k_neighbors == 0:
            logger.warning(f"[{user_id}] Pas assez d'images disponibles pour recommandation")
            return
            
        nn = NearestNeighbors(n_neighbors=k_neighbors, algorithm='auto')
        nn.fit(image_vectors)
        
        distances, indices = nn.kneighbors([user_vector], n_neighbors=k_neighbors)
        
        recommended_files = [image_filenames[idx] for idx in indices[0]]
        
        logger.info(f"[{user_id}] Top recommandations : {recommended_files}")
        store_recommendations(user_id, recommended_files)
    except Exception as e:
        logger.error(f"Erreur recommandation user_id={user_id} : {e}")

def redis_listener():
    pubsub = r.pubsub()
    pubsub.subscribe('user.updated')
    logger.info("Listening for user.updated events...")

    for message in pubsub.listen():
        if message['type'] == 'message':
            user_id = message['data']
            logger.info(f"Événement reçu : user.updated -> {user_id}")
            generate_recommendations(user_id)

@app.route("/recommend/<user_id>", methods=["GET"])
def recommendations_endpoint(user_id):
    recos = get_recommendations(user_id)
    if not recos:
        logger.info(f"[{user_id}] Aucune recommandation trouvée dans Redis")
        return jsonify({"status": "empty", "recommendations": []}), 404
    
    history = get_recommendation_history(user_id)
    logger.info(f"[{user_id}] Recommandations retournées au frontend : {recos}")
    logger.info(f"[{user_id}] Historique de recommandations : {len(history)} images")
    
    return jsonify({
        "status": "ok", 
        "recommendations": recos,
        "history_count": len(history)
    }), 200

@app.route("/history/<user_id>", methods=["GET"])
def history_endpoint(user_id):
    """Endpoint pour consulter l'historique des recommandations d'un utilisateur"""
    history = get_recommendation_history(user_id)
    return jsonify({
        "status": "ok", 
        "history": history,
        "count": len(history)
    }), 200

@app.route("/reset_history/<user_id>", methods=["POST"])
def reset_history_endpoint(user_id):
    """Endpoint pour réinitialiser l'historique des recommandations d'un utilisateur"""
    history_key = f"history:{user_id}"
    r.delete(history_key)
    logger.info(f"[{user_id}] Historique de recommandations réinitialisé")
    generate_recommendations(user_id)
    return jsonify({"status": "ok", "message": "Historique réinitialisé"}), 200

if __name__ == "__main__":
    threading.Thread(target=redis_listener, daemon=True).start()
    app.run(host="0.0.0.0", port=5005)