# ============================================================
# DARUKAA BIODIVERSITY AI
# Environmental Reasoning Engine
# ============================================================


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_low(value):
    """
    Check whether a value is described as low.
    """

    if value is None:
        return False

    if isinstance(value, str):
        return value.lower() in [
            "low",
            "very low",
            "poor"
        ]

    return False


def is_high(value):
    """
    Check whether a value is described as high.
    """

    if value is None:
        return False

    if isinstance(value, str):
        return value.lower() in [
            "high",
            "very high",
            "severe"
        ]

    return False


# ============================================================
# MAIN REASONING FUNCTION
# ============================================================

def analyze_environment(profile):

    findings = []

    interactions = []

    recommendations = []

    metrics = set()


    # --------------------------------------------------------
    # Extract sections
    # --------------------------------------------------------

    soil = profile.get("soil", {})
    climate = profile.get("climate", {})
    land = profile.get("land", {})
    biodiversity = profile.get("biodiversity", {})
    human_impact = profile.get("human_impact", {})


    # ========================================================
    # SOIL ANALYSIS
    # ========================================================

    organic_carbon = soil.get(
        "organic_carbon_percent"
    )

    if organic_carbon is not None:

        if organic_carbon < 0.5:

            findings.append({
                "factor": "Low soil organic carbon",
                "severity": "high",
                "explanation":
                    "The supplied soil organic carbon value "
                    "is very low and indicates potential "
                    "soil-health pressure."
            })

            metrics.add(
                "soil organic carbon"
            )

        elif organic_carbon < 1.0:

            findings.append({
                "factor": "Relatively low soil organic carbon",
                "severity": "medium",
                "explanation":
                    "The supplied soil organic carbon value "
                    "may indicate reduced soil condition."
            })

            metrics.add(
                "soil organic carbon"
            )


    # ========================================================
    # SOIL MOISTURE
    # ========================================================

    moisture = soil.get(
        "moisture_percent"
    )

    if moisture is not None:

        if moisture < 20:

            findings.append({
                "factor": "Low soil moisture",
                "severity": "medium",
                "explanation":
                    "Low soil moisture can create water "
                    "stress for plants and soil organisms."
            })

            metrics.add(
                "soil moisture"
            )


    # ========================================================
    # CLIMATE / RAINFALL
    # ========================================================

    rainfall = climate.get(
        "rainfall_mm_year"
    )

    if rainfall is not None:

        if rainfall < 500:

            findings.append({
                "factor": "Low annual rainfall",
                "severity": "high",
                "explanation":
                    "Low rainfall can increase water "
                    "availability constraints."
            })

            metrics.add(
                "water availability"
            )


    # ========================================================
    # TEMPERATURE
    # ========================================================

    temperature = climate.get(
        "temperature_celsius"
    )

    if temperature is not None:

        if temperature > 35:

            findings.append({
                "factor": "High temperature",
                "severity": "medium",
                "explanation":
                    "High temperatures can increase "
                    "environmental and water stress."
            })

            metrics.add(
                "temperature stress"
            )


    # ========================================================
    # LAND USE
    # ========================================================

    land_use = land.get(
        "land_use"
    )

    crop_type = land.get(
        "crop_type"
    )


    # --------------------------------------------------------
    # Monoculture
    # --------------------------------------------------------

    if crop_type:

        crop_lower = str(
            crop_type
        ).lower()

        if "monoculture" in crop_lower:

            findings.append({
                "factor": "Monoculture cropping",
                "severity": "medium",
                "explanation":
                    "A single-crop system can provide "
                    "less structural and habitat diversity "
                    "than a diversified system."
            })

            metrics.add(
                "habitat diversity"
            )


    # ========================================================
    # BIODIVERSITY
    # ========================================================

    species_richness = biodiversity.get(
        "species_richness"
    )

    habitat_diversity = biodiversity.get(
        "habitat_diversity"
    )


    if is_low(species_richness):

        findings.append({
            "factor": "Low species richness",
            "severity": "high",
            "explanation":
                "Low species richness indicates reduced "
                "observed biodiversity."
        })

        metrics.add(
            "species richness"
        )


    if is_low(habitat_diversity):

        findings.append({
            "factor": "Low habitat diversity",
            "severity": "high",
            "explanation":
                "Low habitat diversity can reduce the "
                "number of ecological niches available."
        })

        metrics.add(
            "habitat diversity"
        )


    # ========================================================
    # HUMAN IMPACT
    # ========================================================

    pollution = human_impact.get(
        "pollution_level"
    )

    deforestation = human_impact.get(
        "deforestation_level"
    )

    fragmentation = human_impact.get(
        "habitat_fragmentation"
    )


    if is_high(pollution):

        findings.append({
            "factor": "High pollution",
            "severity": "high",
            "explanation":
                "High pollution represents potential "
                "pressure on environmental quality."
        })

        metrics.add(
            "pollution"
        )


    if is_high(deforestation):

        findings.append({
            "factor": "High deforestation",
            "severity": "high",
            "explanation":
                "Deforestation can reduce and alter "
                "available natural habitat."
        })

        metrics.add(
            "habitat availability"
        )


    if is_high(fragmentation):

        findings.append({
            "factor": "High habitat fragmentation",
            "severity": "high",
            "explanation":
                "Fragmentation can separate habitat patches "
                "and affect ecological connectivity."
        })

        metrics.add(
            "habitat connectivity"
        )


    # ========================================================
    # MULTI-METRIC INTERACTIONS
    # ========================================================


    # --------------------------------------------------------
    # Soil carbon + rainfall
    # --------------------------------------------------------

    low_carbon = (
        organic_carbon is not None
        and organic_carbon < 0.5
    )

    low_rainfall = (
        rainfall is not None
        and rainfall < 500
    )


    if low_carbon and low_rainfall:

        interactions.append({
            "variables": [
                "soil organic carbon",
                "rainfall"
            ],
            "reasoning":
                "Low soil organic carbon and low rainfall "
                "can occur together with pressure on soil "
                "condition and water availability."
        })

        recommendations.append(
            "Consider soil-cover and soil-organic-matter "
            "management practices appropriate to the local "
            "climate."
        )


    # --------------------------------------------------------
    # Monoculture + low biodiversity
    # --------------------------------------------------------

    monoculture = (
        crop_type is not None
        and "monoculture"
        in str(crop_type).lower()
    )

    low_biodiversity = (
        is_low(species_richness)
        or is_low(habitat_diversity)
    )


    if monoculture and low_biodiversity:

        interactions.append({
            "variables": [
                "monoculture",
                "biodiversity"
            ],
            "reasoning":
                "A monoculture combined with low biodiversity "
                "suggests that increasing habitat and crop "
                "diversity may be relevant."
        })

        recommendations.append(
            "Consider an appropriately designed diversified "
            "cropping system such as intercropping."
        )


    # --------------------------------------------------------
    # Low rainfall + monoculture
    # --------------------------------------------------------

    if low_rainfall and monoculture:

        interactions.append({
            "variables": [
                "rainfall",
                "land use"
            ],
            "reasoning":
                "Low rainfall combined with monoculture "
                "creates both water-availability and "
                "habitat-diversity considerations."
        })

        recommendations.append(
            "Evaluate drought-compatible crop diversification "
            "and habitat-supporting practices."
        )


    # --------------------------------------------------------
    # Soil + biodiversity
    # --------------------------------------------------------

    if low_carbon and low_biodiversity:

        interactions.append({
            "variables": [
                "soil organic carbon",
                "biodiversity"
            ],
            "reasoning":
                "Low soil organic carbon and low biodiversity "
                "indicate that both soil condition and "
                "biological diversity should be considered."
        })

        recommendations.append(
            "Evaluate practices that increase organic inputs "
            "and support soil biological activity."
        )


    # --------------------------------------------------------
    # Fragmentation + biodiversity
    # --------------------------------------------------------

    if is_high(fragmentation) and low_biodiversity:

        interactions.append({
            "variables": [
                "habitat fragmentation",
                "biodiversity"
            ],
            "reasoning":
                "High habitat fragmentation together with "
                "low biodiversity indicates a potential "
                "habitat-connectivity issue."
        })

        recommendations.append(
            "Consider restoring or connecting suitable "
            "habitat patches where locally appropriate."
        )


    # ========================================================
    # OVERALL ASSESSMENT
    # ========================================================

    if len(interactions) >= 3:

        overall = (
            "Multiple environmental variables are interacting "
            "and should be considered together."
        )

    elif len(interactions) >= 1:

        overall = (
            "The supplied environmental conditions show "
            "potential interactions across multiple metrics."
        )

    else:

        overall = (
            "Insufficient interacting conditions were detected "
            "for a multi-metric assessment."
        )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "findings": findings,

        "interactions": interactions,

        "recommendations": recommendations,

        "impacted_metrics": sorted(
            list(metrics)
        ),

        "overall_assessment": overall
    }


# ============================================================
# TEST
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

        }

    }


    result = analyze_environment(
        test_profile
    )


    print()
    print("=" * 70)
    print("ENVIRONMENTAL ANALYSIS")
    print("=" * 70)


    print("\nOVERALL ASSESSMENT:")

    print(
        result["overall_assessment"]
    )


    print("\nFINDINGS:")

    for finding in result["findings"]:

        print(
            f"- {finding['factor']}: "
            f"{finding['explanation']}"
        )


    print("\nINTERACTIONS:")

    for interaction in result["interactions"]:

        print(
            f"- {' + '.join(interaction['variables'])}"
        )

        print(
            f"  {interaction['reasoning']}"
        )


    print("\nRECOMMENDATIONS:")

    for recommendation in result[
        "recommendations"
    ]:

        print(
            f"- {recommendation}"
        )


    print("\nIMPACTED METRICS:")

    for metric in result[
        "impacted_metrics"
    ]:

        print(
            f"- {metric}"
        )