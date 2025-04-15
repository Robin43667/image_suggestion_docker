from flask import Flask, jsonify
import requests
import random

app = Flask(__name__)

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
DATA_COLLECTOR_1_URL = "http://data-collector-1:5001/collect"
DATA_COLLECTOR_2_URL = "http://data-collector-2:5001/collect"

SPARQL_QUERY = """
SELECT ?image
WHERE {
  ?nebuleuse wdt:P31/wdt:P279* wd:Q204194 .
  ?nebuleuse wdt:P18 ?image .
}
LIMIT 100
"""

def fetch_image_urls():
    try:
        response = requests.get(SPARQL_ENDPOINT, params={"query": SPARQL_QUERY, "format": "json"})
        response.raise_for_status()
        data = response.json()
        return [binding["image"]["value"] for binding in data["results"]["bindings"]]
    except Exception as e:
        print(f"Erreur SPARQL : {e}")
        return []

def split_list(lst, n):
    k, m = divmod(len(lst), n)
    return (lst[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n))

def send_urls_to_collector(collector_url, urls, prefix):
    try:
        response = requests.post(collector_url, json={"urls": urls, "prefix": prefix})
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Erreur POST vers {collector_url} : {e}")
        return False

@app.route("/start_collection", methods=["GET"])
def start_collection():
    urls = fetch_image_urls()
    if not urls:
        return jsonify({"status": "failure", "message": "Aucune URL récupérée"}), 500

    urls_sample = random.sample(urls, min(10, len(urls)))
    urls1, urls2 = split_list(urls_sample, 2)

    success1 = send_urls_to_collector(DATA_COLLECTOR_1_URL, list(urls1), "collector1")
    success2 = send_urls_to_collector(DATA_COLLECTOR_2_URL, list(urls2), "collector2")

    if success1 and success2:
        return jsonify({"status": "success", "message": "Collecte répartie et lancée"})
    else:
        return jsonify({"status": "partial_failure", "message": "Erreur avec un des collecteurs"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
