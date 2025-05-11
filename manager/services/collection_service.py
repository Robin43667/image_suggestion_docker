import requests
from config import SPARQL_ENDPOINT, SPARQL_QUERIES

def fetch_image_urls():
    all_urls = []
    for query in SPARQL_QUERIES:
        try:
            response = requests.get(SPARQL_ENDPOINT, params={"query": query, "format": "json"})
            response.raise_for_status()
            data = response.json()
            urls = [binding["image"]["value"] for binding in data["results"]["bindings"]]
            all_urls.extend(urls)
        except Exception as e:
            print(f"Erreur SPARQL pour une requête : {e}")
    return list(set(all_urls))  # retire les doublons

def split_list(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n)]

def send_urls_to_collector(collector_url, urls, prefix):
    try:
        response = requests.post(collector_url, json={"urls": urls, "prefix": prefix})
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Erreur POST vers {collector_url} : {e}")
        return False