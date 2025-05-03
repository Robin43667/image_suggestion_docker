# MANAGER

from flask import Flask, jsonify, request, send_from_directory
import os
import requests
import random
import base64
import logging
import mysql.connector
import os
import hashlib

app = Flask(__name__)

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
DATA_COLLECTOR_1_URL = "http://data-collector-1:5001/collect"
DATA_COLLECTOR_2_URL = "http://data-collector-2:5001/collect"
USER_PROFILER_URL = "http://user-profiler:5000/profile"
IMAGE_RECOMMENDER_URL = "http://image-recommender:5005/recommend"
IMAGE_DIRECTORY = "/app/images/"

SPARQL_QUERY = """
SELECT ?image
WHERE {
  ?nebuleuse wdt:P31/wdt:P279* wd:Q204194 .
  ?nebuleuse wdt:P18 ?image .
}
LIMIT 100
"""





logger = logging.getLogger(__name__)

# DB config
DB_HOST = "mariadb"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "imageDB"

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def create_users_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE,
                password VARCHAR(255),
                calibrated BOOLEAN DEFAULT FALSE
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Table users vérifiée/créée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la création de la table users : {e}")


def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ':' + key.hex()

def verify_password(stored_password, provided_password):
    salt_hex, key_hex = stored_password.split(':')
    salt = bytes.fromhex(salt_hex)
    stored_key = bytes.fromhex(key_hex)
    new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return new_key == stored_key

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Username et password requis"}), 400
    
    try:
        create_users_table()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Username déjà utilisé"}), 400
        
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                      (username, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"status": "success", "message": "Utilisateur créé avec succès"}), 201
        
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement : {e}")
        return jsonify({"status": "error", "message": "Erreur serveur"}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Username et password requis"}), 400
    
    try:
        create_users_table()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, password, calibrated FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user or not verify_password(user[1], password):
            return jsonify({"status": "error", "message": "Identifiants invalides"}), 401
        
        return jsonify({
            "status": "success", 
            "message": "Connexion réussie",
            "user": {
                "username": user[0],
                "calibrated": bool(user[2])  # On force à booléen Python
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la connexion : {e}")
        return jsonify({"status": "error", "message": "Erreur serveur"}), 500

def fetch_image_urls():
    try:
        response = requests.get(SPARQL_ENDPOINT, params={"query": SPARQL_QUERY, "format": "json"})
        response.raise_for_status()
        data = response.json()
        return [binding["image"]["value"] for binding in data["results"]["bindings"]]
    except Exception as e:
        print(f"Erreur SPARQL : {e}")
        return []

def split_list(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n)]

def send_urls_to_collector(collector_url, urls, prefix):
    try:
        response = requests.post(collector_url, json={"urls": urls, "prefix": prefix})
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Erreur POST vers {collector_url} : {e}")
        return False

@app.route("/start_collection", methods=["GET"])
def start_collection():
    try:
        print("Récupération des URLs depuis Wikidata...")
        urls = fetch_image_urls()
        print(f"{len(urls)} URLs récupérées")

        if not urls:
            return jsonify({"status": "failure", "message": "Aucune URL récupérée"}), 500
        
        urls_sample = random.sample(urls, min(10, len(urls)))
        urls1, urls2 = split_list(urls_sample, 2)
        print("Envoi aux collecteurs...")

        success1 = send_urls_to_collector(DATA_COLLECTOR_1_URL, urls1, "collector1")
        success2 = send_urls_to_collector(DATA_COLLECTOR_2_URL, urls2, "collector2")

        if success1 and success2:
            return jsonify({"status": "success", "message": "Collecte répartie et lancée"})
        else:
            return jsonify({"status": "partial_failure", "message": "Erreur avec un des collecteurs"}), 500
    except Exception as e:
        print(f"Erreur inattendue dans start_collection : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route("/list-images", methods=["GET"])
def list_images():
    try:
        image_list = []

        for filename in os.listdir(IMAGE_DIRECTORY):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(IMAGE_DIRECTORY, filename)
                with open(filepath, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    image_list.append({
                        "filename": filename,
                        "content": encoded_string,
                        "mimeType": "image/jpeg" if filename.lower().endswith("jpg") or filename.lower().endswith("jpeg") else "image/png"
                    })

        return jsonify({
            "status": "success", 
            "images": image_list,
            "count": len(image_list)
        })
    except Exception as e:
        print(f"Erreur lors du listage des images : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/images/<path:filename>")
def get_image(filename):
    return send_from_directory(IMAGE_DIRECTORY, filename)

@app.route("/send-preferences", methods=["POST"])
def send_preferences():
    data = request.get_json()
    liked_images = data.get("likedImages", [])
    username = data.get("username", "anonymous")
    
    if not liked_images:
        return jsonify({
            "status": "error", 
            "message": "Aucune image likée fournie"
        }), 400
    
    try:
        response = requests.post(
            USER_PROFILER_URL, 
            json={  "username": username, "likedImages": liked_images}
        )
        
        response.raise_for_status()
        result = response.json()
        
        return jsonify({
            "status": "success",
            "message": "Préférences envoyées avec succès",
            "result": result
        })
    except Exception as e:
        print(f"Erreur lors de l'envoi des préférences : {e}")
        return jsonify({
            "status": "error", 
            "message": f"Erreur lors de l'envoi des préférences : {str(e)}"
        }), 500
    
@app.route("/recommend", methods=["GET"])
def trigger_recommendation():
    try:
        response = requests.get(IMAGE_RECOMMENDER_URL)
        response.raise_for_status()
        result = response.json()
        return jsonify({
            "status": "success",
            "message": "Recommandations déclenchées",
            "result": result
        })
    except Exception as e:
        print(f"Erreur lors du déclenchement des recommandations : {e}")
        return jsonify({
            "status": "error", 
            "message": f"Erreur déclenchement recommandations : {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)