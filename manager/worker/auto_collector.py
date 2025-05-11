import time
import requests
import redis
import hashlib

from config import DATA_ANALYZER_URL, REDIS_HOST, REDIS_PORT
from services.collection_service import fetch_image_urls, split_list, send_urls_to_collector

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def hash_url(url):
    return hashlib.sha256(url.encode()).hexdigest()

def start_collection_cycle():
    seen_hashes = set(r.smembers("downloaded_hashes"))

    while True:
        print("Cycle de collecte lancé...")
        all_urls = fetch_image_urls()
        
        # Filtre les nouvelles URLs qui n'ont pas encore été téléchargées
        new_urls = [url for url in all_urls if hash_url(url) not in seen_hashes]

        if not new_urls:
            print("Toutes les images ont été traitées. Fin du cycle.")
            break  # Arrête la boucle si toutes les images sont traitées

        # On prend un lot de 5 nouvelles URLs
        batch = new_urls[:5]
        seen_hashes.update(hash_url(url) for url in batch)
        r.sadd("downloaded_hashes", *[hash_url(url) for url in batch])

        print(f"Téléchargement de {len(batch)} images...")

        # Divise la liste en deux parties pour l'envoi aux collecteurs
        urls1, urls2 = split_list(batch, 2)

        # Envoie les URLs au collecteur, et vérifie si l'envoi a réussi
        success1 = send_urls_to_collector("http://data-collector-1:5001/collect", urls1, "collector1")
        success2 = send_urls_to_collector("http://data-collector-2:5001/collect", urls2, "collector2")

        if success1 or success2:
            r.publish("status", "download_done")
        else:
            print("Erreur lors de l'envoi aux collecteurs")

        time.sleep(10)  # Pause avant de recommencer le cycle
