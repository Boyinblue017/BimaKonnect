import unittest

from backend.app import app


class BimaKonnectMvpTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_and_health_are_available(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        home.close()
        privacy = self.client.get("/privacy.html")
        self.assertEqual(privacy.status_code, 200)
        privacy.close()
        self.assertEqual(self.client.get("/api/health").get_json()["status"], "ok")

    def test_chat_understands_a_natural_motor_question(self):
        response = self.client.post("/chat", json={"question": "What is motor insurance?"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["topic"], "motor insurance")

    def test_recommendations_include_reasons(self):
        response = self.client.post("/recommend", json={"vehicle": True, "dependents": True})
        recommendations = response.get_json()["recommendations"]
        self.assertGreaterEqual(len(recommendations), 2)
        self.assertIn("reason", recommendations[0])

    def test_glossary_search(self):
        response = self.client.post("/glossary/search", json={"query": "claim"})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.get_json()["total_results"], 0)

    def test_claim_guidance_is_tailored_to_motor_cover(self):
        response = self.client.post("/claims/guidance", json={"cover_type": "motor", "incident": "accident"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Motor", response.get_json()["title"])


if __name__ == "__main__":
    unittest.main()
