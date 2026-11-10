from contextlib import contextmanager
import os
import re
import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128


@contextmanager
def _connect(database_path):
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(database_path, admin_email=None, admin_password=None):
    if bool(admin_email) != bool(admin_password):
        raise ValueError("Set both ADMIN_EMAIL and ADMIN_PASSWORD to provision an administrator.")
    if admin_email:
        admin_email = validate_email(admin_email)
        if not admin_email or not validate_password(admin_password):
            raise ValueError("ADMIN_EMAIL must be valid and ADMIN_PASSWORD must be 12-128 characters.")

    os.makedirs(os.path.dirname(database_path) or ".", exist_ok=True)
    with _connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL DEFAULT 'user'
            )
            """
        )
        columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(users)")
        }
        if "role" not in columns:
            connection.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS specialist_profiles (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                display_name TEXT NOT NULL,
                public_email TEXT NOT NULL,
                phone TEXT NOT NULL,
                specialty TEXT NOT NULL,
                region TEXT NOT NULL,
                bio TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS specialist_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                specialist_id INTEGER NOT NULL REFERENCES specialist_profiles(user_id) ON DELETE CASCADE,
                reviewer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (specialist_id, reviewer_id)
            )
            """
        )
        if admin_email:
            existing_admin = connection.execute(
                "SELECT id FROM users WHERE email = ?",
                (admin_email,),
            ).fetchone()
            if existing_admin:
                connection.execute(
                    "UPDATE users SET role = 'admin' WHERE id = ?",
                    (existing_admin["id"],),
                )
            else:
                connection.execute(
                    "INSERT INTO users (email, password_hash, role) VALUES (?, ?, 'admin')",
                    (admin_email, generate_password_hash(admin_password)),
                )


def validate_email(email):
    normalized_email = email.strip().lower()
    if len(normalized_email) > 254 or not EMAIL_PATTERN.fullmatch(normalized_email):
        return None
    return normalized_email


def validate_password(password):
    return isinstance(password, str) and MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH


def create_user(database_path, email, password):
    password_hash = generate_password_hash(password)
    try:
        with _connect(database_path) as connection:
            cursor = connection.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash),
            )
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    return get_user_by_id(database_path, user_id)


def authenticate_user(database_path, email, password):
    with _connect(database_path) as connection:
        user = connection.execute(
            "SELECT id, email, password_hash, role FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    if user is None or not check_password_hash(user["password_hash"], password):
        return None
    return {"id": user["id"], "email": user["email"], "role": user["role"]}


def get_user_by_id(database_path, user_id):
    with _connect(database_path) as connection:
        user = connection.execute(
            "SELECT id, email, role FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(user) if user else None


def change_password(database_path, user_id, current_password, new_password):
    with _connect(database_path) as connection:
        user = connection.execute(
            "SELECT password_hash FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if user is None or not check_password_hash(user["password_hash"], current_password):
            return "invalid_current_password"
        if not validate_password(new_password):
            return "invalid_new_password"
        connection.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(new_password), user_id),
        )
    return "ok"
