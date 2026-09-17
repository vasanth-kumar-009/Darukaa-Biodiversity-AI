import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


TEST_ENVIRONMENT = {
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


MOCK_GEMINI_RESPONSE = {
    "assessment": "The environment shows several biodiversity pressures.",
    "key_interactions": [
        {
            "interaction": "Low soil organic carbon + low soil moisture + low rainfall",
            "reasoning": "These conditions can increase environmental stress and affect ecosystem functioning."
        }
    ],
    "recommendations": [
        {
            "action": "Increase habitat and crop diversity using locally appropriate practices.",
            "why_it_works": "Greater diversity can support ecosystem functions and habitat availability.",
            "impacted_metrics": [
                "soil organic carbon",
                "habitat diversity",
                "species richness"
            ],
            "time_horizon": "medium-term",
            "confidence": "moderate"
        }
    ],
    "scientific_evidence": [
        {
            "source": "FAO_soil_biodiversity.pdf",
            "page": "10",
            "evidence": "Soil organisms contribute to soil processes and ecosystem health."
        }
    ],
    "data_limitations": [
        "The demonstration environmental dataset is not real field measurements.",
        "GBIF observations do not represent complete species richness."
    ]
}


class TestAPI(unittest.TestCase):

    def test_root(self):
        response = client.get("/")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIsInstance(data, dict)

    def test_health(self):
        response = client.get("/health")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIsInstance(data, dict)

    def test_info(self):
        response = client.get("/info")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIsInstance(data, dict)

    def test_analyze_requires_question(self):
        response = client.post(
            "/analyze",
            json={
                "environment": TEST_ENVIRONMENT
            }
        )

        self.assertEqual(response.status_code, 422)

    @patch(
        "backend.biodiversity_pipeline.generate_biodiversity_response",
        return_value=MOCK_GEMINI_RESPONSE
    )
    def test_analyze_endpoint(self, mock_gemini):
        response = client.post(
            "/analyze",
            json={
                "question": "How can biodiversity be improved?",
                "environment": TEST_ENVIRONMENT
            }
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn("success", data)
        self.assertIn("response", data)
        self.assertIn("analysis", data)
        self.assertIn("scientific_evidence", data)
        self.assertIn("data_quality", data)
        self.assertIn("location_biodiversity", data)

        mock_gemini.assert_called_once()

    @patch(
        "backend.biodiversity_pipeline.generate_biodiversity_response",
        return_value=MOCK_GEMINI_RESPONSE
    )
    def test_chat_endpoint(self, mock_gemini):
        response = client.post(
            "/chat",
            json={
                "session_id": "test_session_001",
                "question": "What is the main biodiversity problem?",
                "environment": TEST_ENVIRONMENT
            }
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn("success", data)
        self.assertIn("response", data)
        self.assertIn("analysis", data)
        self.assertIn("scientific_evidence", data)
        self.assertIn("data_quality", data)

        mock_gemini.assert_called_once()

    @patch(
        "backend.biodiversity_pipeline.generate_biodiversity_response",
        return_value=MOCK_GEMINI_RESPONSE
    )
    def test_chat_memory(self, mock_gemini):
        session_id = "test_memory_session"

        response1 = client.post(
            "/chat",
            json={
                "session_id": session_id,
                "question": "What is the environmental condition?",
                "environment": TEST_ENVIRONMENT
            }
        )

        self.assertEqual(response1.status_code, 200)

        response2 = client.post(
            "/chat",
            json={
                "session_id": session_id,
                "question": "What should I improve first?"
            }
        )

        self.assertEqual(response2.status_code, 200)

        data = response2.json()

        self.assertIn("success", data)
        self.assertIn("response", data)
        self.assertIn("analysis", data)

        self.assertEqual(mock_gemini.call_count, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)