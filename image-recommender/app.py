from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    # Logique de recommandation fictive
    return jsonify({
        "user_id": data.get("user_id"),
        "recommended_images": ["img_42.jpg", "img_17.jpg", "img_99.jpg"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
