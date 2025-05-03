from flask import Flask, request, jsonify
import logging
import mysql.connector
import json
from collections import Counter

app = Flask(__name__)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('user_profiler.log')
    ]
)

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

def create_profiles_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255),
                avg_width FLOAT,
                avg_height FLOAT,
                avg_colors TEXT,
                favorite_tags TEXT
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Erreur lors de la création de la table profiles : {e}")

@app.route("/profile", methods=["POST"])
def profile_user():
    data = request.get_json()
    username = data.get("username", "anonymous")
    logger.info(f"Username reçu dans le profil: {username}")  
    liked_images = data.get("likedImages", [])

    if not liked_images:
        logger.warning("Aucune image likée reçue")
        return jsonify({"status": "error", "message": "Aucune image likée fournie"}), 400

    logger.info(f"Préférences utilisateur reçues: {liked_images}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        format_strings = ','.join(['%s'] * len(liked_images))
        cursor.execute(f"""
            SELECT * FROM files WHERE filename IN ({format_strings})
        """, liked_images)

        rows = cursor.fetchall()
        if not rows:
            return jsonify({"status": "error", "message": "Aucune correspondance trouvée"}), 404

        total_width = total_height = 0
        all_colors = []
        all_tags = []

        for row in rows:
            total_width += row['width']
            total_height += row['height']
            all_colors.extend(json.loads(row['colors']))
            all_tags.extend(json.loads(row['tags']))

        avg_width = total_width / len(rows)
        avg_height = total_height / len(rows)

        # Moyenne des couleurs RGB
        avg_colors = []
        for i in range(5):  # assume 5 colors per image
            channel_totals = [0, 0, 0]
            count = 0
            for j in range(i, len(all_colors), 5):
                r, g, b = all_colors[j]
                channel_totals[0] += r
                channel_totals[1] += g
                channel_totals[2] += b
                count += 1
            if count > 0:
                avg_colors.append([int(c / count) for c in channel_totals])
        
        tag_counter = Counter(all_tags)
        most_common_tags = [tag for tag, _ in tag_counter.most_common(5)]

        # Sauvegarde dans la table profiles
        create_profiles_table()
        cursor.execute("""
            INSERT INTO profiles (username, avg_width, avg_height, avg_colors, favorite_tags)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            username,
            avg_width,
            avg_height,
            json.dumps(avg_colors),
            json.dumps(most_common_tags)
        ))
        conn.commit()

        logger.info(f"Profil enregistré pour {username}")

        # Mise à jour de l'utilisateur : set calibrated = 1
        cursor.execute("""
            UPDATE users
            SET calibrated = 1
            WHERE username = %s
        """, (username,))
        if cursor.rowcount == 0:
            logger.warning(f"Aucun utilisateur trouvé avec le username {username} pour mise à jour de calibrated")
        else:
            logger.info(f"Champ calibrated mis à jour pour {username}")
        conn.commit()

        return jsonify({
            "status": "success",
            "message": f"Profil créé pour {username}",
            "profil": {
                "avg_width": avg_width,
                "avg_height": avg_height,
                "avg_colors": avg_colors,
                "favorite_tags": most_common_tags
            }
        })

    except Exception as e:
        logger.error(f"Erreur lors du traitement des préférences: {e}")
        return jsonify({"status": "error", "message": "Erreur interne"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
