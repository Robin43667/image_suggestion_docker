# manager/routes/images.py

from flask import Blueprint, jsonify, request, send_from_directory
from services.image_service import list_all_images, encode_image
from config import IMAGE_DIRECTORY, USER_PROFILER_URL, IMAGE_RECOMMENDER_URL
import requests

images_bp = Blueprint('images', __name__)

@images_bp.route("/list-images", methods=["GET"])
def list_images():
    try:
        image_list = list_all_images()
        
        return jsonify({
            "status": "success", 
            "images": image_list,
            "count": len(image_list)
        })
    except Exception as e:
        print(f"Erreur lors du listage des images : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@images_bp.route("/images/<path:filename>")
def get_image(filename):
    return send_from_directory(IMAGE_DIRECTORY, filename)

@images_bp.route("/send-preferences", methods=["POST"])
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
            json={"username": username, "likedImages": liked_images}
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
    

@images_bp.route("/image-for-calibration", methods=["GET"])
def image_for_calibration():
    try:
        image_list = list_all_images()
        calibration_images = image_list[:5]  # Prend les 5 premières images

        return jsonify({
            "status": "success",
            "images": calibration_images,
            "count": len(calibration_images)
        })
    except Exception as e:
        print(f"Erreur lors de la récupération des images de calibration : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

@images_bp.route("/dislike-image", methods=["POST"])
def dislike_image():
    # logger.info("DISLIKE")
    data = request.get_json()
    username = data.get("username", "anonymous")
    image = data.get("image")
    
    if not image:
        return jsonify({
            "status": "error",
            "message": "Aucune image fournie"
        }), 400
    
    try:
        # URL du recommender à mettre dans votre fichier config
        recommender_url = IMAGE_RECOMMENDER_URL + f"/dislike/{username}"
        
        response = requests.post(
            recommender_url,
            json={"image": image}
        )
        
        response.raise_for_status()
        result = response.json()
        
        return jsonify({
            "status": "success",
            "message": "Image marquée comme non aimée",
            "result": result
        })
    except Exception as e:
        print(f"Erreur lors du signalement de l'image non aimée : {e}")
        return jsonify({
            "status": "error",
            "message": f"Erreur lors du signalement de l'image non aimée : {str(e)}"
        }), 500