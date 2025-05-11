from flask import Blueprint, jsonify, request,make_response
from services.auth_service import create_users_table, register_user, verify_user
from utils.logger import logger
from services.db import get_db_connection

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
        
        response = make_response(jsonify(response_data), status_code)
        
        if user_data:
            response_data["user"] = user_data
            # Pose un cookie httpOnly pour éviter XSS (et sécurise éventuellement par SameSite / Secure si HTTPS)
            response.set_cookie('username', user_data['username'], httponly=True, samesite='Lax')

        return response
        
    except Exception as e:
        logger.error(f"Erreur lors de la connexion : {e}")
        return jsonify({"status": "error", "message": "Erreur serveur"}), 500


@auth_bp.route("/me", methods=["GET"])
def me():
    username = request.cookies.get('username')
    
    if not username:
        return jsonify({"status": "error", "message": "Utilisateur non authentifié"}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, calibrated FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({"status": "error", "message": "Utilisateur non trouvé"}), 404
        
        user_data = {
            "username": user[0],
            "calibrated": bool(user[1])
        }

        # Ajout de logs pour voir ce qui est renvoyé
        logger.info(f"Réponse de /me: {user_data}")

        return jsonify({"status": "success", "user": user_data}), 200
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'utilisateur /me : {e}")
        return jsonify({"status": "error", "message": "Erreur serveur"}), 500
