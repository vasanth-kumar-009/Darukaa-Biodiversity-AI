"""
Optimized Biodiversity AI Pipeline

RAG, structured knowledge and GBIF run in parallel.
Gemini runs after retrieval completes.
"""

from concurrent.futures import ThreadPoolExecutor

from rag.environmental_rag import run_environmental_rag

from backend.knowledge_layer import build_knowledge_context

from backend.llm_generator import (
    generate_biodiversity_response
)

from backend.gbif import (
    get_nearby_occurrences
)


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline(
    profile,
    user_question=None,
    chat_history=None
):

    print("\n" + "=" * 60)
    print("BIODIVERSITY AI PIPELINE")
    print("=" * 60)

    location = profile.get(
        "location",
        {}
    )

    latitude = location.get(
        "latitude"
    )

    longitude = location.get(
        "longitude"
    )

    # ========================================================
    # PARALLEL RETRIEVAL
    # ========================================================

    print(
        "\nStarting parallel retrieval:"
    )

    print(
        "- Scientific RAG"
    )

    print(
        "- Structured knowledge"
    )

    print(
        "- GBIF biodiversity data"
    )

    with ThreadPoolExecutor(
        max_workers=3
    ) as executor:

        # ----------------------------------------------------
        # Start RAG
        # ----------------------------------------------------

        rag_future = executor.submit(
            run_environmental_rag,
            profile,
            5
        )

        # ----------------------------------------------------
        # Start structured knowledge
        # ----------------------------------------------------

        knowledge_future = executor.submit(
            build_knowledge_context,
            profile
        )

        # ----------------------------------------------------
        # Start GBIF
        # ----------------------------------------------------

        gbif_future = executor.submit(
            get_nearby_occurrences,
            latitude,
            longitude,
            25,
            20
        )

        # ====================================================
        # RAG RESULT
        # ====================================================

        try:

            rag_result = rag_future.result()

            analysis = rag_result.get(
                "analysis",
                {}
            )

            evidence = rag_result.get(
                "evidence",
                []
            )

            print(
                "RAG complete:",
                len(evidence),
                "evidence chunks"
            )

        except Exception as exc:

            print(
                "RAG failed:",
                repr(exc)
            )

            analysis = {}

            evidence = []

        # ====================================================
        # STRUCTURED KNOWLEDGE RESULT
        # ====================================================

        try:

            knowledge_context = (
                knowledge_future.result()
            )

            print(
                "Structured knowledge complete."
            )

        except Exception as exc:

            print(
                "Structured knowledge failed:",
                repr(exc)
            )

            knowledge_context = {

                "dataset_source": None,

                "matching_region_sites": [],

                "matching_biodiversity_sites": [],

                "similar_environments": [],

                "error": str(exc)
            }

        # ====================================================
        # GBIF RESULT
        # ====================================================

        try:

            gbif_data = (
                gbif_future.result()
            )

            if gbif_data.get(
                "available",
                False
            ):

                print(
                    "GBIF complete:",
                    gbif_data.get(
                        "record_count",
                        0
                    ),
                    "matching records"
                )

                print(
                    "Observed taxa:",
                    gbif_data.get(
                        "observed_taxa_count",
                        0
                    )
                )

            else:

                print(
                    "GBIF unavailable:",
                    gbif_data.get(
                        "error",
                        "Unknown error"
                    )
                )

        except Exception as exc:

            print(
                "GBIF failed:",
                repr(exc)
            )

            gbif_data = {

                "available": False,

                "source":
                    "GBIF Occurrence Search API",

                "error": str(exc),

                "record_count": 0,

                "returned_records": 0,

                "observed_taxa_count": 0,

                "observed_taxa": [],

                "occurrences": []
            }

    # ========================================================
    # GEMINI
    # ========================================================

    print(
        "\nGenerating final AI response..."
    )

    response = generate_biodiversity_response(

        profile=profile,

        analysis=analysis,

        evidence=evidence,

        user_question=user_question,

        chat_history=chat_history,

        gbif_data=gbif_data,

        knowledge_context=knowledge_context
    )

    print(
        "Pipeline completed successfully."
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "success": True,

        "question":
            user_question,

        "environment":
            profile,

        "analysis":
            analysis,

        "response":
            response,

        "scientific_evidence":
            evidence,

        "location_biodiversity":
            gbif_data,

        "structured_knowledge":
            knowledge_context
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    test_profile = {

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

            "latitude": 30.9010,

            "longitude": 75.8573,

            "region": "Punjab"
        }
    }

    result = run_pipeline(

        profile=test_profile,

        user_question=(
            "How can biodiversity be improved "
            "in this environment?"
        ),

        chat_history=[]
    )

    print(
        "\nFINAL RESPONSE"
    )

    print(
        result["response"]
    )