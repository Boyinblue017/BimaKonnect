import re
import sqlite3

from flask import Blueprint, current_app, jsonify, render_template, request, session

try:
    from backend.services.auth_service import (
        MAX_PASSWORD_LENGTH,
        MIN_PASSWORD_LENGTH,
        change_password,
        get_user_by_id,
        validate_email,
        validate_password,
    )
    from backend.services.specialist_service import (
        create_specialist,
        get_specialist_profile,
        list_specialists,
        rate_specialist,
        update_specialist_profile,
    )
except ModuleNotFoundError:
    from services.auth_service import (
        MAX_PASSWORD_LENGTH,
        MIN_PASSWORD_LENGTH,
        change_password,
        get_user_by_id,
        validate_email,
        validate_password,
    )
    from services.specialist_service import (
        create_specialist,
        get_specialist_profile,
        list_specialists,
        rate_specialist,
        update_specialist_profile,
    )

specialists_bp = Blueprint("specialists", __name__)
PROFILE_FIELDS = ("display_name", "public_email", "phone", "specialty", "region", "bio")
FIELD_LIMITS = {
    "display_name": 100,
    "public_email": 254,
    "phone": 40,
    "specialty": 100,
    "region": 120,
    "bio": 800,
}


def _database_path():
    return current_app.config["DATABASE_PATH"]


def _profile_from_payload(payload):
    profile = {
        field: str(payload.get(field, "")).strip()
        for field in PROFILE_FIELDS
    }
    if any(not profile[field] for field in PROFILE_FIELDS):
        return None, "Complete all specialist profile fields."
    for field, limit in FIELD_LIMITS.items():
        if len(profile[field]) > limit:
            return None, f"{field.replace('_', ' ').capitalize()} must be {limit} characters or fewer."
    profile["public_email"] = validate_email(profile["public_email"])
    if not profile["public_email"]:
        return None, "Enter a valid public contact email."
    if not re.fullmatch(r"[+0-9() .-]{7,40}", profile["phone"]):
        return None, "Enter a phone number using digits and standard phone symbols."
    return profile, None


def _role_required(role):
    user = get_user_by_id(_database_path(), session["user_id"])
    if user is None or user["role"] != role:
        return None
    return user


@specialists_bp.route("/specialists")
def directory():
    return render_template("specialists.html", csrf_token=session["csrf_token"])


@specialists_bp.route("/api/specialists")
def directory_data():
    return jsonify({"specialists": list_specialists(_database_path(), session["user_id"])})


@specialists_bp.route("/api/specialists/<int:specialist_id>/rating", methods=["POST"])
def submit_rating(specialist_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Submit a rating as an object."}), 400
    rating = data.get("rating")
    if isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5:
        return jsonify({"error": "Choose a rating from 1 to 5 stars."}), 400
    result = rate_specialist(
        _database_path(),
        specialist_id,
        session["user_id"],
        rating,
    )
    if result == "not_found":
        return jsonify({"error": "That specialist could not be found."}), 404
    if result == "self_rating":
        return jsonify({"error": "You cannot rate your own specialist profile."}), 400
    if result != "ok":
        return jsonify({"error": "We could not save that rating."}), 400
    specialist = next(
        (item for item in list_specialists(_database_path(), session["user_id"]) if item["id"] == specialist_id),
        None,
    )
    return jsonify({"message": "Your rating was saved.", "specialist": specialist})


@specialists_bp.route("/admin/specialists")
def admin_dashboard():
    if _role_required("admin") is None:
        return "Administrator access required.", 403
    return render_template("admin-specialists.html", csrf_token=session["csrf_token"])


@specialists_bp.route("/api/admin/specialists", methods=["GET", "POST"])
def add_specialist():
    if _role_required("admin") is None:
        return jsonify({"error": "Administrator access required."}), 403
    if request.method == "GET":
        return jsonify({"specialists": list_specialists(_database_path(), None)})
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Submit specialist details as an object."}), 400
    profile, error = _profile_from_payload(data)
    if error:
        return jsonify({"error": error}), 400
    login_email = validate_email(str(data.get("login_email", "")))
    password = data.get("temporary_password", "")
    if not login_email:
        return jsonify({"error": "Enter a valid sign-in email address."}), 400
    if not validate_password(password):
        return jsonify({
            "error": f"Use a temporary password between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters."
        }), 400
    profile["login_email"] = login_email
    try:
        user_id = create_specialist(_database_path(), profile, password)
    except sqlite3.IntegrityError:
        return jsonify({"error": "An account with that sign-in email already exists."}), 409
    return jsonify({"message": "Specialist account created.", "id": user_id}), 201


@specialists_bp.route("/specialist/account")
def specialist_account():
    if _role_required("specialist") is None:
        return "Specialist account access required.", 403
    return render_template("specialist-account.html", csrf_token=session["csrf_token"])


@specialists_bp.route("/api/specialists/me")
def specialist_account_data():
    if _role_required("specialist") is None:
        return jsonify({"error": "Specialist account access required."}), 403
    user = get_user_by_id(_database_path(), session["user_id"])
    profile = get_specialist_profile(_database_path(), user["id"])
    if profile is None:
        return jsonify({"error": "Your specialist profile could not be found."}), 404
    return jsonify({"profile": profile})


@specialists_bp.route("/api/specialists/me", methods=["POST"])
def save_specialist_account():
    if _role_required("specialist") is None:
        return jsonify({"error": "Specialist account access required."}), 403
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Submit profile details as an object."}), 400
    profile, error = _profile_from_payload(data)
    if error:
        return jsonify({"error": error}), 400
    if not update_specialist_profile(_database_path(), session["user_id"], profile):
        return jsonify({"error": "Your specialist profile could not be updated."}), 404
    return jsonify({"message": "Your specialist profile was updated."})


@specialists_bp.route("/api/specialists/me/password", methods=["POST"])
def update_specialist_password():
    if _role_required("specialist") is None:
        return jsonify({"error": "Specialist account access required."}), 403
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Submit password details as an object."}), 400
    result = change_password(
        _database_path(),
        session["user_id"],
        data.get("current_password", ""),
        data.get("new_password", ""),
    )
    if result == "invalid_current_password":
        return jsonify({"error": "Your current password was not recognized."}), 400
    if result == "invalid_new_password":
        return jsonify({
            "error": f"Use a new password between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters."
        }), 400
    return jsonify({"message": "Your password was updated."})
