import unittest

from backend.knowledge_layer import (
    get_all_sites,
    get_site_by_id,
    get_sites_by_region,
    get_sites_by_condition,
    get_sites_by_biodiversity,
    search_environmental_knowledge,
    find_similar_environment,
    build_knowledge_context
)


# ==========================================================
# TEST ENVIRONMENT
# ==========================================================

TEST_PROFILE = {
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

class TestKnowledgeLayer(unittest.TestCase):

    # ------------------------------------------------------
    # 1. Dataset should contain sites
    # ------------------------------------------------------

    def test_dataset_loaded(self):

        sites = get_all_sites()

        self.assertIsInstance(
            sites,
            list
        )

        self.assertGreater(
            len(sites),
            0
        )

        print(
            "PASS: Environmental dataset loaded"
        )


    # ------------------------------------------------------
    # 2. Find site by ID
    # ------------------------------------------------------

    def test_get_site_by_id(self):

        site = get_site_by_id(
            "site_001"
        )

        self.assertIsNotNone(
            site
        )

        self.assertEqual(
            site["id"],
            "site_001"
        )

        print(
            "PASS: Site lookup by ID works"
        )


    # ------------------------------------------------------
    # 3. Find sites by region
    # ------------------------------------------------------

    def test_get_sites_by_region(self):

        sites = get_sites_by_region(
            "Punjab"
        )

        self.assertGreater(
            len(sites),
            0
        )

        self.assertEqual(
            sites[0]["region"],
            "Punjab"
        )

        print(
            "PASS: Region search works"
        )


    # ------------------------------------------------------
    # 4. Search by nested condition
    # ------------------------------------------------------

    def test_get_sites_by_condition(self):

        sites = get_sites_by_condition(
            "soil.organic_carbon_percent",
            0.3
        )

        self.assertGreater(
            len(sites),
            0
        )

        print(
            "PASS: Nested environmental condition search works"
        )


    # ------------------------------------------------------
    # 5. Search low biodiversity sites
    # ------------------------------------------------------

    def test_get_sites_by_biodiversity(self):

        sites = get_sites_by_biodiversity(
            species_richness="low"
        )

        self.assertGreater(
            len(sites),
            0
        )

        for site in sites:

            self.assertEqual(
                site["biodiversity"]["species_richness"],
                "low"
            )

        print(
            "PASS: Biodiversity search works"
        )


    # ------------------------------------------------------
    # 6. Environmental knowledge search
    # ------------------------------------------------------

    def test_environmental_search(self):

        sites = search_environmental_knowledge(
            region="Punjab",
            species_richness="low",
            land_use="cropland"
        )

        self.assertGreater(
            len(sites),
            0
        )

        print(
            "PASS: Combined environmental search works"
        )


    # ------------------------------------------------------
    # 7. Find similar environment
    # ------------------------------------------------------

    def test_similar_environment(self):

        sites = find_similar_environment(
            TEST_PROFILE
        )

        self.assertIsInstance(
            sites,
            list
        )

        self.assertGreater(
            len(sites),
            0
        )

        print(
            "PASS: Similar environment search works"
        )


    # ------------------------------------------------------
    # 8. Build complete knowledge context
    # ------------------------------------------------------

    def test_build_knowledge_context(self):

        context = build_knowledge_context(
            TEST_PROFILE
        )

        self.assertIsInstance(
            context,
            dict
        )

        self.assertIn(
            "matching_region_sites",
            context
        )

        self.assertIn(
            "matching_biodiversity_sites",
            context
        )

        self.assertIn(
            "similar_environments",
            context
        )

        print(
            "PASS: Knowledge context generated"
        )


    # ------------------------------------------------------
    # 9. Verify Punjab match
    # ------------------------------------------------------

    def test_punjab_match(self):

        context = build_knowledge_context(
            TEST_PROFILE
        )

        region_sites = context[
            "matching_region_sites"
        ]

        self.assertTrue(
            any(
                site.get("region") == "Punjab"
                for site in region_sites
            )
        )

        print(
            "PASS: Punjab environmental record matched"
        )


    # ------------------------------------------------------
    # 10. Verify low biodiversity match
    # ------------------------------------------------------

    def test_low_biodiversity_match(self):

        context = build_knowledge_context(
            TEST_PROFILE
        )

        biodiversity_sites = context[
            "matching_biodiversity_sites"
        ]

        self.assertTrue(
            any(
                site.get("biodiversity", {}).get(
                    "species_richness"
                ) == "low"
                for site in biodiversity_sites
            )
        )

        print(
            "PASS: Low biodiversity record matched"
        )


# ==========================================================
# RUN TESTS
# ==========================================================

if __name__ == "__main__":

    unittest.main(
        verbosity=2
    )