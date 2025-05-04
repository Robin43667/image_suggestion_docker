# from flask import Flask, request, jsonify
# import logging
# import mysql.connector
# import json
# import redis
# from collections import Counter

# app = Flask(__name__)

# # Logging setup
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),
#         logging.FileHandler('user_profiler.log')
#     ]
# )

# logger = logging.getLogger(__name__)

# # DB config
# DB_HOST = "mariadb"
# DB_USER = "root"
# DB_PASSWORD = "root"
# DB_NAME = "imageDB"

# # Connexion à Redis (en utilisant le nom du service Docker : "redis")
# r = redis.Redis(host='redis', port=6379, decode_responses=True)

# def notify_user_updated(user_id):
#     logger.info("redis publish")
#     r.publish('user.updated', str(user_id))

# def get_db_connection():
#     return mysql.connector.connect(
#         host=DB_HOST,
#         user=DB_USER,
#         password=DB_PASSWORD,
#         database=DB_NAME
#     )

# def create_profiles_table():
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS profiles (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 username VARCHAR(255) UNIQUE,
#                 avg_width FLOAT,
#                 avg_height FLOAT,
#                 avg_colors TEXT,
#                 favorite_tags TEXT
#             )
#         """)
#         conn.commit()
#         cursor.close()
#         conn.close()
#     except Exception as e:
#         logger.error(f"Erreur lors de la création de la table profiles : {e}")

# @app.route("/profile", methods=["POST"])
# def profile_user():
#     data = request.get_json()
#     username = data.get("username", "anonymous")
#     logger.info(f"Username reçu dans le profil: {username}")  
#     liked_images = data.get("likedImages", [])

#     if not liked_images:
#         logger.warning("Aucune image likée reçue")
#         return jsonify({"status": "error", "message": "Aucune image likée fournie"}), 400

#     logger.info(f"Préférences utilisateur reçues: {liked_images}")

#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         format_strings = ','.join(['%s'] * len(liked_images))
#         cursor.execute(f"""
#             SELECT * FROM files WHERE filename IN ({format_strings})
#         """, liked_images)

#         rows = cursor.fetchall()
#         if not rows:
#             return jsonify({"status": "error", "message": "Aucune correspondance trouvée"}), 404

#         total_width = total_height = 0
#         all_colors = []
#         all_tags = []

#         for row in rows:
#             total_width += row['width']
#             total_height += row['height']
#             all_colors.extend(json.loads(row['colors']))
#             all_tags.extend(json.loads(row['tags']))

#         avg_width = total_width / len(rows)
#         avg_height = total_height / len(rows)

#         # Moyenne des couleurs RGB
#         avg_colors = []
#         for i in range(5):  # assume 5 colors per image
#             channel_totals = [0, 0, 0]
#             count = 0
#             for j in range(i, len(all_colors), 5):
#                 r, g, b = all_colors[j]
#                 channel_totals[0] += r
#                 channel_totals[1] += g
#                 channel_totals[2] += b
#                 count += 1
#             if count > 0:
#                 avg_colors.append([int(c / count) for c in channel_totals])
        
#         tag_counter = Counter(all_tags)
#         most_common_tags = [tag for tag, _ in tag_counter.most_common(5)]

#         # Sauvegarde ou mise à jour dans la table profiles
#         create_profiles_table()

#         cursor.execute("""
#             SELECT id FROM profiles WHERE username = %s
#         """, (username,))
#         existing_profile = cursor.fetchone()

#         if existing_profile:
#             logger.info(f"Profil existant trouvé pour {username}, mise à jour en cours")
#             cursor.execute("""
#                 UPDATE profiles
#                 SET avg_width = %s, avg_height = %s, avg_colors = %s, favorite_tags = %s
#                 WHERE username = %s
#             """, (
#                 avg_width,
#                 avg_height,
#                 json.dumps(avg_colors),
#                 json.dumps(most_common_tags),
#                 username
#             ))
#         else:
#             logger.info(f"Aucun profil existant pour {username}, création en cours")
#             cursor.execute("""
#                 INSERT INTO profiles (username, avg_width, avg_height, avg_colors, favorite_tags)
#                 VALUES (%s, %s, %s, %s, %s)
#             """, (
#                 username,
#                 avg_width,
#                 avg_height,
#                 json.dumps(avg_colors),
#                 json.dumps(most_common_tags)
#             ))

#         conn.commit()
#         notify_user_updated(user_id=username)

#         # Mise à jour de l'utilisateur : set calibrated = 1
#         cursor.execute("""
#             UPDATE users
#             SET calibrated = 1
#             WHERE username = %s
#         """, (username,))
#         if cursor.rowcount == 0:
#             logger.warning(f"Aucun utilisateur trouvé avec le username {username} pour mise à jour de calibrated")
#         else:
#             logger.info(f"Champ calibrated mis à jour pour {username}")
#         conn.commit()

#         return jsonify({
#             "status": "success",
#             "message": f"Profil {'mis à jour' if existing_profile else 'créé'} pour {username}",
#             "profil": {
#                 "avg_width": avg_width,
#                 "avg_height": avg_height,
#                 "avg_colors": avg_colors,
#                 "favorite_tags": most_common_tags
#             }
#         })

#     except Exception as e:
#         logger.error(f"Erreur lors du traitement des préférences: {e}")
#         return jsonify({"status": "error", "message": "Erreur interne"}), 500
#     finally:
#         if cursor: cursor.close()
#         if conn: conn.close()

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)



from flask import Flask, request, jsonify
import logging
import mysql.connector
import json
import redis
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

# Connexion à Redis (en utilisant le nom du service Docker : "redis")
r = redis.Redis(host='redis', port=6379, decode_responses=True)

def notify_user_updated(user_id):
    logger.info("redis publish")
    r.publish('user.updated', str(user_id))

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
                username VARCHAR(255) UNIQUE,
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

def combine_lists(list1, list2):
    return list1 + list2

def average_colors(color_lists, group_size=5):
    avg_colors = []
    for i in range(group_size):
        channel_totals = [0, 0, 0]
        count = 0
        for j in range(i, len(color_lists), group_size):
            r, g, b = color_lists[j]
            channel_totals[0] += r
            channel_totals[1] += g
            channel_totals[2] += b
            count += 1
        if count > 0:
            avg_colors.append([int(c / count) for c in channel_totals])
    return avg_colors

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

        nb_new_images = len(rows)
        total_width = sum(row['width'] for row in rows)
        total_height = sum(row['height'] for row in rows)
        all_colors = []
        all_tags = []

        for row in rows:
            all_colors.extend(json.loads(row['colors']))
            all_tags.extend(json.loads(row['tags']))

        avg_width_new = total_width / nb_new_images
        avg_height_new = total_height / nb_new_images

        # Moyenne des nouvelles couleurs
        avg_colors_new = average_colors(all_colors)

        tag_counter_new = Counter(all_tags)

        create_profiles_table()

        cursor.execute("""
            SELECT * FROM profiles WHERE username = %s
        """, (username,))
        existing_profile = cursor.fetchone()

        if existing_profile:
            logger.info(f"Profil existant trouvé pour {username}, fusion des données")

            avg_width_old = existing_profile['avg_width']
            avg_height_old = existing_profile['avg_height']
            avg_colors_old = json.loads(existing_profile['avg_colors'])
            favorite_tags_old = json.loads(existing_profile['favorite_tags'])

            # On suppose que le profil actuel est basé sur N images -> on va approximer N = 5 (arbitraire si pas stocké)
            # Pour plus de précision on devrait stocker ce nombre dans la table.
            nb_old_images = 5

            # Moyenne pondérée
            combined_nb_images = nb_old_images + nb_new_images
            combined_avg_width = (avg_width_old * nb_old_images + avg_width_new * nb_new_images) / combined_nb_images
            combined_avg_height = (avg_height_old * nb_old_images + avg_height_new * nb_new_images) / combined_nb_images

            # Fusion couleurs (simple concaténation puis recalcul de moyenne)
            combined_colors = combine_lists(avg_colors_old * nb_old_images, avg_colors_new * nb_new_images)
            combined_avg_colors = average_colors(combined_colors)

            # Fusion tags
            combined_tags = favorite_tags_old * nb_old_images + list(tag_counter_new.elements())
            tag_counter_combined = Counter(combined_tags)
            most_common_tags = [tag for tag, _ in tag_counter_combined.most_common(5)]

            cursor.execute("""
                UPDATE profiles
                SET avg_width = %s, avg_height = %s, avg_colors = %s, favorite_tags = %s
                WHERE username = %s
            """, (
                combined_avg_width,
                combined_avg_height,
                json.dumps(combined_avg_colors),
                json.dumps(most_common_tags),
                username
            ))

        else:
            logger.info(f"Aucun profil existant pour {username}, création en cours")
            most_common_tags = [tag for tag, _ in tag_counter_new.most_common(5)]

            cursor.execute("""
                INSERT INTO profiles (username, avg_width, avg_height, avg_colors, favorite_tags)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                username,
                avg_width_new,
                avg_height_new,
                json.dumps(avg_colors_new),
                json.dumps(most_common_tags)
            ))

        conn.commit()
        notify_user_updated(user_id=username)

        # Mise à jour calibrated
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
            "message": f"Profil {'mis à jour' if existing_profile else 'créé'} pour {username}",
            "profil": {
                "avg_width": combined_avg_width if existing_profile else avg_width_new,
                "avg_height": combined_avg_height if existing_profile else avg_height_new,
                "avg_colors": combined_avg_colors if existing_profile else avg_colors_new,
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
