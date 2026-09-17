# backend/validation.py

# --------------------------------------------------
# Validation helpers
# --------------------------------------------------

def validate_range(
    value,
    minimum,
    maximum,
    field_name,
    errors
):
    """
    Validate a numeric value against a range.
    """

    if value is None:
        return

    if value < minimum or value > maximum:

        errors.append(
            f"{field_name} must be between "
            f"{minimum} and {maximum}."
        )


# --------------------------------------------------
# Validate environmental profile
# --------------------------------------------------

def validate_environment(profile):

    errors = []

    warnings = []

    # ==================================================
    # SOIL
    # ==================================================

    soil = profile.get(
        "soil",
        {}
    )

    ph = soil.get("ph")

    validate_range(
        ph,
        0,
        14,
        "soil.ph",
        errors
    )

    organic_carbon = soil.get(
        "organic_carbon_percent"
    )

    validate_range(
        organic_carbon,
        0,
        100,
        "soil.organic_carbon_percent",
        errors
    )

    moisture = soil.get(
        "moisture_percent"
    )

    validate_range(
        moisture,
        0,
        100,
        "soil.moisture_percent",
        errors
    )

    # ==================================================
    # CLIMATE
    # ==================================================

    climate = profile.get(
        "climate",
        {}
    )

    rainfall = climate.get(
        "rainfall_mm_year"
    )

    validate_range(
        rainfall,
        0,
        20000,
        "climate.rainfall_mm_year",
        errors
    )

    temperature = climate.get(
        "temperature_celsius"
    )

    validate_range(
        temperature,
        -100,
        70,
        "climate.temperature_celsius",
        errors
    )

    # ==================================================
    # BIODIVERSITY
    # ==================================================

    biodiversity = profile.get(
        "biodiversity",
        {}
    )

    allowed_levels = {
        "low",
        "moderate",
        "medium",
        "high"
    }

    species_richness = biodiversity.get(
        "species_richness"
    )

    if (
        species_richness is not None
        and species_richness.lower()
        not in allowed_levels
    ):

        warnings.append(
            "biodiversity.species_richness "
            "should normally be low, moderate, "
            "medium or high."
        )

    habitat_diversity = biodiversity.get(
        "habitat_diversity"
    )

    if (
        habitat_diversity is not None
        and habitat_diversity.lower()
        not in allowed_levels
    ):

        warnings.append(
            "biodiversity.habitat_diversity "
            "should normally be low, moderate, "
            "medium or high."
        )

    # ==================================================
    # HUMAN IMPACT
    # ==================================================

    impact = profile.get(
        "human_impact",
        {}
    )

    for field in [
        "pollution_level",
        "deforestation_level",
        "habitat_fragmentation"
    ]:

        value = impact.get(field)

        if (
            value is not None
            and value.lower()
            not in allowed_levels
        ):

            warnings.append(
                f"human_impact.{field} "
                "should normally be low, moderate, "
                "medium or high."
            )

    # ==================================================
    # LOCATION
    # ==================================================

    location = profile.get(
        "location",
        {}
    )

    latitude = location.get(
        "latitude"
    )

    validate_range(
        latitude,
        -90,
        90,
        "location.latitude",
        errors
    )

    longitude = location.get(
        "longitude"
    )

    validate_range(
        longitude,
        -180,
        180,
        "location.longitude",
        errors
    )

    # ==================================================
    # DATA COMPLETENESS
    # ==================================================

    total_fields = 0
    missing_fields = 0

    sections = [
        "soil",
        "climate",
        "land",
        "biodiversity",
        "human_impact",
        "location"
    ]

    for section in sections:

        section_data = profile.get(
            section,
            {}
        )

        for value in section_data.values():

            total_fields += 1

            if value is None:
                missing_fields += 1

    if total_fields > 0:

        completeness = (
            (total_fields - missing_fields)
            / total_fields
        ) * 100

    else:

        completeness = 0

    # --------------------------------------------------
    # Missing data warning
    # --------------------------------------------------

    if completeness < 50:

        warnings.append(
            "Environmental profile contains "
            "substantial missing data. "
            "Recommendations may have lower confidence."
        )

    # ==================================================
    # RESULT
    # ==================================================

    return {
        "valid": len(errors) == 0,

        "errors": errors,

        "warnings": warnings,

        "completeness_percent": round(
            completeness,
            2
        )
    }