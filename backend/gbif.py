import requests
import math


# ============================================================
# CONFIGURATION
# ============================================================

GBIF_API_URL = (
    "https://api.gbif.org/v1/occurrence/search"
)

DEFAULT_RADIUS_KM = 25

DEFAULT_LIMIT = 20

REQUEST_TIMEOUT_SECONDS = 8


# ============================================================
# CREATE BOUNDING BOX
# ============================================================


def create_bounding_box(
    latitude,
    longitude,
    radius_km
):

    lat_delta = radius_km / 111.0

    cos_lat = math.cos(
        math.radians(latitude)
    )

    if abs(cos_lat) < 0.01:

        cos_lat = 0.01

    lon_delta = radius_km / (
        111.0 * cos_lat
    )

    return {

        "min_lat":
            max(
                -90,
                latitude - lat_delta
            ),

        "max_lat":
            min(
                90,
                latitude + lat_delta
            ),

        "min_lon":
            max(
                -180,
                longitude - lon_delta
            ),

        "max_lon":
            min(
                180,
                longitude + lon_delta
            )
    }


# ============================================================
# STANDARD ERROR RESPONSE
# ============================================================


def gbif_error(
    message,
    latitude=None,
    longitude=None,
    radius_km=DEFAULT_RADIUS_KM
):

    return {

        "available": False,

        "source":
            "GBIF Occurrence Search API",

        "error":
            message,

        "latitude":
            latitude,

        "longitude":
            longitude,

        "radius_km":
            radius_km,

        "record_count": 0,

        "returned_records": 0,

        "observed_taxa_count": 0,

        "observed_taxa": [],

        "occurrences": []
    }


# ============================================================
# GET NEARBY OCCURRENCES
# ============================================================


def get_nearby_occurrences(
    latitude,
    longitude,
    radius_km=DEFAULT_RADIUS_KM,
    limit=DEFAULT_LIMIT
):

    if latitude is None or longitude is None:

        return gbif_error(
            "Latitude and longitude are required.",
            latitude,
            longitude,
            radius_km
        )

    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )

        radius_km = float(
            radius_km
        )

        limit = int(
            limit
        )

    except (
        ValueError,
        TypeError
    ):

        return gbif_error(
            "Invalid geographic parameters.",
            latitude,
            longitude,
            radius_km
        )

    if not -90 <= latitude <= 90:

        return gbif_error(
            "Latitude must be between -90 and 90.",
            latitude,
            longitude,
            radius_km
        )

    if not -180 <= longitude <= 180:

        return gbif_error(
            "Longitude must be between -180 and 180.",
            latitude,
            longitude,
            radius_km
        )

    if radius_km <= 0:

        radius_km = DEFAULT_RADIUS_KM

    # Keep interactive requests small.
    limit = max(
        1,
        min(
            limit,
            50
        )
    )

    bbox = create_bounding_box(
        latitude,
        longitude,
        radius_km
    )

    params = {

        "decimalLatitude":
            (
                f"{bbox['min_lat']},"
                f"{bbox['max_lat']}"
            ),

        "decimalLongitude":
            (
                f"{bbox['min_lon']},"
                f"{bbox['max_lon']}"
            ),

        "hasCoordinate":
            "true",

        "limit":
            limit
    }

    print(
        "\nGBIF request started..."
    )

    try:

        response = requests.get(

            GBIF_API_URL,

            params=params,

            timeout=REQUEST_TIMEOUT_SECONDS
        )

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.Timeout:

        return gbif_error(
            "GBIF request timed out.",
            latitude,
            longitude,
            radius_km
        )

    except requests.exceptions.ConnectionError:

        return gbif_error(
            "Could not connect to GBIF.",
            latitude,
            longitude,
            radius_km
        )

    except requests.exceptions.HTTPError as exc:

        return gbif_error(
            f"GBIF HTTP error: {exc}",
            latitude,
            longitude,
            radius_km
        )

    except ValueError:

        return gbif_error(
            "GBIF returned invalid JSON.",
            latitude,
            longitude,
            radius_km
        )

    except requests.exceptions.RequestException as exc:

        return gbif_error(
            f"GBIF request failed: {exc}",
            latitude,
            longitude,
            radius_km
        )

    records = data.get(
        "results",
        []
    )

    observed_taxa = set()

    occurrences = []

    for record in records:

        scientific_name = record.get(
            "scientificName"
        )

        if scientific_name:

            observed_taxa.add(
                scientific_name
            )

        # Only retain fields needed by the UI.
        occurrence = {

            "gbif_id":
                record.get("key"),

            "scientific_name":
                scientific_name,

            "basis_of_record":
                record.get(
                    "basisOfRecord"
                ),

            "event_date":
                record.get(
                    "eventDate"
                ),

            "latitude":
                record.get(
                    "decimalLatitude"
                ),

            "longitude":
                record.get(
                    "decimalLongitude"
                ),

            "country":
                record.get(
                    "country"
                ),

            "state_province":
                record.get(
                    "stateProvince"
                )
        }

        occurrences.append(
            occurrence
        )

    result = {

        "available": True,

        "source":
            "GBIF Occurrence Search API",

        "latitude":
            latitude,

        "longitude":
            longitude,

        "radius_km":
            radius_km,

        "bounding_box":
            bbox,

        "record_count":
            data.get(
                "count",
                len(records)
            ),

        "returned_records":
            len(records),

        "observed_taxa_count":
            len(observed_taxa),

        "observed_taxa":
            sorted(
                observed_taxa
            )[:30],

        # Keep only a small sample.
        "occurrences":
            occurrences[:10],

        "sample_note":
            (
                "GBIF occurrence data represents "
                "available observations and does not "
                "constitute a complete species inventory."
            )
    }

    print(
        "GBIF complete:",
        result["record_count"],
        "matching records,"
        ,
        result["observed_taxa_count"],
        "observed taxa."
    )

    return result


# ============================================================
# TEST
# ============================================================


if __name__ == "__main__":

    result = get_nearby_occurrences(

        latitude=30.9010,

        longitude=75.8573
    )

    print()

    print(
        "Available:",
        result.get(
            "available"
        )
    )

    print(
        "Records:",
        result.get(
            "record_count"
        )
    )

    print(
        "Returned:",
        result.get(
            "returned_records"
        )
    )

    print(
        "Observed taxa:",
        result.get(
            "observed_taxa_count"
        )
    )