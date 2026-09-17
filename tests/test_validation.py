import unittest

from backend.validation import validate_environment


# ==========================================================
# TEST DATA
# ==========================================================

VALID_PROFILE = {
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

class TestEnvironmentalValidation(unittest.TestCase):

    # ------------------------------------------------------
    # 1. Valid profile
    # ------------------------------------------------------

    def test_valid_environment(self):

        result = validate_environment(
            VALID_PROFILE
        )

        self.assertTrue(
            result["valid"]
        )

        self.assertEqual(
            len(result["errors"]),
            0
        )

        print("PASS: Valid environmental profile")


    # ------------------------------------------------------
    # 2. Invalid pH
    # ------------------------------------------------------

    def test_invalid_ph(self):

        profile = VALID_PROFILE.copy()

        profile["soil"] = {
            **VALID_PROFILE["soil"],
            "ph": 25
        }

        result = validate_environment(
            profile
        )

        self.assertFalse(
            result["valid"]
        )

        self.assertGreater(
            len(result["errors"]),
            0
        )

        print("PASS: Invalid pH detected")


    # ------------------------------------------------------
    # 3. Invalid organic carbon
    # ------------------------------------------------------

    def test_invalid_organic_carbon(self):

        profile = VALID_PROFILE.copy()

        profile["soil"] = {
            **VALID_PROFILE["soil"],
            "organic_carbon_percent": 150
        }

        result = validate_environment(
            profile
        )

        self.assertFalse(
            result["valid"]
        )

        print(
            "PASS: Invalid organic carbon detected"
        )


    # ------------------------------------------------------
    # 4. Invalid soil moisture
    # ------------------------------------------------------

    def test_invalid_moisture(self):

        profile = VALID_PROFILE.copy()

        profile["soil"] = {
            **VALID_PROFILE["soil"],
            "moisture_percent": 120
        }

        result = validate_environment(
            profile
        )

        self.assertFalse(
            result["valid"]
        )

        print(
            "PASS: Invalid soil moisture detected"
        )


    # ------------------------------------------------------
    # 5. Invalid rainfall
    # ------------------------------------------------------

    def test_invalid_rainfall(self):

        profile = VALID_PROFILE.copy()

        profile["climate"] = {
            **VALID_PROFILE["climate"],
            "rainfall_mm_year": -500
        }

        result = validate_environment(
            profile
        )

        self.assertFalse(
            result["valid"]
        )

        print(
            "PASS: Invalid rainfall detected"
        )


    # ------------------------------------------------------
    # 6. Invalid temperature
    # ------------------------------------------------------

    def test_invalid_temperature(self):

        profile = VALID_PROFILE.copy()

        profile["climate"] = {
            **VALID_PROFILE["climate"],
            "temperature_celsius": 100
        }

        result = validate_environment(
            profile
        )

        self.assertFalse(
            result["valid"]
        )

        print(
            "PASS: Invalid temperature detected"
        )


    # ------------------------------------------------------
    # 7. Invalid latitude
    # ------------------------------------------------------

    def test_invalid_latitude(self):

        profile = VALID_PROFILE.copy()

        profile["location"] = {
            **VALID_PROFILE["location"],
            "latitude": 150
        }

        result = validate_environment(
            profile
        )

        self.assertFalse(
            result["valid"]
        )

        print(
            "PASS: Invalid latitude detected"
        )


    # ------------------------------------------------------
    # 8. Invalid longitude
    # ------------------------------------------------------

    def test_invalid_longitude(self):

        profile = VALID_PROFILE.copy()

        profile["location"] = {
            **VALID_PROFILE["location"],
            "longitude": 250
        }

        result = validate_environment(
            profile
        )

        self.assertFalse(
            result["valid"]
        )

        print(
            "PASS: Invalid longitude detected"
        )


    # ------------------------------------------------------
    # 9. Missing values
    # ------------------------------------------------------

    def test_incomplete_environment(self):

        profile = {
            "soil": {
                "ph": 6.5
            }
        }

        result = validate_environment(
            profile
        )

        # The validator should still return a structured
        # result instead of crashing.

        self.assertIn(
            "valid",
            result
        )

        self.assertIn(
            "errors",
            result
        )

        self.assertIn(
            "warnings",
            result
        )

        self.assertIn(
            "completeness_percent",
            result
        )

        print(
            "PASS: Incomplete environment handled"
        )


# ==========================================================
# RUN TESTS
# ==========================================================

if __name__ == "__main__":

    unittest.main(
        verbosity=2
    )