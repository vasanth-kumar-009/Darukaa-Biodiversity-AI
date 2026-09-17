# backend/knowledge_layer.py

import json
from pathlib import Path


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "environmental_dataset.json"
)


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():
    """
    Load the structured environmental dataset.
    """

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"Environmental dataset not found: {DATA_FILE}"
        )

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# GET ALL SITES
# ============================================================

def get_all_sites():
    """
    Return all environmental sites.
    """

    return load_dataset()


# ============================================================
# GET SITE BY ID
# ============================================================

def get_site_by_id(site_id):
    """
    Find a specific environmental site.
    """

    dataset = load_dataset()

    for site in dataset:

        if site.get("id") == site_id:

            return site

    return None


# ============================================================
# GET SITES BY REGION
# ============================================================

def get_sites_by_region(region):
    """
    Find environmental sites belonging to a region.
    """

    if not region:
        return []

    dataset = load_dataset()

    region = region.strip().lower()

    results = []

    for site in dataset:

        site_region = site.get(
            "region",
            ""
        ).strip().lower()

        if site_region == region:

            results.append(site)

    return results


# ============================================================
# GET SITES BY ENVIRONMENTAL CONDITION
# ============================================================

def get_sites_by_condition(
    variable,
    value
):
    """
    Search environmental sites based on
    a nested environmental variable.

    Example:

    variable =
        "soil.organic_carbon_percent"

    value =
        0.3
    """

    if not variable:

        return []

    dataset = load_dataset()

    parts = variable.split(".")

    results = []

    for site in dataset:

        current = site

        try:

            for part in parts:

                current = current[part]

            # ------------------------------------------------
            # Numeric comparison
            # ------------------------------------------------

            if isinstance(
                current,
                (int, float)
            ):

                try:

                    if float(current) == float(value):

                        results.append(site)

                except (
                    ValueError,
                    TypeError
                ):

                    continue

            # ------------------------------------------------
            # String comparison
            # ------------------------------------------------

            else:

                if str(current).lower() == str(
                    value
                ).lower():

                    results.append(site)

        except (
            KeyError,
            TypeError
        ):

            continue

    return results


# ============================================================
# GET SITES BY BIODIVERSITY CONDITION
# ============================================================

def get_sites_by_biodiversity(
    species_richness=None,
    habitat_diversity=None
):
    """
    Find sites using biodiversity indicators.
    """

    dataset = load_dataset()

    results = []

    for site in dataset:

        biodiversity = site.get(
            "biodiversity",
            {}
        )

        match = True

        # ----------------------------------------------------
        # Species richness
        # ----------------------------------------------------

        if species_richness is not None:

            if str(
                biodiversity.get(
                    "species_richness",
                    ""
                )
            ).lower() != str(
                species_richness
            ).lower():

                match = False

        # ----------------------------------------------------
        # Habitat diversity
        # ----------------------------------------------------

        if habitat_diversity is not None:

            if str(
                biodiversity.get(
                    "habitat_diversity",
                    ""
                )
            ).lower() != str(
                habitat_diversity
            ).lower():

                match = False

        if match:

            results.append(site)

    return results


# ============================================================
# SEARCH ENVIRONMENTAL KNOWLEDGE
# ============================================================

def search_environmental_knowledge(
    region=None,
    species_richness=None,
    habitat_diversity=None,
    land_use=None,
    crop_type=None
):
    """
    Search the structured environmental knowledge base
    using multiple conditions.

    This is the main knowledge-layer search function.
    """

    dataset = load_dataset()

    results = []

    for site in dataset:

        match = True

        # ----------------------------------------------------
        # Region
        # ----------------------------------------------------

        if region is not None:

            if str(
                site.get(
                    "region",
                    ""
                )
            ).lower() != str(
                region
            ).lower():

                match = False

        # ----------------------------------------------------
        # Biodiversity
        # ----------------------------------------------------

        biodiversity = site.get(
            "biodiversity",
            {}
        )

        if species_richness is not None:

            if str(
                biodiversity.get(
                    "species_richness",
                    ""
                )
            ).lower() != str(
                species_richness
            ).lower():

                match = False

        if habitat_diversity is not None:

            if str(
                biodiversity.get(
                    "habitat_diversity",
                    ""
                )
            ).lower() != str(
                habitat_diversity
            ).lower():

                match = False

        # ----------------------------------------------------
        # Land
        # ----------------------------------------------------

        land = site.get(
            "land",
            {}
        )

        if land_use is not None:

            if str(
                land.get(
                    "land_use",
                    ""
                )
            ).lower() != str(
                land_use
            ).lower():

                match = False

        if crop_type is not None:

            if str(
                land.get(
                    "crop_type",
                    ""
                )
            ).lower() != str(
                crop_type
            ).lower():

                match = False

        # ----------------------------------------------------
        # Add matching site
        # ----------------------------------------------------

        if match:

            results.append(site)

    return results


# ============================================================
# FIND SIMILAR ENVIRONMENT
# ============================================================

def find_similar_environment(
    profile
):
    """
    Find structured dataset records that have similar
    environmental characteristics to the supplied profile.

    This is useful for contextual reasoning.
    """

    dataset = load_dataset()

    if not profile:

        return []

    results = []

    profile_land = profile.get(
        "land",
        {}
    )

    profile_biodiversity = profile.get(
        "biodiversity",
        {}
    )

    profile_climate = profile.get(
        "climate",
        {}
    )

    for site in dataset:

        score = 0

        site_land = site.get(
            "land",
            {}
        )

        site_biodiversity = site.get(
            "biodiversity",
            {}
        )

        site_climate = site.get(
            "climate",
            {}
        )

        # ----------------------------------------------------
        # Land use
        # ----------------------------------------------------

        if (
            profile_land.get("land_use")
            and
            profile_land.get("land_use")
            == site_land.get("land_use")
        ):

            score += 2

        # ----------------------------------------------------
        # Crop type
        # ----------------------------------------------------

        if (
            profile_land.get("crop_type")
            and
            profile_land.get("crop_type")
            == site_land.get("crop_type")
        ):

            score += 2

        # ----------------------------------------------------
        # Species richness
        # ----------------------------------------------------

        if (
            profile_biodiversity.get(
                "species_richness"
            )
            and
            profile_biodiversity.get(
                "species_richness"
            )
            ==
            site_biodiversity.get(
                "species_richness"
            )
        ):

            score += 2

        # ----------------------------------------------------
        # Habitat diversity
        # ----------------------------------------------------

        if (
            profile_biodiversity.get(
                "habitat_diversity"
            )
            and
            profile_biodiversity.get(
                "habitat_diversity"
            )
            ==
            site_biodiversity.get(
                "habitat_diversity"
            )
        ):

            score += 2

        # ----------------------------------------------------
        # Rainfall similarity
        # ----------------------------------------------------

        profile_rainfall = profile_climate.get(
            "rainfall_mm_year"
        )

        site_rainfall = site_climate.get(
            "rainfall_mm_year"
        )

        if (
            profile_rainfall is not None
            and site_rainfall is not None
        ):

            difference = abs(
                float(profile_rainfall)
                -
                float(site_rainfall)
            )

            if difference <= 200:

                score += 2

        # ----------------------------------------------------
        # Keep sites with similarity
        # ----------------------------------------------------

        if score > 0:

            results.append(
                {
                    "site": site,
                    "similarity_score": score
                }
            )

    # --------------------------------------------------------
    # Highest similarity first
    # --------------------------------------------------------

    results.sort(
        key=lambda x: x[
            "similarity_score"
        ],
        reverse=True
    )

    return results


# ============================================================
# CREATE KNOWLEDGE CONTEXT
# ============================================================

def build_knowledge_context(
    profile
):
    """
    Create a structured context object that can be
    supplied to the reasoning engine / RAG / Gemini.
    """

    location = profile.get(
        "location",
        {}
    )

    region = location.get(
        "region"
    )

    biodiversity = profile.get(
        "biodiversity",
        {}
    )

    land = profile.get(
        "land",
        {}
    )

    context = {

        "dataset_source": str(
            DATA_FILE
        ),

        "matching_region_sites":
            get_sites_by_region(
                region
            )
            if region
            else [],

        "matching_biodiversity_sites":
            get_sites_by_biodiversity(
                species_richness=biodiversity.get(
                    "species_richness"
                ),
                habitat_diversity=biodiversity.get(
                    "habitat_diversity"
                )
            ),

        "matching_land_sites":
            search_environmental_knowledge(
                land_use=land.get(
                    "land_use"
                ),
                crop_type=land.get(
                    "crop_type"
                )
            ),

        "similar_environments":
            find_similar_environment(
                profile
            )[:5]
    }

    return context


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n======================================")
    print("KNOWLEDGE LAYER TEST")
    print("======================================")

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    dataset = load_dataset()

    print(
        "\nTotal sites:",
        len(dataset)
    )

    # --------------------------------------------------------
    # Site ID search
    # --------------------------------------------------------

    print(
        "\nSITE ID SEARCH"
    )

    site = get_site_by_id(
        "site_001"
    )

    if site:

        print(
            "Found:",
            site["id"],
            "-",
            site["region"]
        )

    # --------------------------------------------------------
    # Region search
    # --------------------------------------------------------

    print(
        "\nREGION SEARCH"
    )

    punjab_sites = get_sites_by_region(
        "Punjab"
    )

    print(
        "Punjab sites:",
        len(punjab_sites)
    )

    # --------------------------------------------------------
    # Biodiversity search
    # --------------------------------------------------------

    print(
        "\nBIODIVERSITY SEARCH"
    )

    low_biodiversity = (
        get_sites_by_biodiversity(
            species_richness="low"
        )
    )

    print(
        "Low species richness sites:",
        len(low_biodiversity)
    )

    # --------------------------------------------------------
    # Environmental condition search
    # --------------------------------------------------------

    print(
        "\nENVIRONMENTAL CONDITION SEARCH"
    )

    low_carbon_sites = (
        get_sites_by_condition(
            "soil.organic_carbon_percent",
            0.3
        )
    )

    print(
        "Sites with organic carbon = 0.3%:",
        len(low_carbon_sites)
    )

    # --------------------------------------------------------
    # Combined search
    # --------------------------------------------------------

    print(
        "\nCOMBINED SEARCH"
    )

    combined = search_environmental_knowledge(
        region="Punjab",
        species_richness="low",
        habitat_diversity="low",
        land_use="cropland"
    )

    print(
        "Matching sites:",
        len(combined)
    )

    for site in combined:

        print(
            "-",
            site["id"],
            site["region"]
        )

    # --------------------------------------------------------
    # Similar environment
    # --------------------------------------------------------

    print(
        "\nSIMILAR ENVIRONMENT SEARCH"
    )

    test_profile = {

        "climate": {
            "rainfall_mm_year": 450
        },

        "land": {
            "land_use": "cropland",
            "crop_type": "wheat_monoculture"
        },

        "biodiversity": {
            "species_richness": "low",
            "habitat_diversity": "low"
        },

        "location": {
            "region": "Punjab"
        }
    }

    similar = find_similar_environment(
        test_profile
    )

    for item in similar:

        site = item["site"]

        print(
            "-",
            site["id"],
            "| score:",
            item["similarity_score"]
        )

    # --------------------------------------------------------
    # Knowledge context
    # --------------------------------------------------------

    print(
        "\nKNOWLEDGE CONTEXT"
    )

    context = build_knowledge_context(
        test_profile
    )

    print(
        "Region matches:",
        len(
            context[
                "matching_region_sites"
            ]
        )
    )

    print(
        "Biodiversity matches:",
        len(
            context[
                "matching_biodiversity_sites"
            ]
        )
    )

    print(
        "Similar environments:",
        len(
            context[
                "similar_environments"
            ]
        )
    )

    print("\n======================================")
    print("KNOWLEDGE LAYER TEST COMPLETE")
    print("======================================")