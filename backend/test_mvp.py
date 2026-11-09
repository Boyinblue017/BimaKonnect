import os
import sqlite3
import tempfile
import unittest

from backend.app import app
from backend.services.auth_service import initialize_database


class BimaKonnectMvpTests(unittest.TestCase):
    def setUp(self):
        self.database_dir = tempfile.TemporaryDirectory()
        app.config["DATABASE_PATH"] = os.path.join(self.database_dir.name, "users.sqlite3")
        initialize_database(app.config["DATABASE_PATH"])
        self.client = app.test_client()
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as browser_session:
            csrf_token = browser_session["csrf_token"]
        response = self.client.post(
            "/register",
            data={
                "csrf_token": csrf_token,
                "email": "tester@example.com",
                "password": "a-strong-test-password",
                "password_confirmation": "a-strong-test-password",
            },
        )
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        self.database_dir.cleanup()

    def post_api(self, path, payload):
        with self.client.session_transaction() as browser_session:
            csrf_token = browser_session["csrf_token"]
        return self.client.post(path, json=payload, headers={"X-CSRF-Token": csrf_token})

    def test_home_and_health_are_available(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        home.close()
        privacy = self.client.get("/privacy.html")
        self.assertEqual(privacy.status_code, 200)
        privacy.close()
        self.assertEqual(self.client.get("/api/health").get_json()["status"], "ok")

    def test_claim_guidance_is_tailored_to_motor_cover(self):
        response = self.post_api("/claims/guidance", {"cover_type": "motor", "incident": "accident"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Motor", response.get_json()["title"])

    def test_chat_understands_a_natural_motor_question(self):
        response = self.post_api("/chat", {"question": "What is motor insurance?"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["topic"], "motor insurance")

    def test_recommendations_include_reasons(self):
        response = self.post_api("/recommend", {"vehicle": True, "dependents": True})
        recommendations = response.get_json()["recommendations"]
        self.assertGreaterEqual(len(recommendations), 2)
        self.assertIn("reason", recommendations[0])

    def test_glossary_search(self):
        response = self.post_api("/glossary/search", {"query": "claim"})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.get_json()["total_results"], 0)

    def test_account_required_and_logout_ends_access(self):
        anonymous = app.test_client()
        self.assertEqual(anonymous.get("/").status_code, 302)
        self.assertEqual(anonymous.get("/mvp.html").status_code, 302)
        self.assertEqual(anonymous.get("/MVP.html").status_code, 302)
        self.assertEqual(anonymous.post("/chat", json={"question": "What is insurance?"}).status_code, 401)

        with self.client.session_transaction() as browser_session:
            csrf_token = browser_session["csrf_token"]
        response = self.client.post("/logout", data={"csrf_token": csrf_token})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get("/").status_code, 302)

    def test_registered_user_can_sign_in(self):
        client = app.test_client()
        client.get("/login")
        with client.session_transaction() as browser_session:
            csrf_token = browser_session["csrf_token"]
        response = client.post(
            "/login",
            data={
                "csrf_token": csrf_token,
                "email": "TESTER@example.com",
                "password": "a-strong-test-password",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(client.get("/").status_code, 200)

    def test_password_is_stored_as_a_hash(self):
        connection = sqlite3.connect(app.config["DATABASE_PATH"])
        try:
            password_hash = connection.execute(
                "SELECT password_hash FROM users WHERE email = ?",
                ("tester@example.com",),
            ).fetchone()[0]
        finally:
            connection.close()
        self.assertNotEqual(password_hash, "a-strong-test-password")
        self.assertTrue(password_hash.startswith("scrypt:"))

    def test_registration_rejects_short_passwords_and_duplicate_emails(self):
        client = app.test_client()
        client.get("/register")
        with client.session_transaction() as browser_session:
            csrf_token = browser_session["csrf_token"]
        response = client.post(
            "/register",
            data={
                "csrf_token": csrf_token,
                "email": "new@example.com",
                "password": "short",
                "password_confirmation": "short",
            },
        )
        self.assertIn(b"Use a password between 12 and 128 characters.", response.data)

        response = client.post(
            "/register",
            data={
                "csrf_token": csrf_token,
                "email": "TESTER@example.com",
                "password": "a-strong-test-password",
                "password_confirmation": "a-strong-test-password",
            },
        )
        self.assertIn(b"account with that email already exists", response.data)

    def test_protected_post_requires_csrf_token(self):
        response = self.client.post("/chat", json={"question": "What is insurance?"})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
