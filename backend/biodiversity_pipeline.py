"""
Main Biodiversity AI Pipeline

Pipeline flow:
1. Rule-based environmental reasoning
2. Scientific RAG retrieval
3. Structured environmental knowledge retrieval
4. GBIF location-based biodiversity lookup
5. Gemini response generation
6. Return complete evidence-backed result
"""

from rag.environmental_rag import run_environmental_rag
from backend.knowledge_layer import build_knowledge_context
from backend.llm_generator import generate_biodiversity_response
from backend.gbif import get_nearby_occurrences


def run_pipeline(
    profile,
    user_question=None,
    chat_history=None
):
    """
    Run the complete biodiversity intelligence pipeline.

    Parameters
    ----------
    profile : dict
        Structured environmental profile.

    user_question : str, optional
        User's natural-language question.

    chat_history : list, optional
        Previous conversation messages.

    Returns
    -------
    dict
        Complete pipeline result.
    """

    print("\n" + "=" * 60)
    print("BIODIVERSITY AI PIPELINE")
    print("=" * 60)

    # ==========================================================
    # 1. RULE-BASED ENVIRONMENTAL REASONING + RAG
    # ==========================================================

    print("\n[1/5] Running environmental reasoning + scientific RAG...")

    rag_result = run_environmental_rag(
        profile,
        top_k=8
    )

    analysis = rag_result.get(
        "analysis",
        {}
    )

    evidence = rag_result.get(
        "evidence",
        []
    )

    print(
        f"Scientific evidence retrieved: {len(evidence)}"
    )

    # ==========================================================
    # 2. STRUCTURED ENVIRONMENTAL KNOWLEDGE
    # ==========================================================

    print(
        "\n[2/5] Retrieving structured environmental knowledge..."
    )

    try:
        knowledge_context = build_knowledge_context(
            profile
        )

        print(
            "Region matches:",
            len(
                knowledge_context.get(
                    "matching_region_sites",
                    []
                )
            )
        )

        print(
            "Biodiversity matches:",
            len(
                knowledge_context.get(
                    "matching_biodiversity_sites",
                    []
                )
            )
        )

        print(
            "Similar environments:",
            len(
                knowledge_context.get(
                    "similar_environments",
                    []
                )
            )
        )

    except Exception as e:

        print(
            "Structured knowledge retrieval failed:",
            str(e)
        )

        # Keep pipeline running even if structured
        # knowledge retrieval fails.
        knowledge_context = {
            "dataset_source": None,
            "matching_region_sites": [],
            "matching_biodiversity_sites": [],
            "similar_environments": [],
            "error": str(e)
        }

    # ==========================================================
    # 3. GBIF LOCATION BIODIVERSITY
    # ==========================================================

    print(
        "\n[3/5] Retrieving location-based biodiversity data..."
    )

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

    try:

        gbif_data = get_nearby_occurrences(
            latitude=latitude,
            longitude=longitude
        )

        if gbif_data.get("available"):

            print(
                "GBIF records:",
                gbif_data.get(
                    "record_count",
                    0
                )
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
                "GBIF data unavailable:",
                gbif_data.get(
                    "error",
                    "No data"
                )
            )

    except Exception as e:

        print(
            "GBIF retrieval failed:",
            str(e)
        )

        gbif_data = {
            "available": False,
            "source": "GBIF",
            "error": str(e),
            "record_count": 0,
            "returned_records": 0,
            "observed_taxa_count": 0,
            "observed_taxa": [],
            "occurrences": []
        }

    # ==========================================================
    # 4. GEMINI RESPONSE GENERATION
    # ==========================================================

    print(
        "\n[4/5] Generating evidence-backed biodiversity response..."
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
        "[5/5] Pipeline completed successfully."
    )

    # ==========================================================
    # 5. FINAL RESULT
    # ==========================================================

    return {
        "success": True,

        "question": user_question,

        "environment": profile,

        # Rule-based reasoning
        "analysis": analysis,

        # Final Gemini-generated answer
        "response": response,

        # Scientific RAG evidence
        "scientific_evidence": evidence,

        # GBIF biodiversity observations
        "location_biodiversity": gbif_data,

        # Structured environmental dataset
        "structured_knowledge": knowledge_context
    }


# ==============================================================
# TEST
# ==============================================================

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
            "How can biodiversity be improved in this environment?"
        ),
        chat_history=[]
    )

    print("\n" + "=" * 60)
    print("FINAL RESPONSE")
    print("=" * 60)

    print(result["response"])