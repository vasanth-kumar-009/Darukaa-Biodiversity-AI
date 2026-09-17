import requests


# ============================================================
# GBIF CONFIGURATION
# ============================================================

GBIF_API_URL = "https://api.gbif.org/v1/occurrence/search"

DEFAULT_RADIUS_KM = 25
DEFAULT_LIMIT = 100


# ============================================================
# APPROXIMATE KM -> LAT/LONG
# ============================================================

def create_bounding_box(latitude, longitude, radius_km):
    """
    Create an approximate geographic bounding box around
    the requested latitude/longitude.

    1 degree latitude ~= 111 km
    Longitude distance varies with latitude.
    """

    lat_delta = radius_km / 111.0

    # Prevent division problems near the poles
    import math

    cos_lat = math.cos(math.radians(latitude))

    if abs(cos_lat) < 0.01:
        cos_lat = 0.01

    lon_delta = radius_km / (111.0 * cos_lat)

    min_lat = max(-90, latitude - lat_delta)
    max_lat = min(90, latitude + lat_delta)

    min_lon = max(-180, longitude - lon_delta)
    max_lon = min(180, longitude + lon_delta)

    return {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    }


# ============================================================
# GET NEARBY GBIF OCCURRENCES
# ============================================================

def get_nearby_occurrences(
    latitude,
    longitude,
    radius_km=DEFAULT_RADIUS_KM,
    limit=DEFAULT_LIMIT
):
    """
    Retrieve biodiversity occurrence records from GBIF
    around a geographic location.

    NOTE:
    GBIF occurrence records represent recorded observations.
    observed_taxa_count is NOT equivalent to true species richness.
    """

    # --------------------------------------------------------
    # Missing coordinates
    # --------------------------------------------------------

    if latitude is None or longitude is None:

        return {
            "available": False,
            "source": "GBIF Occurrence Search API",
            "error": "Latitude and longitude are required.",
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km,
            "record_count": 0,
            "returned_records": 0,
            "observed_taxa_count": 0,
            "observed_taxa": [],
            "occurrences": []
        }

    # --------------------------------------------------------
    # Convert values
    # --------------------------------------------------------

    try:

        latitude = float(latitude)
        longitude = float(longitude)
        radius_km = float(radius_km)
        limit = int(limit)

    except (ValueError, TypeError):

        return {
            "available": False,
            "source": "GBIF Occurrence Search API",
            "error": "Invalid latitude, longitude, radius, or limit.",
            "record_count": 0,
            "returned_records": 0,
            "observed_taxa_count": 0,
            "observed_taxa": [],
            "occurrences": []
        }

    # --------------------------------------------------------
    # Validate latitude
    # --------------------------------------------------------

    if not -90 <= latitude <= 90:

        return {
            "available": False,
            "source": "GBIF Occurrence Search API",
            "error": "Latitude must be between -90 and 90.",
            "record_count": 0,
            "returned_records": 0,
            "observed_taxa_count": 0,
            "observed_taxa": [],
            "occurrences": []
        }

    # --------------------------------------------------------
    # Validate longitude
    # --------------------------------------------------------

    if not -180 <= longitude <= 180:

        return {
            "available": False,
            "source": "GBIF Occurrence Search API",
            "error": "Longitude must be between -180 and 180.",
            "record_count": 0,
            "returned_records": 0,
            "observed_taxa_count": 0,
            "observed_taxa": [],
            "occurrences": []
        }

    # --------------------------------------------------------
    # Validate radius
    # --------------------------------------------------------

    if radius_km <= 0:
        radius_km = DEFAULT_RADIUS_KM

    # GBIF maximum page size is 300
    limit = max(1, min(limit, 300))

    # --------------------------------------------------------
    # Create bounding box
    # --------------------------------------------------------

    bbox = create_bounding_box(
        latitude,
        longitude,
        radius_km
    )

    # --------------------------------------------------------
    # GBIF API parameters
    #
    # GBIF occurrence search accepts geographic bounding
    # coordinates using decimalLatitude and decimalLongitude.
    # --------------------------------------------------------

    params = {
        "decimalLatitude": (
            f"{bbox['min_lat']},{bbox['max_lat']}"
        ),

        "decimalLongitude": (
            f"{bbox['min_lon']},{bbox['max_lon']}"
        ),

        "hasCoordinate": "true",

        "limit": limit
    }

    # --------------------------------------------------------
    # Print request for debugging
    # --------------------------------------------------------

    print("\nGBIF API REQUEST")
    print("--------------------------------------")
    print("URL:", GBIF_API_URL)
    print("Parameters:", params)

    # --------------------------------------------------------
    # Request GBIF
    # --------------------------------------------------------

    try:

        response = requests.get(
            GBIF_API_URL,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

    # --------------------------------------------------------
    # Timeout
    # --------------------------------------------------------

    except requests.exceptions.Timeout:

        return {
            "available": False,
            "source": "GBIF Occurrence Search API",
            "error": "GBIF API request timed out.",
            "record_count": 0,
            "returned_records": 0,
            "observed_taxa_count": 0,
            "observed_taxa": [],
            "occurrences": []
        }

    # --------------------------------------------------------
    # Connection error
    # --------------------------------------------------------

    except requests.exceptions.ConnectionError:

        return {
            "available": False,
            "source": "GBIF Occurrence Search API",
            "error": (
                "Could not connect to GBIF API. "
                "Check your internet connection."
            ),
            "record_count": 0,
            "returned_records": 0,
            "observed_taxa_count": 0,
            "observed_taxa": [],
            "occurrences": []
        }

    # --------------------------------------------------------
    # HTTP error
    # --------------------------------------------------------

    except requests.exceptions.HTTPError as e:

        error_text = ""

        try:
            error_text = response.text[:1000]
        except Exception:
            pass

        return {
            "available": False,
            "source": "GBIF Occurrence Search API",
            "error": f"GBIF API HTTP error: {e}",
            "api_response": error_text,
            "record_count": 0,
            "returned_records": 0,
            "observed_taxa_count": 0,
            "observed_taxa": [],
            "occurrences": []
        }

    # --------------------------------------------------------
    # Other request error
    # --------------------------------------------------------

    except requests.exceptions.RequestException as e:

        return {
            "available": False,
            "source": "GBIF Occurrence Search API",
            "error": f"GBIF API request failed: {e}",
            "record_count": 0,
            "returned_records": 0,
            "observed_taxa_count": 0,
            "observed_taxa": [],
            "occurrences": []
        }

    # --------------------------------------------------------
    # Invalid JSON
    # --------------------------------------------------------

    except ValueError:

        return {
            "available": False,
            "source": "GBIF Occurrence Search API",
            "error": "GBIF returned invalid JSON data.",
            "record_count": 0,
            "returned_records": 0,
            "observed_taxa_count": 0,
            "observed_taxa": [],
            "occurrences": []
        }

    # ========================================================
    # PROCESS GBIF RESULTS
    # ========================================================

    records = data.get("results", [])

    observed_taxa = set()

    occurrences = []

    # --------------------------------------------------------
    # Process every record
    # --------------------------------------------------------

    for record in records:

        scientific_name = record.get(
            "scientificName"
        )

        if scientific_name:

            observed_taxa.add(
                scientific_name
            )

        occurrence = {

            "gbif_id": record.get("key"),

            "scientific_name": scientific_name,

            "kingdom": record.get("kingdom"),

            "phylum": record.get("phylum"),

            "class": record.get("class"),

            "order": record.get("order"),

            "family": record.get("family"),

            "genus": record.get("genus"),

            "species": record.get("species"),

            "basis_of_record": record.get(
                "basisOfRecord"
            ),

            "event_date": record.get(
                "eventDate"
            ),

            "latitude": record.get(
                "decimalLatitude"
            ),

            "longitude": record.get(
                "decimalLongitude"
            ),

            "coordinate_uncertainty_meters": record.get(
                "coordinateUncertaintyInMeters"
            ),

            "country": record.get(
                "country"
            ),

            "state_province": record.get(
                "stateProvince"
            ),

            "locality": record.get(
                "locality"
            )
        }

        occurrences.append(
            occurrence
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    result = {

        "available": True,

        "source": (
            "GBIF Occurrence Search API"
        ),

        "latitude": latitude,

        "longitude": longitude,

        "radius_km": radius_km,

        "bounding_box": bbox,

        "record_count": data.get(
            "count",
            len(records)
        ),

        "returned_records": len(
            records
        ),

        # This is observed taxa from GBIF,
        # NOT actual ecological species richness.
        "observed_taxa_count": len(
            observed_taxa
        ),

        "observed_taxa": sorted(
            observed_taxa
        )[:100],

        "occurrences": occurrences
    }

    return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n======================================")
    print("GBIF BIODIVERSITY TEST")
    print("======================================")

    # Example:
    # Ludhiana, Punjab

    latitude = 30.9010
    longitude = 75.8573

    print(
        f"\nLatitude: {latitude}"
    )

    print(
        f"Longitude: {longitude}"
    )

    print(
        f"Radius: {DEFAULT_RADIUS_KM} km"
    )

    # --------------------------------------------------------
    # Call GBIF
    # --------------------------------------------------------

    result = get_nearby_occurrences(
        latitude=latitude,
        longitude=longitude
    )

    # --------------------------------------------------------
    # Display result
    # --------------------------------------------------------

    print("\n--------------------------------------")
    print("RESULT")
    print("--------------------------------------")

    print(
        "Available:",
        result.get(
            "available",
            False
        )
    )

    print(
        "Records:",
        result.get(
            "record_count",
            0
        )
    )

    print(
        "Returned records:",
        result.get(
            "returned_records",
            0
        )
    )

    print(
        "Observed taxa:",
        result.get(
            "observed_taxa_count",
            0
        )
    )

    # --------------------------------------------------------
    # Error
    # --------------------------------------------------------

    if not result.get(
        "available",
        False
    ):

        print("\nGBIF ERROR:")

        print(
            result.get(
                "error",
                "Unknown error"
            )
        )

        if result.get(
            "api_response"
        ):

            print(
                "\nGBIF API RESPONSE:"
            )

            print(
                result.get(
                    "api_response"
                )
            )

    # --------------------------------------------------------
    # Successful response
    # --------------------------------------------------------

    else:

        print(
            "\nObserved scientific names:"
        )

        observed_taxa = result.get(
            "observed_taxa",
            []
        )

        if observed_taxa:

            for name in observed_taxa[:20]:

                print(
                    "-",
                    name
                )

        else:

            print(
                "No scientific names were "
                "returned."
            )

    print(
        "\n======================================"
    )

    print(
        "TEST COMPLETE"
    )

    print(
        "======================================"
    )