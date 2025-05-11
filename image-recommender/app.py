from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import numpy as np
import json
import logging
import redis
import threading
from datetime import datetime
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("ImageRecommender").getOrCreate()
sc = spark.sparkContext

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

        cursor.execute("SELECT username, avg_colors, avg_width, avg_height, favorite_tags FROM profiles")
        profiles = cursor.fetchall()

        cursor.execute("SELECT filename, colors, width, height, tags FROM files")
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

def compute_similarity(user_vector, image_vector, user_tags, image_tags):
    # Distance euclidienne sur les vecteurs
    color_distance = np.linalg.norm(user_vector[:15] - image_vector[:15])
    size_distance = np.linalg.norm(user_vector[15:] - image_vector[15:])

    # Similarité de tags (bonus si intersection)
    user_tags_set = set(user_tags)
    image_tags_set = set(image_tags)
    intersection = user_tags_set.intersection(image_tags_set)
    tag_bonus = len(intersection) * -5  # réduire distance pour correspondance de tags

    return color_distance + size_distance + tag_bonus

def generate_recommendations(user_id):
    profiles, images_metadata = fetch_profiles_and_images()
    logger.info(f"Recommandations avec MapReduce pour user_id={user_id}")

    profile = next((p for p in profiles if p["username"] == user_id), None)
    if not profile:
        logger.warning(f"Aucun profil trouvé pour user_id={user_id}")
        return

    try:
        history = set(get_recommendation_history(user_id))
        disliked = set(get_disliked_images(user_id))

        user_colors = json.loads(profile["avg_colors"])
        user_vector = np.concatenate([
            flatten_colors(user_colors),
            [profile["avg_width"] or 0, profile["avg_height"] or 0]
        ])
        user_tags = json.loads(profile["favorite_tags"])

        user_vector_b = sc.broadcast(user_vector)
        user_tags_b = sc.broadcast(user_tags)

        rdd = sc.parallelize(images_metadata)

        filtered_vectors = (
            rdd.filter(lambda img: img["filename"] not in history and img["filename"] not in disliked)
               .map(lambda img: (
                    img["filename"],
                    np.concatenate([
                        flatten_colors(json.loads(img["colors"])),
                        [img.get("width") or 0, img.get("height") or 0]
                    ]),
                    json.loads(img["tags"]) if img.get("tags") else []
                ))
        )

        distances = (
            filtered_vectors.map(lambda x: (x[0], compute_similarity(user_vector_b.value, x[1], user_tags_b.value, x[2])))
        )

        # Utilisation de reduce pour trouver les meilleures recommandations
        top_n = distances.takeOrdered(NUM_RECOMMENDATIONS, key=lambda x: x[1])
        recommended_files = [filename for filename, _ in top_n]

        logger.info(f"[{user_id}] Recommandations MapReduce : {recommended_files}")
        store_recommendations(user_id, recommended_files)
    except Exception as e:
        logger.error(f"Erreur MapReduce recommandation user_id={user_id} : {e}")

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
