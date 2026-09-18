from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel, Field

from backend.validation import validate_environment
from backend.memory import (
    get_conversation,
    update_environment,
    add_message,
    format_chat_history,
)
from backend.biodiversity_pipeline import run_pipeline


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FRONTEND_DIR = PROJECT_ROOT / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Darukaa.Earth Biodiversity Intelligence API",
    description=(
        "AI-powered biodiversity intelligence system combining "
        "environmental reasoning, scientific RAG, structured "
        "environmental knowledge and biodiversity observations."
    ),
    version="1.0.0",
)


# ============================================================
# STATIC FRONTEND
# ============================================================

if FRONTEND_DIR.exists():

    app.mount(
        "/static",
        StaticFiles(directory=str(FRONTEND_DIR)),
        name="static",
    )


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",

        "http://localhost:8000",
        "http://127.0.0.1:8000",

        "https://darukaa-biodiversity-ai.vercel.app",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# PYDANTIC MODELS
# ============================================================


class Soil(BaseModel):

    ph: float | None = Field(
        default=None,
        ge=0,
        le=14,
    )

    organic_carbon_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    moisture_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class Climate(BaseModel):

    rainfall_mm_year: float | None = Field(
        default=None,
        ge=0,
        le=20000,
    )

    temperature_celsius: float | None = Field(
        default=None,
        ge=-100,
        le=70,
    )


class Land(BaseModel):

    land_use: str | None = None

    crop_type: str | None = None


class Biodiversity(BaseModel):

    species_richness: str | None = None

    habitat_diversity: str | None = None


class HumanImpact(BaseModel):

    pollution_level: str | None = None

    deforestation_level: str | None = None

    habitat_fragmentation: str | None = None


class Location(BaseModel):

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    region: str | None = None


class EnvironmentalProfile(BaseModel):

    soil: Soil = Field(
        default_factory=Soil
    )

    climate: Climate = Field(
        default_factory=Climate
    )

    land: Land = Field(
        default_factory=Land
    )

    biodiversity: Biodiversity = Field(
        default_factory=Biodiversity
    )

    human_impact: HumanImpact = Field(
        default_factory=HumanImpact
    )

    location: Location = Field(
        default_factory=Location
    )


class BiodiversityRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        description="User's biodiversity/environment question",
    )

    environment: EnvironmentalProfile


class ChatRequest(BaseModel):

    session_id: str = Field(
        ...,
        min_length=1,
    )

    question: str = Field(
        ...,
        min_length=1,
    )

    environment: EnvironmentalProfile | None = None


# ============================================================
# HELPERS
# ============================================================


def profile_to_dict(
    profile: EnvironmentalProfile,
) -> dict:

    return profile.model_dump()


def validate_profile(
    profile: dict,
) -> dict:

    try:

        result = validate_environment(
            profile
        )

        return result

    except Exception as exc:

        return {
            "valid": False,
            "errors": [
                f"Validation error: {str(exc)}"
            ],
            "warnings": [],
            "completeness_percent": 0,
        }


# ============================================================
# ROOT / FRONTEND
# ============================================================


@app.get(
    "/",
    include_in_schema=False,
)
async def root():

    """
    Serve the frontend application.

    On Vercel, this allows:
        https://your-domain.vercel.app/

    to directly display frontend/index.html.
    """

    if FRONTEND_INDEX.exists():

        return FileResponse(
            str(FRONTEND_INDEX),
            media_type="text/html",
        )

    return {
        "message": "Darukaa.Earth API is running",
        "status": "online",
        "docs": "/docs",
    }


# ============================================================
# HEALTH
# ============================================================


@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "service": "Darukaa.Earth",
        "version": "1.0.0",
    }


# ============================================================
# INFO
# ============================================================


@app.get("/info")
async def info():

    return {

        "name": "Darukaa.Earth",

        "description": (
            "AI Biodiversity Intelligence System"
        ),

        "components": [

            "Environmental validation",

            "Environmental reasoning",

            "Scientific RAG",

            "Structured environmental knowledge",

            "GBIF biodiversity observations",

            "Gemini AI",

            "Conversational memory",
        ],

        "input_variables": [

            "soil",

            "climate",

            "land",

            "biodiversity",

            "human_impact",

            "location",
        ],

        "location_support": {

            "region": True,

            "latitude": True,

            "longitude": True,

            "gbif_integration": True,
        },
    }


# ============================================================
# ANALYZE
# ============================================================


@app.post("/analyze")
async def analyze(
    request: BiodiversityRequest,
):

    """
    Analyze an environmental profile.

    Flow:

        Input
          ↓
        Validation
          ↓
        Environmental reasoning
          ↓
        Scientific RAG
          ↓
        Structured knowledge
          ↓
        GBIF location biodiversity
          ↓
        Gemini response
    """

    # --------------------------------------------------------
    # Convert Pydantic model to dictionary
    # --------------------------------------------------------

    profile = profile_to_dict(
        request.environment
    )


    # --------------------------------------------------------
    # Validate environment
    # --------------------------------------------------------

    validation = validate_profile(
        profile
    )


    if not validation.get("valid", False):

        raise HTTPException(
            status_code=422,
            detail={
                "message": "Invalid environmental data",
                "errors": validation.get(
                    "errors",
                    [],
                ),
                "warnings": validation.get(
                    "warnings",
                    [],
                ),
                "completeness_percent":
                    validation.get(
                        "completeness_percent",
                        0,
                    ),
            },
        )


    # --------------------------------------------------------
    # Run biodiversity pipeline
    # --------------------------------------------------------

    try:

        result = run_pipeline(

            profile=profile,

            user_question=request.question,

            chat_history=None,
        )

    except Exception as exc:

        print(
            "ERROR in /analyze:",
            repr(exc),
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Biodiversity analysis failed: "
                f"{str(exc)}"
            ),
        )


    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        "success": True,

        "question": request.question,

        "environment": profile,

        "analysis":
            result.get(
                "analysis",
                {},
            ),

        "response":
            result.get(
                "response",
                {},
            ),

        "scientific_evidence":
            result.get(
                "scientific_evidence",
                [],
            ),

        "location_biodiversity":
            result.get(
                "location_biodiversity",
                {},
            ),

        "structured_knowledge":
            result.get(
                "structured_knowledge",
                {},
            ),

        "data_quality":
            validation,
    }


# ============================================================
# CHAT
# ============================================================


@app.post("/chat")
async def chat(
    request: ChatRequest,
):

    """
    Multi-turn biodiversity conversation.

    The conversation stores:

        - environmental context
        - user messages
        - assistant messages

    Memory is currently in-memory and therefore
    resets when the server restarts.
    """

    # --------------------------------------------------------
    # Get/create conversation
    # --------------------------------------------------------

    conversation = get_conversation(
        request.session_id
    )


    # --------------------------------------------------------
    # Update environment if supplied
    # --------------------------------------------------------

    if request.environment is not None:

        profile = profile_to_dict(
            request.environment
        )

        update_environment(
            request.session_id,
            profile,
        )

    else:

        profile = conversation.get(
            "environment",
            {},
        )


    # --------------------------------------------------------
    # Ensure profile exists
    # --------------------------------------------------------

    if not profile:

        raise HTTPException(

            status_code=400,

            detail=(
                "Environmental information is required. "
                "Please provide environment data first."
            ),
        )


    # --------------------------------------------------------
    # Validate environment
    # --------------------------------------------------------

    validation = validate_profile(
        profile
    )


    if not validation.get("valid", False):

        raise HTTPException(

            status_code=422,

            detail={
                "message":
                    "Invalid environmental data",

                "errors":
                    validation.get(
                        "errors",
                        [],
                    ),

                "warnings":
                    validation.get(
                        "warnings",
                        [],
                    ),

                "completeness_percent":
                    validation.get(
                        "completeness_percent",
                        0,
                    ),
            },
        )


    # --------------------------------------------------------
    # Save user message
    # --------------------------------------------------------

    add_message(

        request.session_id,

        "user",

        request.question,
    )


    # --------------------------------------------------------
    # Build conversation history
    # --------------------------------------------------------

    chat_history = format_chat_history(

        request.session_id,

        max_messages=10,
    )


    # --------------------------------------------------------
    # Run pipeline
    # --------------------------------------------------------

    try:

        result = run_pipeline(

            profile=profile,

            user_question=request.question,

            chat_history=chat_history,
        )

    except Exception as exc:

        print(
            "ERROR in /chat:",
            repr(exc),
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Chat processing failed: "
                f"{str(exc)}"
            ),
        )


    # --------------------------------------------------------
    # Extract response
    # --------------------------------------------------------

    response = result.get(
        "response",
        {},
    )


    # --------------------------------------------------------
    # Save assistant response
    # --------------------------------------------------------

    if isinstance(response, dict):

        assistant_message = response.get(
            "assessment",
            str(response),
        )

    else:

        assistant_message = str(
            response
        )


    add_message(

        request.session_id,

        "assistant",

        assistant_message,
    )


    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return {

        "success": True,

        "session_id":
            request.session_id,

        "question":
            request.question,

        "environment":
            profile,

        "response":
            response,

        "analysis":
            result.get(
                "analysis",
                {},
            ),

        "scientific_evidence":
            result.get(
                "scientific_evidence",
                [],
            ),

        "location_biodiversity":
            result.get(
                "location_biodiversity",
                {},
            ),

        "structured_knowledge":
            result.get(
                "structured_knowledge",
                {},
            ),

        "data_quality":
            validation,
    }


# ============================================================
# STARTUP
# ============================================================


@app.on_event("startup")
async def startup_event():

    print("=" * 60)

    print(
        "Darukaa.Earth API starting..."
    )

    print(
        f"Project root: {PROJECT_ROOT}"
    )

    print(
        f"Frontend directory: {FRONTEND_DIR}"
    )

    print(
        f"Frontend index exists: "
        f"{FRONTEND_INDEX.exists()}"
    )

    print(
        "Location support: Region + Latitude + Longitude"
    )

    print(
        "Ready."
    )

    print("=" * 60)