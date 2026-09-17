import unittest

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


VALID_ENVIRONMENT = {
    "soil": {
        "ph": 6.5,
        "organic_carbon_percent": 0.3,
        "moisture_percent": 15
    },
    "climate": {
        "rainfall_mm_year": 450,
        "temperature_celsius": 31
    },
    "land": {
        "land_use": "cropland",
        "crop_type": "wheat_monoculture"
    },
    "biodiversity": {
        "species_richness": "low",
        "habitat_diversity": "low"
    },
    "human_impact": {
        "pollution_level": "moderate",
        "deforestation_level": "low",
        "habitat_fragmentation": "moderate"
    },
    "location": {
        "latitude": None,
        "longitude": None,
        "region": "Punjab"
    }
}


class TestEdgeCases(unittest.TestCase):

    def test_missing_environment(self):
        response = client.post(
            "/analyze",
            json={
                "question": "How can biodiversity be improved?"
            }
        )

        self.assertEqual(response.status_code, 422)

    def test_missing_question(self):
        response = client.post(
            "/analyze",
            json={
                "environment": VALID_ENVIRONMENT
            }
        )

        self.assertEqual(response.status_code, 422)

    def test_invalid_ph(self):
        environment = VALID_ENVIRONMENT.copy()
        environment["soil"] = environment["soil"].copy()
        environment["soil"]["ph"] = 20

        response = client.post(
            "/analyze",
            json={
                "question": "Analyze this environment",
                "environment": environment
            }
        )

        self.assertIn(response.status_code, [200, 400, 422])

    def test_invalid_latitude(self):
        environment = VALID_ENVIRONMENT.copy()
        environment["location"] = {
            "latitude": 100,
            "longitude": 75,
            "region": "Punjab"
        }

        response = client.post(
            "/analyze",
            json={
                "question": "Analyze this environment",
                "environment": environment
            }
        )

        self.assertIn(response.status_code, [200, 400, 422])

    def test_invalid_longitude(self):
        environment = VALID_ENVIRONMENT.copy()
        environment["location"] = {
            "latitude": 30,
            "longitude": 200,
            "region": "Punjab"
        }

        response = client.post(
            "/analyze",
            json={
                "question": "Analyze this environment",
                "environment": environment
            }
        )

        self.assertIn(response.status_code, [200, 400, 422])

    def test_empty_question(self):
        response = client.post(
            "/analyze",
            json={
                "question": "",
                "environment": VALID_ENVIRONMENT
            }
        )

        self.assertIn(response.status_code, [200, 400, 422])

    def test_chat_missing_session_id(self):
        response = client.post(
            "/chat",
            json={
                "question": "What should I improve?",
                "environment": VALID_ENVIRONMENT
            }
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main(verbosity=2)