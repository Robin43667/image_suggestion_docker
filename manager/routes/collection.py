from flask import Blueprint, jsonify
from services.collection_service import fetch_image_urls, split_list, send_urls_to_collector
from config import DATA_COLLECTOR_1_URL, DATA_COLLECTOR_2_URL
import random

collection_bp = Blueprint('collection', __name__)

@collection_bp.route("/start_collection", methods=["GET"])
def start_collection():
    try:
        print("Récupération des URLs depuis Wikidata...")
        urls = fetch_image_urls()
        print(f"{len(urls)} URLs récupérées")

        if not urls:
            return jsonify({"status": "failure", "message": "Aucune URL récupérée"}), 500
        
        urls_sample = random.sample(urls, min(20, len(urls)))
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