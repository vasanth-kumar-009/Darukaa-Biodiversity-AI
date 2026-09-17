import sys
from pathlib import Path

# --------------------------------------------------
# Project root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# --------------------------------------------------
# Imports
# --------------------------------------------------

import chromadb
from sentence_transformers import SentenceTransformer

from reasoning.environmental_reasoner import analyze_environment


# --------------------------------------------------
# Configuration
# --------------------------------------------------

CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "environmental_knowledge"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

TOP_K = 8


# --------------------------------------------------
# Load embedding model
# --------------------------------------------------

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

print("Embedding model loaded.")


# --------------------------------------------------
# ChromaDB
# --------------------------------------------------

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = chroma_client.get_collection(
    name=COLLECTION_NAME
)

print(
    f"Knowledge base contains "
    f"{collection.count()} chunks."
)


# ==================================================
# RAG RETRIEVAL
# ==================================================

def retrieve_evidence(
    query,
    top_k=TOP_K
):

    query_embedding = embedding_model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    evidence = []

    for i, text in enumerate(documents):

        metadata = (
            metadatas[i]
            if i < len(metadatas)
            else {}
        )

        distance = (
            distances[i]
            if i < len(distances)
            else None
        )

        evidence.append(
            {
                "text": text,

                "source": metadata.get(
                    "source",
                    "Unknown"
                ),

                "category": metadata.get(
                    "category",
                    "Unknown"
                ),

                "page": metadata.get(
                    "page",
                    "Unknown"
                ),

                "distance": distance
            }
        )

    return evidence


# ==================================================
# REMOVE DUPLICATE / NEAR-DUPLICATE EVIDENCE
# ==================================================

def deduplicate_evidence(
    evidence,
    max_per_source=3
):

    unique = []

    seen_text = set()

    source_counts = {}

    for item in evidence:

        text = item.get(
            "text",
            ""
        ).strip()

        source = item.get(
            "source",
            "Unknown"
        )

        # ------------------------------------------
        # Normalize text
        # ------------------------------------------

        normalized = " ".join(
            text.lower().split()
        )

        # ------------------------------------------
        # Exact duplicate
        # ------------------------------------------

        if normalized in seen_text:
            continue

        # ------------------------------------------
        # Limit same source
        # ------------------------------------------

        count = source_counts.get(
            source,
            0
        )

        if count >= max_per_source:
            continue

        # ------------------------------------------
        # Keep evidence
        # ------------------------------------------

        seen_text.add(
            normalized
        )

        source_counts[source] = count + 1

        unique.append(item)

    return unique


# ==================================================
# BUILD RAG QUERY
# ==================================================

def build_rag_query(
    profile,
    analysis
):

    query_parts = []

    # --------------------------------------------------
    # Soil
    # --------------------------------------------------

    soil = profile.get(
        "soil",
        {}
    )

    if soil.get("ph") is not None:

        query_parts.append(
            f"soil pH {soil['ph']}"
        )

    if soil.get(
        "organic_carbon_percent"
    ) is not None:

        query_parts.append(
            "soil organic carbon "
            f"{soil['organic_carbon_percent']} percent"
        )

    if soil.get(
        "moisture_percent"
    ) is not None:

        query_parts.append(
            "soil moisture "
            f"{soil['moisture_percent']} percent"
        )

    # --------------------------------------------------
    # Climate
    # --------------------------------------------------

    climate = profile.get(
        "climate",
        {}
    )

    if climate.get(
        "rainfall_mm_year"
    ) is not None:

        query_parts.append(
            "annual rainfall "
            f"{climate['rainfall_mm_year']} mm"
        )

    if climate.get(
        "temperature_celsius"
    ) is not None:

        query_parts.append(
            "temperature "
            f"{climate['temperature_celsius']} Celsius"
        )

    # --------------------------------------------------
    # Land
    # --------------------------------------------------

    land = profile.get(
        "land",
        {}
    )

    if land.get("land_use"):

        query_parts.append(
            f"land use {land['land_use']}"
        )

    if land.get("crop_type"):

        query_parts.append(
            f"crop type {land['crop_type']}"
        )

    # --------------------------------------------------
    # Biodiversity
    # --------------------------------------------------

    biodiversity = profile.get(
        "biodiversity",
        {}
    )

    if biodiversity.get(
        "species_richness"
    ):

        query_parts.append(
            "species richness "
            f"{biodiversity['species_richness']}"
        )

    if biodiversity.get(
        "habitat_diversity"
    ):

        query_parts.append(
            "habitat diversity "
            f"{biodiversity['habitat_diversity']}"
        )

    # --------------------------------------------------
    # Human impact
    # --------------------------------------------------

    impact = profile.get(
        "human_impact",
        {}
    )

    if impact.get(
        "pollution_level"
    ):

        query_parts.append(
            "pollution "
            f"{impact['pollution_level']}"
        )

    if impact.get(
        "deforestation_level"
    ):

        query_parts.append(
            "deforestation "
            f"{impact['deforestation_level']}"
        )

    if impact.get(
        "habitat_fragmentation"
    ):

        query_parts.append(
            "habitat fragmentation "
            f"{impact['habitat_fragmentation']}"
        )

    # --------------------------------------------------
    # Reasoning findings
    # --------------------------------------------------

    findings = analysis.get(
        "findings",
        []
    )

    for finding in findings:

        if isinstance(
            finding,
            dict
        ):

            factor = finding.get(
                "factor"
            )

            if factor:

                query_parts.append(
                    str(factor)
                )

    # --------------------------------------------------
    # Interactions
    # --------------------------------------------------

    interactions = analysis.get(
        "interactions",
        []
    )

    for interaction in interactions:

        if isinstance(
            interaction,
            dict
        ):

            description = (
                interaction.get(
                    "interaction"
                )
                or
                interaction.get(
                    "description"
                )
            )

            if description:

                query_parts.append(
                    str(description)
                )

    # --------------------------------------------------
    # Scientific concepts
    # --------------------------------------------------

    query_parts.extend(
        [
            "soil biodiversity",
            "ecosystem health",
            "biodiversity conservation",
            "sustainable land management",
            "ecosystem services"
        ]
    )

    return " ".join(
        query_parts
    )


# ==================================================
# MAIN ENVIRONMENTAL RAG
# ==================================================

def run_environmental_rag(
    profile,
    top_k=TOP_K
):

    print(
        "\n======================================"
    )

    print(
        "ENVIRONMENTAL RAG"
    )

    print(
        "======================================"
    )

    # --------------------------------------------------
    # 1. Reasoning
    # --------------------------------------------------

    print(
        "\nRunning environmental reasoning..."
    )

    analysis = analyze_environment(
        profile
    )

    print(
        "Environmental reasoning completed."
    )

    # --------------------------------------------------
    # 2. Build query
    # --------------------------------------------------

    rag_query = build_rag_query(
        profile,
        analysis
    )

    print(
        "\nRAG Query:"
    )

    print(
        rag_query
    )

    # --------------------------------------------------
    # 3. Retrieve
    # --------------------------------------------------

    print(
        f"\nRetrieving top {top_k} "
        "scientific evidence chunks..."
    )

    raw_evidence = retrieve_evidence(
        rag_query,
        top_k=top_k
    )

    print(
        f"Raw evidence retrieved: "
        f"{len(raw_evidence)}"
    )

    # --------------------------------------------------
    # 4. Deduplicate
    # --------------------------------------------------

    evidence = deduplicate_evidence(
        raw_evidence,
        max_per_source=3
    )

    print(
        f"Evidence after deduplication: "
        f"{len(evidence)}"
    )

    # --------------------------------------------------
    # 5. Print evidence
    # --------------------------------------------------

    print(
        "\n========== SCIENTIFIC EVIDENCE =========="
    )

    for i, item in enumerate(
        evidence,
        start=1
    ):

        print(
            f"\nEvidence {i}"
        )

        print(
            f"Source: {item['source']}"
        )

        print(
            f"Category: {item['category']}"
        )

        print(
            f"Page: {item['page']}"
        )

        print(
            f"Distance: {item['distance']}"
        )

        print(
            f"Text: {item['text'][:300]}..."
        )

    # --------------------------------------------------
    # 6. Return
    # --------------------------------------------------

    return {
        "analysis": analysis,
        "evidence": evidence,
        "rag_query": rag_query
    }


# ==================================================
# TEST
# ==================================================

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
        test_profile
    )

    print(
        "\n======================================"
    )

    print(
        "RAG TEST COMPLETE"
    )

    print(
        "======================================"
    )