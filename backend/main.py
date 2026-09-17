from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.biodiversity_pipeline import run_pipeline
from backend.memory import (
    get_context,
    update_environment,
    add_message,
    format_chat_history
)
from backend.validation import validate_environment


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Darukaa.Earth Biodiversity Intelligence API",
    description=(
        "AI-powered biodiversity intelligence system using "
        "environmental reasoning, RAG, GBIF and Gemini."
    ),
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# PYDANTIC MODELS
# ============================================================

class Soil(BaseModel):

    ph: Optional[float] = None

    organic_carbon_percent: Optional[float] = None

    moisture_percent: Optional[float] = None


class Climate(BaseModel):

    rainfall_mm_year: Optional[float] = None

    temperature_celsius: Optional[float] = None


class Land(BaseModel):

    land_use: Optional[str] = None

    crop_type: Optional[str] = None


class Biodiversity(BaseModel):

    species_richness: Optional[str] = None

    habitat_diversity: Optional[str] = None


class HumanImpact(BaseModel):

    pollution_level: Optional[str] = None

    deforestation_level: Optional[str] = None

    habitat_fragmentation: Optional[str] = None


class Location(BaseModel):

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    region: Optional[str] = None


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

    question: str

    environment: EnvironmentalProfile


class ChatRequest(BaseModel):

    session_id: str

    question: str

    environment: Optional[EnvironmentalProfile] = None


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name": "Darukaa.Earth Biodiversity Intelligence API",

        "status": "running",

        "version": "1.0.0",

        "features": [
            "Environmental reasoning",
            "Scientific RAG",
            "GBIF biodiversity observations",
            "Gemini AI reasoning",
            "Multi-turn conversation"
        ]
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# API INFORMATION
# ============================================================

@app.get("/info")
def info():

    return {

        "project": "Darukaa.Earth",

        "description": (
            "AI Biodiversity Intelligence Chatbot"
        ),

        "pipeline": [
            "Environmental profile",
            "Environmental reasoning",
            "Scientific RAG",
            "GBIF location biodiversity",
            "Gemini generation"
        ],

        "endpoints": [
            "/",
            "/health",
            "/info",
            "/analyze",
            "/chat"
        ]
    }


# ============================================================
# ANALYZE ENVIRONMENT
# ============================================================

@app.post("/analyze")
def analyze_environment(
    request: BiodiversityRequest
):

    try:

        # ----------------------------------------------------
        # Convert Pydantic model to dictionary
        # ----------------------------------------------------

        environment = request.environment.model_dump()

        # ----------------------------------------------------
        # Validate environmental data
        # ----------------------------------------------------

        validation = validate_environment(
            environment
        )

        if not validation["valid"]:

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid environmental data.",
                    "errors": validation["errors"],
                    "warnings": validation["warnings"]
                }
            )

        # ----------------------------------------------------
        # Run complete pipeline
        # ----------------------------------------------------

        result = run_pipeline(

            profile=environment,

            user_question=request.question,

            chat_history=None
        )

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return {

            "success": True,

            "question": request.question,

            "environment": environment,

            "analysis": result.get(
                "analysis",
                {}
            ),

            "response": result.get(
                "response",
                {}
            ),

            "scientific_evidence": result.get(
                "scientific_evidence",
                []
            ),

            # NEW GBIF DATA
            "location_biodiversity": result.get(
                "location_biodiversity",
                {}
            ),

            "data_quality": validation
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            "\nERROR IN /analyze:"
        )

        print(e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
def chat(
    request: ChatRequest
):

    try:

        # ----------------------------------------------------
        # Get existing conversation
        # ----------------------------------------------------

        context = get_context(
            request.session_id
        )

        existing_environment = context.get(
            "environment",
            {}
        )

        # ----------------------------------------------------
        # Merge new environment data
        # ----------------------------------------------------

        if request.environment is not None:

            new_environment = (
                request.environment.model_dump(
                    exclude_none=True
                )
            )

            update_environment(
                request.session_id,
                new_environment
            )

        # ----------------------------------------------------
        # Get updated environment
        # ----------------------------------------------------

        context = get_context(
            request.session_id
        )

        environment = context.get(
            "environment",
            {}
        )

        # ----------------------------------------------------
        # Validate environment
        # ----------------------------------------------------

        validation = validate_environment(
            environment
        )

        if not validation["valid"]:

            raise HTTPException(
                status_code=400,
                detail={
                    "message": (
                        "Environmental data is invalid."
                    ),

                    "errors": validation["errors"],

                    "warnings": validation["warnings"]
                }
            )

        # ----------------------------------------------------
        # Store user message
        # ----------------------------------------------------

        add_message(
            request.session_id,

            "user",

            request.question
        )

        # ----------------------------------------------------
        # Get conversation history
        # ----------------------------------------------------

        chat_history = format_chat_history(
            request.session_id,
            max_messages=10
        )

        # ----------------------------------------------------
        # Run complete pipeline
        # ----------------------------------------------------

        result = run_pipeline(

            profile=environment,

            user_question=request.question,

            chat_history=chat_history
        )

        # ----------------------------------------------------
        # Store assistant response
        # ----------------------------------------------------

        assistant_response = result.get(
            "response",
            {}
        )

        add_message(

            request.session_id,

            "assistant",

            assistant_response
        )

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {

            "success": True,

            "session_id": request.session_id,

            "question": request.question,

            "environment": environment,

            "response": assistant_response,

            "analysis": result.get(
                "analysis",
                {}
            ),

            "scientific_evidence": result.get(
                "scientific_evidence",
                []
            ),

            # NEW GBIF DATA
            "location_biodiversity": result.get(
                "location_biodiversity",
                {}
            ),

            "data_quality": validation
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            "\nERROR IN /chat:"
        )

        print(e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )