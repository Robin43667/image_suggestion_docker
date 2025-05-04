import os
import hashlib
from services.db import get_db_connection
from utils.logger import logger

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
        raise

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

def register_user(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return "error", "Username déjà utilisé", 400
        
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                      (username, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        
        return "success", "Utilisateur créé avec succès", 201
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement : {e}")
        raise

def verify_user(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, password, calibrated FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user or not verify_password(user[1], password):
            return "error", "Identifiants invalides", 401, None
        
        user_data = {
            "username": user[0],
            "calibrated": bool(user[2])
        }
        
        return "success", "Connexion réussie", 200, user_data
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'utilisateur : {e}")
        raise