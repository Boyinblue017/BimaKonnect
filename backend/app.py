import os
import secrets

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_cors import CORS

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, "templates")
DEFAULT_DATABASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "instance", "bimakonnect.sqlite3")
)

app = Flask(
    __name__,
    static_folder=STATIC_DIR,
    static_url_path="",
    template_folder=TEMPLATES_DIR,
)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
    DATABASE_PATH=os.environ.get("BIMAKONNECT_DATABASE", DEFAULT_DATABASE_PATH),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "").lower() == "true",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 7,
)
CORS(app)

try:
    # Package mode: python -m backend.app (recommended for deployment/testing)
    from backend.routes.chat import chat_bp
    from backend.routes.quiz import quiz_bp
    from backend.routes.glossary import glossary_bp
    from backend.routes.claims import claims_bp
    from backend.routes.auth import auth_bp
    from backend.routes.specialists import specialists_bp
    from backend.services.auth_service import get_user_by_id, initialize_database
except ModuleNotFoundError:
    # Script mode: python backend/app.py (friendly for local development)
    from routes.chat import chat_bp
    from routes.quiz import quiz_bp
    from routes.glossary import glossary_bp
    from routes.claims import claims_bp
    from routes.auth import auth_bp
    from routes.specialists import specialists_bp
    from services.auth_service import get_user_by_id, initialize_database

app.register_blueprint(chat_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(glossary_bp)
app.register_blueprint(claims_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(specialists_bp)
initialize_database(
    app.config["DATABASE_PATH"],
    admin_email=os.environ.get("ADMIN_EMAIL"),
    admin_password=os.environ.get("ADMIN_PASSWORD"),
)

PUBLIC_ENDPOINTS = {
    "auth.login",
    "auth.register",
    "health",
    "privacy",
    "static",
}


def csrf_token():
    token = session.get("csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


@app.context_processor
def inject_csrf_token():
    return {"csrf_token": csrf_token()}


@app.before_request
def require_account_and_csrf():
    if (
        request.endpoint == "static"
        and request.path.lower().endswith(".html")
        and request.path.lower() != "/privacy.html"
    ):
        return redirect(url_for("auth.login"))

    if request.endpoint in PUBLIC_ENDPOINTS:
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            supplied_token = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
            expected_token = session.get("csrf_token", "")
            if not expected_token or not secrets.compare_digest(supplied_token, expected_token):
                return jsonify({"error": "Your session expired. Refresh the page and try again."}), 400
        return None

    user_id = session.get("user_id")
    if user_id is None or get_user_by_id(app.config["DATABASE_PATH"], user_id) is None:
        session.clear()
        if request.is_json or request.path.startswith(("/chat", "/recommend", "/glossary", "/claims")):
            return jsonify({"error": "Please sign in to continue."}), 401
        return redirect(url_for("auth.login", next=request.path))

    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        supplied_token = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
        expected_token = session.get("csrf_token", "")
        if not expected_token or not secrets.compare_digest(supplied_token, expected_token):
            return jsonify({"error": "Your session expired. Refresh the page and try again."}), 400
    return None

@app.route("/")
def home():
    user = get_user_by_id(app.config["DATABASE_PATH"], session["user_id"])
    return render_template(
        "mvp.html",
        csrf_token=csrf_token(),
        user_email=user["email"],
        user_role=user["role"],
    )


@app.route("/privacy.html")
def privacy():
    return render_template("privacy.html")


@app.route("/api/health")
def health():
    """Small readiness endpoint for hosting platforms."""
    return jsonify({"status": "ok", "service": "BimaKonnect API"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
