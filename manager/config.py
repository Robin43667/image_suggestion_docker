import os

# Database configuration
DB_HOST = "mariadb"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "imageDB"

REDIS_HOST = "redis"
REDIS_PORT = 6379
DATA_ANALYZER_URL = "http://data-analyzer:5003"


# API endpoints
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
DATA_COLLECTOR_1_URL = "http://data-collector-1:5001/collect"
DATA_COLLECTOR_2_URL = "http://data-collector-2:5001/collect"
USER_PROFILER_URL = "http://user-profiler:5000/profile"
IMAGE_RECOMMENDER_URL = "http://image-recommender:5005/recommend"
IMAGE_RECOMMENDER_URL = "http://image-recommender:5005"

# Paths
IMAGE_DIRECTORY = "/app/images/"

SPARQL_QUERIES = [
    """
    SELECT ?image
    WHERE {
      ?nebuleuse wdt:P31/wdt:P279* wd:Q204194 .
      ?nebuleuse wdt:P18 ?image .
    }
    LIMIT 50
    """,
    """
    SELECT ?image
    WHERE {
      ?glacier wdt:P31/wdt:P279* wd:Q35666 .
      ?glacier wdt:P18 ?image .
    }
    LIMIT 50
    """,
    """
    SELECT ?image
    WHERE {
      ?ville wdt:P31/wdt:P279* wd:Q515 .
      ?ville wdt:P18 ?image .
    }
    LIMIT 50
    """
]
