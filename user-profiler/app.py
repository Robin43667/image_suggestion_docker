from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/profile", methods=["GET"])
def profile():
    # Génération d’un profil utilisateur fictif
    return jsonify({"user_id": 1, "preferences": ["nature", "espace", "anime"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
