import secrets

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

try:
    from backend.services.auth_service import (
        MAX_PASSWORD_LENGTH,
        MIN_PASSWORD_LENGTH,
        authenticate_user,
        create_user,
        validate_email,
        validate_password,
    )
except ModuleNotFoundError:
    from services.auth_service import (
        MAX_PASSWORD_LENGTH,
        MIN_PASSWORD_LENGTH,
        authenticate_user,
        create_user,
        validate_email,
        validate_password,
    )

auth_bp = Blueprint("auth", __name__)


def _database_path():
    return current_app.config["DATABASE_PATH"]


def _start_session(user):
    session.clear()
    session["user_id"] = user["id"]
    session["csrf_token"] = secrets.token_urlsafe(32)
    session.permanent = True


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id") is not None:
        return redirect(url_for("home"))
    error = None
    email = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        normalized_email = validate_email(email)
        password = request.form.get("password", "")
        user = authenticate_user(_database_path(), normalized_email, password) if normalized_email else None
        if user is None:
            error = "That email and password combination was not recognized."
        else:
            _start_session(user)
            return redirect(url_for("home"))
    return render_template("login.html", error=error, email=email)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id") is not None:
        return redirect(url_for("home"))
    error = None
    email = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("password_confirmation", "")
        normalized_email = validate_email(email)
        if not normalized_email:
            error = "Enter a valid email address."
        elif not validate_password(password):
            error = f"Use a password between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters."
        elif password != confirmation:
            error = "The passwords do not match."
        else:
            user = create_user(_database_path(), normalized_email, password)
            if user is None:
                error = "An account with that email already exists. Try signing in instead."
            else:
                _start_session(user)
                return redirect(url_for("home"))
    return render_template("register.html", error=error, email=email)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
