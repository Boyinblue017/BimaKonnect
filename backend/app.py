import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

from backend.routes.chat import chat_bp
from backend.routes.quiz import quiz_bp
from backend.routes.glossary import glossary_bp

app.register_blueprint(chat_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(glossary_bp)

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "mvp.html")


@app.route("/api/health")
def health():
    """Small readiness endpoint for hosting platforms."""
    return jsonify({"status": "ok", "service": "BimaKonnect API"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
