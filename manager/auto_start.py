import threading
from flask import Flask
from routes.auth import auth_bp
from routes.collection import collection_bp
from routes.images import images_bp
from routes.recommend import recommend_bp
from worker.auto_collector import start_collection_cycle
from worker.listener import listen_to_redis
from utils.logger import setup_logger

def create_app():
    app = Flask(__name__)
    
    setup_logger()
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(images_bp)
    app.register_blueprint(recommend_bp)
    
    return app

if __name__ == "__main__":
    # Lancer les workers en arrière-plan
    threading.Thread(target=start_collection_cycle, daemon=True).start()
    threading.Thread(target=listen_to_redis, daemon=True).start()
    
    # Lancer le serveur Flask
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
