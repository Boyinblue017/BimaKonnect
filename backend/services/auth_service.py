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
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(database_path):
    os.makedirs(os.path.dirname(database_path) or ".", exist_ok=True)
    with _connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def validate_email(email):
    normalized_email = email.strip().lower()
    if len(normalized_email) > 254 or not EMAIL_PATTERN.fullmatch(normalized_email):
        return None
    return normalized_email


def validate_password(password):
    return MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH


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
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    if user is None or not check_password_hash(user["password_hash"], password):
        return None
    return {"id": user["id"], "email": user["email"]}


def get_user_by_id(database_path, user_id):
    with _connect(database_path) as connection:
        user = connection.execute(
            "SELECT id, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(user) if user else None
