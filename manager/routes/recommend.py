# manager/routes/recommend.py
from flask import Blueprint, jsonify, request
from config import IMAGE_RECOMMENDER_URL
import requests
from services.image_service import encode_image

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route("/recommend/<user_id>", methods=["GET"])
def get_user_recommendation(user_id):
    """Route appelée par le frontend : renvoie l'image recommandée (encodée) pour un utilisateur"""
    try:
        # Appel au microservice image recommender
        recommender_url = f"{IMAGE_RECOMMENDER_URL}/{user_id}"
        response = requests.get(recommender_url)
        response.raise_for_status()
        result = response.json()

        if result.get("status") != "ok" or not result.get("recommendations"):
            return jsonify({
                "status": "empty",
                "message": f"Aucune recommandation disponible pour l'utilisateur {user_id}"
            }), 404

        # On récupère le nom du fichier recommandé
        recommended_filename = result["recommendations"][0]

        # On encode l'image correspondante
        image_data = encode_image(recommended_filename)

        return jsonify({
            "status": "success",
            "recommendation": image_data
        }), 200

    except requests.RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"Erreur lors de l'appel à l'image recommender : {str(e)}"
        }), 500
    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "message": f"Image recommandée '{recommended_filename}' introuvable dans le volume"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erreur interne : {str(e)}"
        }), 500
