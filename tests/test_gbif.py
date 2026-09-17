import unittest

from backend.gbif import (
    create_bounding_box,
    get_nearby_occurrences
)


class TestGBIF(unittest.TestCase):

    def test_bounding_box(self):
        bbox = create_bounding_box(
            latitude=30.901,
            longitude=75.8573,
            radius_km=25
        )

        self.assertIsInstance(bbox, dict)

        self.assertIn("min_lat", bbox)
        self.assertIn("max_lat", bbox)
        self.assertIn("min_lon", bbox)
        self.assertIn("max_lon", bbox)

        self.assertLess(bbox["min_lat"], bbox["max_lat"])
        self.assertLess(bbox["min_lon"], bbox["max_lon"])

    def test_gbif_returns_dict(self):
        result = get_nearby_occurrences(
            latitude=30.901,
            longitude=75.8573,
            radius_km=25,
            limit=10
        )

        self.assertIsInstance(result, dict)

    def test_gbif_result_has_status(self):
        result = get_nearby_occurrences(
            latitude=30.901,
            longitude=75.8573,
            radius_km=25,
            limit=10
        )

        self.assertIn("available", result)

    def test_gbif_result_structure(self):
        result = get_nearby_occurrences(
            latitude=30.901,
            longitude=75.8573,
            radius_km=25,
            limit=10
        )

        if result.get("available"):
            self.assertIn("record_count", result)
            self.assertIn("returned_records", result)
            self.assertIn("observed_taxa_count", result)
            self.assertIn("observed_taxa", result)

    def test_gbif_taxa_is_list(self):
        result = get_nearby_occurrences(
            latitude=30.901,
            longitude=75.8573,
            radius_km=25,
            limit=10
        )

        if result.get("available"):
            self.assertIsInstance(
                result["observed_taxa"],
                list
            )

    def test_invalid_coordinates(self):
        result = get_nearby_occurrences(
            latitude=None,
            longitude=None
        )

        self.assertIsInstance(result, dict)

        # Function should fail gracefully instead of crashing
        self.assertIn("available", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)