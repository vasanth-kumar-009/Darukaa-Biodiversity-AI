from pathlib import Path
import sys


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# Local imports
# ---------------------------------------------------------

from reasoning.environmental_reasoner import (
    analyze_environment
)

from rag.retrieve import retrieve_evidence


# ---------------------------------------------------------
# Evidence deduplication
# ---------------------------------------------------------

def deduplicate_evidence(
    evidence,
    max_per_source=3
):
    """
    Prevent the final evidence list from being dominated
    by chunks from one scientific source.
    """

    source_counts = {}

    unique_evidence = []

    for item in evidence:

        source = item.get(
            "source",
            "Unknown source"
        )

        count = source_counts.get(
            source,
            0
        )

        if count >= max_per_source:
            continue

        source_counts[source] = count + 1

        unique_evidence.append(item)

    return unique_evidence


# ---------------------------------------------------------
# Build RAG query
# ---------------------------------------------------------

def build_rag_query(
    profile,
    analysis
):
    """
    Convert the structured environmental profile and
    rule-based reasoning results into a scientific
    retrieval query.
    """

    soil = profile.get(
        "soil",
        {}
    )

    climate = profile.get(
        "climate",
        {}
    )

    land = profile.get(
        "land",
        {}
    )

    biodiversity = profile.get(
        "biodiversity",
        {}
    )

    human_impact = profile.get(
        "human_impact",
        {}
    )

    location = profile.get(
        "location",
        {}
    )

    findings = analysis.get(
        "findings",
        []
    )

    interactions = analysis.get(
        "interactions",
        []
    )

    # -----------------------------------------------------
    # Convert findings
    # -----------------------------------------------------

    finding_text = " ".join(
        str(item)
        for item in findings
    )

    # -----------------------------------------------------
    # Convert interactions
    # -----------------------------------------------------

    interaction_texts = []

    for interaction in interactions:

        if isinstance(
            interaction,
            dict
        ):

            interaction_texts.append(
                str(
                    interaction.get(
                        "interaction",
                        ""
                    )
                )
            )

            interaction_texts.append(
                str(
                    interaction.get(
                        "reasoning",
                        ""
                    )
                )
            )

        else:

            interaction_texts.append(
                str(interaction)
            )

    interaction_text = " ".join(
        interaction_texts
    )

    # -----------------------------------------------------
    # Construct scientific query
    # -----------------------------------------------------

    query_parts = [

        "biodiversity conservation",

        f"soil pH {soil.get('ph')}",

        (
            "soil organic carbon "
            f"{soil.get('organic_carbon_percent')} percent"
        ),

        (
            "soil moisture "
            f"{soil.get('moisture_percent')} percent"
        ),

        (
            "annual rainfall "
            f"{climate.get('rainfall_mm_year')} mm"
        ),

        (
            "temperature "
            f"{climate.get('temperature_celsius')} Celsius"
        ),

        (
            f"land use {land.get('land_use')}"
        ),

        (
            f"crop type {land.get('crop_type')}"
        ),

        (
            "species richness "
            f"{biodiversity.get('species_richness')}"
        ),

        (
            "habitat diversity "
            f"{biodiversity.get('habitat_diversity')}"
        ),

        (
            "pollution "
            f"{human_impact.get('pollution_level')}"
        ),

        (
            "deforestation "
            f"{human_impact.get('deforestation_level')}"
        ),

        (
            "habitat fragmentation "
            f"{human_impact.get('habitat_fragmentation')}"
        ),

        f"region {location.get('region')}",

        finding_text,

        interaction_text,

        (
            "soil health biodiversity "
            "water availability species survival "
            "land use habitat fragmentation "
            "agroforestry ecosystem services"
        )
    ]

    # Remove empty values

    query_parts = [
        str(part).strip()
        for part in query_parts
        if str(part).strip()
        and str(part).strip()
        != "None"
    ]

    return " ".join(query_parts)


# ---------------------------------------------------------
# Main RAG pipeline
# ---------------------------------------------------------

def run_environmental_rag(
    profile,
    top_k=8
):
    """
    Complete environmental RAG process:

    1. Analyze environmental profile
    2. Build scientific retrieval query
    3. Retrieve evidence from ChromaDB
    4. Remove excessive duplicate sources
    """

    # -----------------------------------------------------
    # Step 1: Rule-based environmental reasoning
    # -----------------------------------------------------

    analysis = analyze_environment(
        profile
    )

    # -----------------------------------------------------
    # Step 2: Build retrieval query
    # -----------------------------------------------------

    rag_query = build_rag_query(
        profile,
        analysis
    )

    print()
    print("=" * 60)
    print("RAG QUERY")
    print("=" * 60)
    print(rag_query)

    # -----------------------------------------------------
    # Step 3: Retrieve scientific evidence
    # -----------------------------------------------------

    evidence = retrieve_evidence(
        rag_query,
        top_k=top_k
    )

    # -----------------------------------------------------
    # Step 4: Deduplicate evidence
    # -----------------------------------------------------

    evidence = deduplicate_evidence(
        evidence,
        max_per_source=3
    )

    # -----------------------------------------------------
    # Print evidence
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("RETRIEVED SCIENTIFIC EVIDENCE")
    print("=" * 60)

    for index, item in enumerate(
        evidence,
        start=1
    ):

        print()
        print(
            f"[{index}] "
            f"{item.get('source')} "
            f"- Page {item.get('page')}"
        )

        print(
            item.get(
                "text",
                ""
            )[:500]
        )

    # -----------------------------------------------------
    # Return result
    # -----------------------------------------------------

    return {
        "analysis": analysis,
        "evidence": evidence,
        "rag_query": rag_query
    }


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

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
            "latitude": None,
            "longitude": None,
            "region": "Punjab"
        }
    }

    result = run_environmental_rag(
        test_profile,
        top_k=8
    )

    print()
    print("=" * 60)
    print("RAG TEST COMPLETE")
    print("=" * 60)

    print(
        f"Evidence retrieved: "
        f"{len(result['evidence'])}"
    )