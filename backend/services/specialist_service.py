import sqlite3

from werkzeug.security import generate_password_hash

try:
    from backend.services.auth_service import _connect
except ModuleNotFoundError:
    from services.auth_service import _connect


def create_specialist(database_path, profile, temporary_password):
    with _connect(database_path) as connection:
        cursor = connection.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, 'specialist')",
            (profile["login_email"], generate_password_hash(temporary_password)),
        )
        user_id = cursor.lastrowid
        connection.execute(
            """
            INSERT INTO specialist_profiles
                (user_id, display_name, public_email, phone, specialty, region, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                profile["display_name"],
                profile["public_email"],
                profile["phone"],
                profile["specialty"],
                profile["region"],
                profile["bio"],
            ),
        )
    return user_id


def get_specialist_profile(database_path, user_id):
    with _connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT display_name, public_email, phone, specialty, region, bio
            FROM specialist_profiles WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def update_specialist_profile(database_path, user_id, profile):
    with _connect(database_path) as connection:
        cursor = connection.execute(
            """
            UPDATE specialist_profiles
            SET display_name = ?, public_email = ?, phone = ?, specialty = ?,
                region = ?, bio = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (
                profile["display_name"],
                profile["public_email"],
                profile["phone"],
                profile["specialty"],
                profile["region"],
                profile["bio"],
                user_id,
            ),
        )
    return cursor.rowcount == 1


def list_specialists(database_path, reviewer_id):
    with _connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT p.user_id AS id, p.user_id = ? AS is_own_profile,
                   p.display_name, p.public_email, p.phone,
                   p.specialty, p.region, p.bio,
                   ROUND(AVG(r.rating), 1) AS average_rating,
                   COUNT(r.rating) AS rating_count,
                   MAX(CASE WHEN r.reviewer_id = ? THEN r.rating END) AS my_rating
            FROM specialist_profiles p
            JOIN users u ON u.id = p.user_id AND u.role = 'specialist'
            LEFT JOIN specialist_ratings r ON r.specialist_id = p.user_id
            GROUP BY p.user_id
            ORDER BY p.display_name COLLATE NOCASE
            """,
            (reviewer_id, reviewer_id),
        ).fetchall()
    return [dict(row) for row in rows]


def rate_specialist(database_path, specialist_id, reviewer_id, rating):
    try:
        with _connect(database_path) as connection:
            profile = connection.execute(
                "SELECT user_id FROM specialist_profiles WHERE user_id = ?",
                (specialist_id,),
            ).fetchone()
            if profile is None:
                return "not_found"
            if specialist_id == reviewer_id:
                return "self_rating"
            connection.execute(
                """
                INSERT INTO specialist_ratings (specialist_id, reviewer_id, rating)
                VALUES (?, ?, ?)
                ON CONFLICT (specialist_id, reviewer_id)
                DO UPDATE SET rating = excluded.rating, created_at = CURRENT_TIMESTAMP
                """,
                (specialist_id, reviewer_id, rating),
            )
    except sqlite3.IntegrityError:
        return "invalid_rating"
    return "ok"
