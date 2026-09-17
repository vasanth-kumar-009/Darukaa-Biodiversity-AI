import json
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

DATASET_FILE = DATA_DIR / "environmental_dataset.json"

METADATA_FILE = DATA_DIR / "knowledge_metadata.json"


# ============================================================
# LOAD JSON
# ============================================================

def load_json(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# LOAD ENVIRONMENTAL DATASET
# ============================================================

def load_environmental_dataset():

    if not DATASET_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found: {DATASET_FILE}"
        )

    return load_json(
        DATASET_FILE
    )


# ============================================================
# LOAD KNOWLEDGE METADATA
# ============================================================

def load_knowledge_metadata():

    if not METADATA_FILE.exists():

        raise FileNotFoundError(
            f"Knowledge metadata not found: {METADATA_FILE}"
        )

    return load_json(
        METADATA_FILE
    )


# ============================================================
# FIND SITE
# ============================================================

def get_site_by_id(
    site_id
):

    dataset = load_environmental_dataset()

    for site in dataset:

        if site.get("id") == site_id:

            return site

    return None


# ============================================================
# FIND SITES BY REGION
# ============================================================

def get_sites_by_region(
    region
):

    dataset = load_environmental_dataset()

    region_lower = region.lower()

    return [
        site
        for site in dataset
        if site.get(
            "region",
            ""
        ).lower() == region_lower
    ]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n======================================")
    print("STRUCTURED DATA LAYER TEST")
    print("======================================")

    dataset = load_environmental_dataset()

    print(
        "\nEnvironmental records:",
        len(dataset)
    )

    for site in dataset:

        print(
            f"- {site['id']}: "
            f"{site['region']}"
        )

    metadata = load_knowledge_metadata()

    print(
        "\nKnowledge base:",
        metadata["knowledge_base"]["name"]
    )

    print(
        "Scientific sources:",
        len(metadata["sources"])
    )

    print(
        "Structured variables:",
        len(
            metadata["structured_variables"]
        )
    )

    print("\n======================================")
    print("TEST COMPLETE")
    print("======================================")