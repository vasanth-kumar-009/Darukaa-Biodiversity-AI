# ============================================================
# DARUKAA.EARTH - BIODIVERSITY INTELLIGENCE API
# ============================================================

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel, Field

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FRONTEND_DIR = PROJECT_ROOT / "frontend"

FRONTEND_INDEX = FRONTEND_DIR / "index.html"


# ============================================================
# INTERNAL MODULES
# ============================================================

from backend.validation import validate_environment

from backend.memory import (
    get_conversation,
    update_environment,
    add_message,
    format_chat_history
)

from backend.biodiversity_pipeline import run_pipeline


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Darukaa.Earth Biodiversity Intelligence API",

    description=(
        "AI-powered biodiversity and environmental "
        "intelligence system using scientific RAG, "
        "environmental reasoning, structured knowledge, "
        "GBIF biodiversity data, and Gemini."
    ),

    version="1.0.0"
)


# ============================================================
# STATIC FRONTEND FILES
# ============================================================

if FRONTEND_DIR.exists():

    app.mount(
        "/static",
        StaticFiles(directory=str(FRONTEND_DIR)),
        name="static"
    )


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",

        "http://127.0.0.1:8000",
        "http://localhost:8000",

        "https://darukaa-biodiversity-ai.vercel.app"
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
        description="Soil pH"
    )

    organic_carbon_percent: float | None = Field(
        default=None,
        description="Soil organic carbon percentage"
    )

    moisture_percent: float | None = Field(
        default=None,
        description="Soil moisture percentage"
    )


class Climate(BaseModel):

    rainfall_mm_year: float | None = Field(
        default=None,
        description="Annual rainfall in millimeters"
    )

    temperature_celsius: float | None = Field(
        default=None,
        description="Average temperature in Celsius"
    )


class Land(BaseModel):

    land_use: str | None = Field(
        default=None,
        description="Land use category"
    )

    crop_type: str | None = Field(
        default=None,
        description="Crop type or cropping system"
    )


class Biodiversity(BaseModel):

    species_richness: str | None = Field(
        default=None,
        description=(
            "Species richness: low, moderate, "
            "medium, or high"
        )
    )

    habitat_diversity: str | None = Field(
        default=None,
        description=(
            "Habitat diversity: low, moderate, "
            "medium, or high"
        )
    )


class HumanImpact(BaseModel):

    pollution_level: str | None = Field(
        default=None,
        description="Pollution level"
    )

    deforestation_level: str | None = Field(
        default=None,
        description="Deforestation level"
    )

    habitat_fragmentation: str | None = Field(
        default=None,
        description="Habitat fragmentation level"
    )


class Location(BaseModel):

    latitude: float | None = Field(
        default=None,
        description="Latitude"
    )

    longitude: float | None = Field(
        default=None,
        description="Longitude"
    )

    region: str | None = Field(
        default=None,
        description="Region name"
    )


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
        description="Environmental or biodiversity question"
    )

    environment: EnvironmentalProfile


class ChatRequest(BaseModel):

    session_id: str = Field(
        ...,
        min_length=1,
        description="Conversation session identifier"
    )

    question: str = Field(
        ...,
        min_length=1,
        description="User question"
    )

    environment: EnvironmentalProfile | None = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def profile_to_dict(
    profile: EnvironmentalProfile
):
    """
    Convert Pydantic environmental profile
    into a normal Python dictionary.
    """

    return profile.model_dump()


def validate_profile(
    profile_dict
):
    """
    Run the project's custom environmental validation.
    """

    try:

        validation_result = validate_environment(
            profile_dict
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Environmental validation failed: "
                f"{str(e)}"
            )
        )

    if not validation_result.get(
        "valid",
        False
    ):

        raise HTTPException(
            status_code=422,

            detail={
                "message": "Invalid environmental data",

                "errors": validation_result.get(
                    "errors",
                    []
                ),

                "warnings": validation_result.get(
                    "warnings",
                    []
                ),

                "completeness_percent":
                    validation_result.get(
                        "completeness_percent",
                        0
                    )
            }
        )

    return validation_result


# ============================================================
# ROOT / FRONTEND
# ============================================================

@app.get(
    "/",
    include_in_schema=False
)
async def root():

    """
    Serve the Darukaa.Earth frontend.

    The browser opens:

        /

    and FastAPI returns:

        frontend/index.html
    """

    if FRONTEND_INDEX.exists():

        return FileResponse(
            str(FRONTEND_INDEX),
            media_type="text/html"
        )

    return {
        "name":
            "Darukaa.Earth Biodiversity Intelligence API",

        "status":
            "running",

        "version":
            "1.0.0",

        "message":
            "Frontend index.html was not found."
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",

        "service":
            "Darukaa.Earth Biodiversity Intelligence API"
    }


# ============================================================
# API INFORMATION
# ============================================================

@app.get("/info")
async def info():

    return {

        "name":
            "Darukaa.Earth Biodiversity Intelligence API",

        "version":
            "1.0.0",

        "features": [

            "Environmental reasoning",

            "Scientific RAG",

            "Structured environmental knowledge",

            "Evidence-backed recommendations",

            "Multi-metric reasoning",

            "GBIF biodiversity observations",

            "Gemini-powered response generation",

            "Conversational memory",

            "Structured JSON input"
        ],

        "knowledge_sources": [

            "FAO soil biodiversity literature",

            "FAO agroforestry literature",

            "FAO biodiversity literature",

            "Structured environmental dataset",

            "GBIF biodiversity observations"
        ]
    }


# ============================================================
# ANALYZE
# ============================================================

@app.post("/analyze")
async def analyze(
    request: BiodiversityRequest
):

    """
    Analyze a structured environmental profile.

    Pipeline:

        Validation
            ↓
        Environmental reasoning
            ↓
        Scientific RAG
            ↓
        Structured knowledge
            ↓
        GBIF
            ↓
        Gemini
            ↓
        Evidence-backed recommendations
    """

    try:

        # ----------------------------------------------------
        # Convert request
        # ----------------------------------------------------

        profile = profile_to_dict(
            request.environment
        )


        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        data_quality = validate_profile(
            profile
        )


        # ----------------------------------------------------
        # Run complete pipeline
        # ----------------------------------------------------

        result = run_pipeline(

            profile=profile,

            user_question=request.question,

            chat_history=None
        )


        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {

            "success": True,

            "question":
                request.question,

            "environment":
                profile,

            "analysis":
                result.get(
                    "analysis",
                    {}
                ),

            "response":
                result.get(
                    "response",
                    {}
                ),

            "scientific_evidence":
                result.get(
                    "scientific_evidence",
                    []
                ),

            "location_biodiversity":
                result.get(
                    "location_biodiversity",
                    {}
                ),

            "structured_knowledge":
                result.get(
                    "structured_knowledge",
                    {}
                ),

            "data_quality":
                data_quality
        }


    except HTTPException:

        raise


    except Exception as e:

        print()
        print("=" * 60)
        print("ERROR IN /analyze")
        print("=" * 60)
        print(str(e))
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
async def chat(
    request: ChatRequest
):

    """
    Conversational biodiversity analysis.

    Maintains:

        - environmental context
        - user messages
        - assistant messages
        - session history
    """

    try:

        # ----------------------------------------------------
        # Get conversation
        # ----------------------------------------------------

        conversation = get_conversation(
            request.session_id
        )


        # ----------------------------------------------------
        # Update environment if provided
        # ----------------------------------------------------

        if request.environment is not None:

            profile = profile_to_dict(
                request.environment
            )

            update_environment(
                request.session_id,
                profile
            )


        # ----------------------------------------------------
        # Get current environment
        # ----------------------------------------------------

        conversation = get_conversation(
            request.session_id
        )

        profile = conversation.get(
            "environment",
            {}
        )


        # ----------------------------------------------------
        # Validate environment
        # ----------------------------------------------------

        data_quality = validate_profile(
            profile
        )


        # ----------------------------------------------------
        # Add user message
        # ----------------------------------------------------

        add_message(
            request.session_id,
            "user",
            request.question
        )


        # ----------------------------------------------------
        # Get chat history
        # ----------------------------------------------------

        chat_history = format_chat_history(
            request.session_id,
            max_messages=10
        )


        # ----------------------------------------------------
        # Run pipeline
        # ----------------------------------------------------

        result = run_pipeline(

            profile=profile,

            user_question=request.question,

            chat_history=chat_history
        )


        assistant_response = result.get(
            "response",
            {}
        )


        # ----------------------------------------------------
        # Save assistant response
        # ----------------------------------------------------

        add_message(
            request.session_id,
            "assistant",
            assistant_response
        )


        # ----------------------------------------------------
        # Return
        # ----------------------------------------------------

        return {

            "success": True,

            "session_id":
                request.session_id,

            "question":
                request.question,

            "environment":
                profile,

            "response":
                assistant_response,

            "analysis":
                result.get(
                    "analysis",
                    {}
                ),

            "scientific_evidence":
                result.get(
                    "scientific_evidence",
                    []
                ),

            "location_biodiversity":
                result.get(
                    "location_biodiversity",
                    {}
                ),

            "structured_knowledge":
                result.get(
                    "structured_knowledge",
                    {}
                ),

            "data_quality":
                data_quality
        }


    except HTTPException:

        raise


    except Exception as e:

        print()
        print("=" * 60)
        print("ERROR IN /chat")
        print("=" * 60)
        print(str(e))
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# STARTUP MESSAGE
# ============================================================

@app.on_event("startup")
async def startup_event():

    print()
    print("=" * 60)
    print("DARUKAA.EARTH BIODIVERSITY AI")
    print("=" * 60)

    print("API started successfully.")

    print(
        f"Project root: {PROJECT_ROOT}"
    )

    print(
        f"Frontend directory: {FRONTEND_DIR}"
    )

    print(
        f"Frontend index: {FRONTEND_INDEX}"
    )

    print(
        f"Frontend available: "
        f"{FRONTEND_INDEX.exists()}"
    )

    print("=" * 60)