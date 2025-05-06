# from flask import Flask, jsonify
# import mysql.connector
# from mysql.connector import Error
# import numpy as np
# from sklearn.neighbors import NearestNeighbors
# import json
# import logging
# import redis
# import threading
# from datetime import datetime

# app = Flask(__name__)

# DB_CONFIG = {
#     "host": "mariadb",
#     "user": "root",
#     "password": "root",
#     "database": "imageDB"
# }

# REDIS_HOST = 'redis'
# REDIS_PORT = 6379
# RECOMMENDATION_TTL = 900
# NUM_RECOMMENDATIONS = 1
# HISTORY_TTL = 60 * 60 * 24 # 1 jours

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# def get_db_connection():
#     return mysql.connector.connect(**DB_CONFIG)

# def fetch_profiles_and_images():
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
#     flat = np.array(colors).flatten()
#     return np.pad(flat, (0, max(0, 15 - len(flat))))[:15]

# def store_recommendations(user_id, recommendations):
#     key = f"recommendations:{user_id}"
#     r.setex(key, RECOMMENDATION_TTL, json.dumps(recommendations))
#     logger.info(f"[{user_id}] Recommandations stockées dans Redis (clé={key})")

# def get_recommendations(user_id):
#     key = f"recommendations:{user_id}"
#     data = r.get(key)
#     if data:
#         recommendations = json.loads(data)
#         history_key = f"history:{user_id}"
#         for img in recommendations:
#             r.zadd(history_key, {img: datetime.now().timestamp()})
#         r.expire(history_key, HISTORY_TTL)
#         return recommendations
#     return []

# def get_recommendation_history(user_id, max_items=50):
#     history_key = f"history:{user_id}"
#     history = r.zrange(history_key, 0, max_items-1, withscores=True)
#     return [item[0] for item in history]

# def generate_recommendations(user_id):
#     profiles, images_metadata = fetch_profiles_and_images()
#     logger.info(f"Recommandations pour user_id={user_id}")

#     profile = next((p for p in profiles if p["username"] == user_id), None)
#     logger.info(f"profil récupéré={profile}")
#     if not profile:
#         logger.warning(f"Aucun profil trouvé pour user_id={user_id}")
#         return

#     try:
#         # Récupérer l'historique des images déjà recommandées
#         history = get_recommendation_history(user_id)
#         logger.info(f"[{user_id}] Historique de recommandations: {len(history)} images")
        
#         user_colors = json.loads(profile["avg_colors"])
#         user_vector = flatten_colors(user_colors)
        
#         image_vectors = []
#         image_filenames = []
        
#         # Filtrer les images déjà recommandées
#         for image in images_metadata:
#             filename = image["filename"]
#             # Exclure les images déjà vues dans l'historique
#             if filename in history:
#                 continue
                
#             image_colors = json.loads(image["colors"])
#             if not image_colors:
#                 continue
            
#             image_vector = flatten_colors(image_colors)
#             image_vectors.append(image_vector)
#             image_filenames.append(filename)
            
#         if not image_vectors:
#             logger.warning(f"[{user_id}] Toutes les images ont déjà été recommandées ou pas de données de couleur")
#             # Si toutes les images ont déjà été vues, on réinitialise pour ne pas bloquer le système
#             image_vectors = []
#             image_filenames = []
            
#             for image in images_metadata:
#                 image_colors = json.loads(image["colors"])
#                 if not image_colors:
#                     continue
#                 image_vector = flatten_colors(image_colors)
#                 image_vectors.append(image_vector)
#                 image_filenames.append(image["filename"])
            
#             logger.info(f"[{user_id}] Réinitialisation de l'historique de recommandation")
            
#         if not image_vectors:
#             logger.warning(f"[{user_id}] Aucune image avec des données de couleur")
#             return
            
#         image_vectors = np.array(image_vectors)
        
#         k_neighbors = min(NUM_RECOMMENDATIONS, len(image_vectors))
#         if k_neighbors == 0:
#             logger.warning(f"[{user_id}] Pas assez d'images disponibles pour recommandation")
#             return
            
#         nn = NearestNeighbors(n_neighbors=k_neighbors, algorithm='auto')
#         nn.fit(image_vectors)
        
#         distances, indices = nn.kneighbors([user_vector], n_neighbors=k_neighbors)
        
#         recommended_files = [image_filenames[idx] for idx in indices[0]]
        
#         logger.info(f"[{user_id}] Top recommandations : {recommended_files}")
#         store_recommendations(user_id, recommended_files)
#     except Exception as e:
#         logger.error(f"Erreur recommandation user_id={user_id} : {e}")

# def redis_listener():
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
#     recos = get_recommendations(user_id)
#     if not recos:
#         logger.info(f"[{user_id}] Aucune recommandation trouvée dans Redis")
#         return jsonify({"status": "empty", "recommendations": []}), 404
    
#     history = get_recommendation_history(user_id)
#     logger.info(f"[{user_id}] Recommandations retournées au frontend : {recos}")
#     logger.info(f"[{user_id}] Historique de recommandations : {len(history)} images")
    
#     return jsonify({
#         "status": "ok", 
#         "recommendations": recos,
#         "history_count": len(history)
#     }), 200

# @app.route("/history/<user_id>", methods=["GET"])
# def history_endpoint(user_id):
#     """Endpoint pour consulter l'historique des recommandations d'un utilisateur"""
#     history = get_recommendation_history(user_id)
#     return jsonify({
#         "status": "ok", 
#         "history": history,
#         "count": len(history)
#     }), 200

# @app.route("/reset_history/<user_id>", methods=["POST"])
# def reset_history_endpoint(user_id):
#     """Endpoint pour réinitialiser l'historique des recommandations d'un utilisateur"""
#     history_key = f"history:{user_id}"
#     r.delete(history_key)
#     logger.info(f"[{user_id}] Historique de recommandations réinitialisé")
#     generate_recommendations(user_id)
#     return jsonify({"status": "ok", "message": "Historique réinitialisé"}), 200

# if __name__ == "__main__":
#     threading.Thread(target=redis_listener, daemon=True).start()
#     app.run(host="0.0.0.0", port=5005)







from flask import Flask, jsonify, request
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
NUM_RECOMMENDATIONS = 10
HISTORY_TTL = 60 * 60 * 24
DISLIKED_TTL = 60 * 60 * 24 * 7

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

        # 👉 CHANGEMENT ICI : on n'ajoute que la première image dans l'historique
        if recommendations:
            shown_image = recommendations[0]
            history_key = f"history:{user_id}"
            r.zadd(history_key, {shown_image: datetime.now().timestamp()})
            r.expire(history_key, HISTORY_TTL)

        return recommendations
    return []


def get_recommendation_history(user_id, max_items=50):
    history_key = f"history:{user_id}"
    history = r.zrange(history_key, 0, max_items-1, withscores=True)
    return [item[0] for item in history]

def add_to_disliked(user_id, image_filename):
    disliked_key = f"disliked:{user_id}"
    r.zadd(disliked_key, {image_filename: datetime.now().timestamp()})
    r.expire(disliked_key, DISLIKED_TTL)
    logger.info(f"[{user_id}] Image ajoutée aux non-aimées : {image_filename}")

def get_disliked_images(user_id):
    disliked_key = f"disliked:{user_id}"
    disliked = r.zrange(disliked_key, 0, -1)
    return disliked

def generate_recommendations(user_id):
    profiles, images_metadata = fetch_profiles_and_images()
    logger.info(f"Recommandations pour user_id={user_id}")

    profile = next((p for p in profiles if p["username"] == user_id), None)
    logger.info(f"profil récupéré={profile}")
    if not profile:
        logger.warning(f"Aucun profil trouvé pour user_id={user_id}")
        return

    try:
        history = get_recommendation_history(user_id)
        disliked = get_disliked_images(user_id)
        logger.info(f"[{user_id}] Historique: {len(history)} images, Non-aimées: {len(disliked)} images")
        
        user_colors = json.loads(profile["avg_colors"])
        user_vector = flatten_colors(user_colors)
        
        image_vectors = []
        image_filenames = []
        
        for image in images_metadata:
            filename = image["filename"]
            if filename in history or filename in disliked:
                continue
                
            image_colors = json.loads(image["colors"])
            if not image_colors:
                continue
            
            image_vector = flatten_colors(image_colors)
            image_vectors.append(image_vector)
            image_filenames.append(filename)
            
        if not image_vectors:
            logger.warning(f"[{user_id}] Toutes les images ont déjà été vues ou n'ont pas de données couleur")
            
            reset_options = []
            if history and len(disliked) > 0:
                reset_options.append("history")
            
            if reset_options:
                logger.info(f"[{user_id}] Réinitialisation de {reset_options}")
                
                if "history" in reset_options:
                    image_vectors = []
                    image_filenames = []
                    
                    for image in images_metadata:
                        filename = image["filename"]
                        if filename in disliked:
                            continue
                            
                        image_colors = json.loads(image["colors"])
                        if not image_colors:
                            continue
                        
                        image_vector = flatten_colors(image_colors)
                        image_vectors.append(image_vector)
                        image_filenames.append(filename)
                        
                    history_key = f"history:{user_id}"
                    r.delete(history_key)
                    logger.info(f"[{user_id}] Historique réinitialisé tout en préservant les non-aimées")
            else:
                logger.warning(f"[{user_id}] Impossible de générer de nouvelles recommandations")
                return
            
        if not image_vectors:
            logger.warning(f"[{user_id}] Aucune image disponible pour recommandation")
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
        generate_recommendations(user_id)
        recos = get_recommendations(user_id)
        if not recos:
            return jsonify({"status": "empty", "recommendations": []}), 404
    
    history = get_recommendation_history(user_id)
    disliked = get_disliked_images(user_id)
    logger.info(f"[{user_id}] Recommandations retournées : {recos[0] if recos else 'aucune'}")
    logger.info(f"[{user_id}] Stats: {len(history)} dans l'historique, {len(disliked)} non-aimées")
    
    return jsonify({
        "status": "ok", 
        "recommendations": recos[:1],
        "history_count": len(history),
        "disliked_count": len(disliked)
    }), 200

@app.route("/dislike/<user_id>", methods=["POST"])
def dislike_endpoint(user_id):
    data = request.get_json()
    image = data.get("image")
    
    if not image:
        return jsonify({"status": "error", "message": "Image non spécifiée"}), 400
        
    add_to_disliked(user_id, image)
    
    key = f"recommendations:{user_id}"
    current_recos = r.get(key)
    if current_recos:
        recos = json.loads(current_recos)
        if image in recos:
            recos.remove(image)
            if not recos:
                logger.info(f"[{user_id}] Plus de recommandations après dislike, génération de nouvelles")
                generate_recommendations(user_id)
            else:
                r.setex(key, RECOMMENDATION_TTL, json.dumps(recos))
    
    return jsonify({"status": "ok", "message": "Image marquée comme non-aimée"}), 200

@app.route("/history/<user_id>", methods=["GET"])
def history_endpoint(user_id):
    history = get_recommendation_history(user_id)
    disliked = get_disliked_images(user_id)
    return jsonify({
        "status": "ok", 
        "history": history,
        "disliked": disliked,
        "history_count": len(history),
        "disliked_count": len(disliked)
    }), 200

@app.route("/reset_history/<user_id>", methods=["POST"])
def reset_history_endpoint(user_id):
    history_key = f"history:{user_id}"
    r.delete(history_key)
    logger.info(f"[{user_id}] Historique de recommandations réinitialisé")
    generate_recommendations(user_id)
    return jsonify({"status": "ok", "message": "Historique réinitialisé"}), 200

@app.route("/reset_disliked/<user_id>", methods=["POST"])
def reset_disliked_endpoint(user_id):
    disliked_key = f"disliked:{user_id}"
    r.delete(disliked_key)
    logger.info(f"[{user_id}] Liste des images non-aimées réinitialisée")
    generate_recommendations(user_id)
    return jsonify({"status": "ok", "message": "Images non-aimées réinitialisées"}), 200

if __name__ == "__main__":
    threading.Thread(target=redis_listener, daemon=True).start()
    app.run(host="0.0.0.0", port=5005)