import unittest

from rag.environmental_rag import run_environmental_rag


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

class TestEnvironmentalRAG(unittest.TestCase):

    # ------------------------------------------------------
    # 1. RAG should return a dictionary
    # ------------------------------------------------------

    def test_rag_returns_result(self):

        result = run_environmental_rag(
            TEST_PROFILE,
            top_k=8
        )

        self.assertIsInstance(
            result,
            dict
        )

        print(
            "PASS: RAG returned a result"
        )


    # ------------------------------------------------------
    # 2. Analysis should exist
    # ------------------------------------------------------

    def test_analysis_exists(self):

        result = run_environmental_rag(
            TEST_PROFILE,
            top_k=8
        )

        self.assertIn(
            "analysis",
            result
        )

        self.assertIsInstance(
            result["analysis"],
            dict
        )

        print(
            "PASS: Environmental analysis exists"
        )


    # ------------------------------------------------------
    # 3. RAG query should be generated
    # ------------------------------------------------------

    def test_rag_query_exists(self):

        result = run_environmental_rag(
            TEST_PROFILE,
            top_k=8
        )

        self.assertIn(
            "rag_query",
            result
        )

        self.assertIsInstance(
            result["rag_query"],
            str
        )

        self.assertGreater(
            len(result["rag_query"]),
            0
        )

        print(
            "PASS: RAG query generated"
        )


    # ------------------------------------------------------
    # 4. Scientific evidence should be retrieved
    # ------------------------------------------------------

    def test_scientific_evidence_retrieved(self):

        result = run_environmental_rag(
            TEST_PROFILE,
            top_k=8
        )

        evidence = result.get(
            "evidence",
            []
        )

        self.assertGreater(
            len(evidence),
            0
        )

        print(
            f"PASS: Scientific evidence retrieved ({len(evidence)} chunks)"
        )


    # ------------------------------------------------------
    # 5. Evidence should contain source information
    # ------------------------------------------------------

    def test_evidence_has_source(self):

        result = run_environmental_rag(
            TEST_PROFILE,
            top_k=8
        )

        evidence = result.get(
            "evidence",
            []
        )

        self.assertGreater(
            len(evidence),
            0
        )

        for item in evidence:

            self.assertIn(
                "source",
                item
            )

        print(
            "PASS: Evidence contains source information"
        )


    # ------------------------------------------------------
    # 6. Evidence should contain text
    # ------------------------------------------------------

    def test_evidence_has_text(self):

        result = run_environmental_rag(
            TEST_PROFILE,
            top_k=8
        )

        evidence = result.get(
            "evidence",
            []
        )

        self.assertGreater(
            len(evidence),
            0
        )

        valid_text_found = False

        for item in evidence:

            text = item.get(
                "text",
                item.get(
                    "content",
                    ""
                )
            )

            if text and len(text.strip()) > 0:

                valid_text_found = True
                break

        self.assertTrue(
            valid_text_found
        )

        print(
            "PASS: Evidence contains usable text"
        )


    # ------------------------------------------------------
    # 7. Evidence should be environmental/scientific
    # ------------------------------------------------------

    def test_relevant_scientific_sources(self):

        result = run_environmental_rag(
            TEST_PROFILE,
            top_k=8
        )

        evidence = result.get(
            "evidence",
            []
        )

        self.assertGreater(
            len(evidence),
            0
        )

        source_text = " ".join(
            str(item.get("source", "")).lower()
            for item in evidence
        )

        relevant_terms = [
            "soil",
            "biodiversity",
            "agroforestry",
            "fao",
            "land"
        ]

        self.assertTrue(
            any(
                term in source_text
                for term in relevant_terms
            )
        )

        print(
            "PASS: Relevant scientific sources retrieved"
        )


# ==========================================================
# RUN TESTS
# ==========================================================

if __name__ == "__main__":

    unittest.main(
        verbosity=2
    )