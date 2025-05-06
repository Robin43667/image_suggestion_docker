import redis
import requests
from config import DATA_ANALYZER_URL
from worker.auto_collector import start_collection_cycle

r = redis.Redis(host="redis", port=6379, decode_responses=True)

def listen_to_redis():
    pubsub = r.pubsub()
    pubsub.subscribe("status")

    print("En attente des événements Redis...")

    for message in pubsub.listen():
        if message['type'] == 'message':
            if message['data'] == "download_done":
                print("Téléchargement terminé, lancement de l'analyse...")
                try:
                    requests.get(DATA_ANALYZER_URL + "/analyze")
                except Exception as e:
                    print(f"Erreur appel analyze : {e}")
