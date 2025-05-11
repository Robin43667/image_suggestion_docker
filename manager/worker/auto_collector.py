import time
import redis
import hashlib
import glob
import os  # Ajouté pour os.path.join
from utils.logger import logger
from config import REDIS_HOST, REDIS_PORT, IMAGE_DIRECTORY
from services.collection_service import fetch_image_urls, split_list, send_urls_to_collector

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def hash_url(url):
    return hashlib.sha256(url.encode()).hexdigest()

def initialize_known_hashes():
    all_urls = fetch_image_urls()
    all_hashes = {hash_url(url) for url in all_urls}
    r.sadd("all_known_hashes", *all_hashes)

def get_filename_from_url(url):
    return hash_url(url) + ".jpg"

def is_already_downloaded(url, image_dir=IMAGE_DIRECTORY):
    filename_base = hash_url(url)
    pattern = os.path.join(image_dir, filename_base + ".*")
    matches = glob.glob(pattern)
    return len(matches) > 0

def start_collection_cycle():
    initialize_known_hashes()
    all_known = set(r.smembers("all_known_hashes"))
    seen_hashes = set(r.smembers("downloaded_hashes"))

    while True:
        logger.info("Cycle de collecte lancé...")

        remaining_hashes = all_known - seen_hashes
        if not remaining_hashes:
            logger.info("Toutes les images connues ont été téléchargées. Arrêt.")
            break

        all_urls = fetch_image_urls()
        new_urls = [
            url for url in all_urls
            if hash_url(url) in remaining_hashes and not is_already_downloaded(url)
        ]

        if not new_urls:
            logger.info("Plus de nouvelles URLs à télécharger.")
            break

        batch = new_urls[:5]
        seen_hashes.update(hash_url(url) for url in batch)
        r.sadd("downloaded_hashes", *[hash_url(url) for url in batch])

        logger.info(f"Téléchargement de {len(batch)} images...")

        urls1, urls2 = split_list(batch, 2)
        success1 = send_urls_to_collector("http://data-collector-1:5001/collect", urls1, "collector1")
        success2 = send_urls_to_collector("http://data-collector-2:5001/collect", urls2, "collector2")

        if success1 or success2:
            r.publish("status", "download_done")
        else:
            logger.info("Erreur lors de l'envoi aux collecteurs")

        time.sleep(10)
