import unittest

from reasoning.environmental_reasoner import analyze_environment


# ==========================================================
# TEST PROFILE
# ==========================================================

LOW_BIODIVERSITY_PROFILE = {
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
        "latitude": 30.901,
        "longitude": 75.8573,
        "region": "Punjab"
    }
}


# ==========================================================
# TEST CLASS
# ==========================================================

class TestEnvironmentalReasoning(unittest.TestCase):

    # ------------------------------------------------------
    # 1. Reasoning should return structured output
    # ------------------------------------------------------

    def test_reasoning_structure(self):

        result = analyze_environment(
            LOW_BIODIVERSITY_PROFILE
        )

        self.assertIsInstance(
            result,
            dict
        )

        self.assertIn(
            "findings",
            result
        )

        self.assertIn(
            "interactions",
            result
        )

        self.assertIn(
            "recommendations",
            result
        )

        print(
            "PASS: Reasoning returns correct structure"
        )


    # ------------------------------------------------------
    # 2. Detect low soil organic carbon
    # ------------------------------------------------------

    def test_low_soil_carbon(self):

        result = analyze_environment(
            LOW_BIODIVERSITY_PROFILE
        )

        findings_text = " ".join(
            str(x).lower()
            for x in result["findings"]
        )

        self.assertTrue(
            "organic carbon" in findings_text
            or "soil organic carbon" in findings_text
        )

        print(
            "PASS: Low soil organic carbon detected"
        )


    # ------------------------------------------------------
    # 3. Detect low soil moisture
    # ------------------------------------------------------

    def test_low_soil_moisture(self):

        result = analyze_environment(
            LOW_BIODIVERSITY_PROFILE
        )

        findings_text = " ".join(
            str(x).lower()
            for x in result["findings"]
        )

        self.assertIn(
            "soil moisture",
            findings_text
        )

        print(
            "PASS: Low soil moisture detected"
        )


    # ------------------------------------------------------
    # 4. Detect low rainfall
    # ------------------------------------------------------

    def test_low_rainfall(self):

        result = analyze_environment(
            LOW_BIODIVERSITY_PROFILE
        )

        findings_text = " ".join(
            str(x).lower()
            for x in result["findings"]
        )

        self.assertIn(
            "rainfall",
            findings_text
        )

        print(
            "PASS: Low rainfall detected"
        )


    # ------------------------------------------------------
    # 5. Detect monoculture
    # ------------------------------------------------------

    def test_monoculture(self):

        result = analyze_environment(
            LOW_BIODIVERSITY_PROFILE
        )

        findings_text = " ".join(
            str(x).lower()
            for x in result["findings"]
        )

        self.assertIn(
            "monoculture",
            findings_text
        )

        print(
            "PASS: Monoculture detected"
        )


    # ------------------------------------------------------
    # 6. Detect low species richness
    # ------------------------------------------------------

    def test_low_species_richness(self):

        result = analyze_environment(
            LOW_BIODIVERSITY_PROFILE
        )

        findings_text = " ".join(
            str(x).lower()
            for x in result["findings"]
        )

        self.assertIn(
            "species richness",
            findings_text
        )

        print(
            "PASS: Low species richness detected"
        )


    # ------------------------------------------------------
    # 7. Detect low habitat diversity
    # ------------------------------------------------------

    def test_low_habitat_diversity(self):

        result = analyze_environment(
            LOW_BIODIVERSITY_PROFILE
        )

        findings_text = " ".join(
            str(x).lower()
            for x in result["findings"]
        )

        self.assertIn(
            "habitat diversity",
            findings_text
        )

        print(
            "PASS: Low habitat diversity detected"
        )


    # ------------------------------------------------------
    # 8. Test multi-variable interaction
    # ------------------------------------------------------

    def test_soil_rainfall_moisture_interaction(self):

        result = analyze_environment(
            LOW_BIODIVERSITY_PROFILE
        )

        interactions = result["interactions"]

        interaction_text = " ".join(
            str(x).lower()
            for x in interactions
        )

        self.assertTrue(
            (
                "organic carbon" in interaction_text
                and "rainfall" in interaction_text
            )
            or
            (
                "soil organic carbon" in interaction_text
                and "moisture" in interaction_text
            )
        )

        print(
            "PASS: Soil-climate-moisture interaction detected"
        )


    # ------------------------------------------------------
    # 9. Test monoculture + biodiversity interaction
    # ------------------------------------------------------

    def test_monoculture_biodiversity_interaction(self):

        result = analyze_environment(
            LOW_BIODIVERSITY_PROFILE
        )

        interactions = result["interactions"]

        interaction_text = " ".join(
            str(x).lower()
            for x in interactions
        )

        self.assertTrue(
            "monoculture" in interaction_text
            and "biodiversity" in interaction_text
            or
            "monoculture" in interaction_text
            and "species" in interaction_text
        )

        print(
            "PASS: Monoculture-biodiversity interaction detected"
        )


    # ------------------------------------------------------
    # 10. Recommendations should exist
    # ------------------------------------------------------

    def test_recommendations_exist(self):

        result = analyze_environment(
            LOW_BIODIVERSITY_PROFILE
        )

        self.assertGreater(
            len(result["recommendations"]),
            0
        )

        print(
            "PASS: Biodiversity recommendations generated"
        )


# ==========================================================
# RUN TESTS
# ==========================================================

if __name__ == "__main__":

    unittest.main(
        verbosity=2
    )