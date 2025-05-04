from flask import Blueprint, jsonify, request
from services.auth_service import create_users_table, register_user, verify_user
from utils.logger import logger

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Username et password requis"}), 400
    
    try:
        create_users_table()
        result, message, status_code = register_user(username, password)
        
        return jsonify({"status": result, "message": message}), status_code
        
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement : {e}")
        return jsonify({"status": "error", "message": "Erreur serveur"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Username et password requis"}), 400
    
    try:
        create_users_table()
        result, message, status_code, user_data = verify_user(username, password)
        
        response_data = {
            "status": result,
            "message": message
        }
        
        if user_data:
            response_data["user"] = user_data
            
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"Erreur lors de la connexion : {e}")
        return jsonify({"status": "error", "message": "Erreur serveur"}), 500