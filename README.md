# 🌿 Darukaa.Earth — AI Biodiversity Intelligence

> An AI-powered biodiversity intelligence system that combines environmental reasoning, scientific knowledge retrieval, structured environmental data, biodiversity observations, and conversational AI to generate evidence-backed biodiversity recommendations.

---

## 📌 Overview

Darukaa.Earth is an AI-based environmental intelligence system designed to analyze biodiversity and ecosystem conditions using multiple environmental variables.

Instead of relying only on a generic Large Language Model (LLM), the system combines:

- 🌱 Soil parameters
- 🌦️ Climate parameters
- 🌾 Land-use information
- 🦋 Biodiversity indicators
- 🏭 Human-impact indicators
- 📍 Geographic coordinates
- 📚 Scientific documents
- 🧠 Rule-based environmental reasoning
- 🔎 Retrieval-Augmented Generation (RAG)
- 📊 Structured environmental datasets
- 🌍 GBIF biodiversity observations
- 🤖 Gemini AI
- 💬 Multi-turn conversational memory

The system produces actionable recommendations explaining:

- What should be done
- Why the intervention may help
- Which environmental metrics are affected
- Expected time horizon
- Confidence level
- Supporting scientific evidence
- Important data limitations

---

# 🎯 Problem Statement

Environmental and biodiversity decisions often require reasoning across several interacting variables rather than considering one metric independently.

For example:

```text
Low rainfall
      +
Low soil moisture
      +
Low soil organic carbon
      +
Wheat monoculture
      +
Low habitat diversity
      +
Low species richness
```

# 💡 Key Features
## 1. Multi-Metric Environmental Reasoning

The system evaluates relationships among multiple variables such as:

```
Soil Organic Carbon
        ↓
Soil Water Retention
        ↓
Soil Moisture
        ↓
Vegetation Condition
        ↓
Habitat Diversity
        ↓
Biodiversity
```
The reasoning layer also considers relationships involving:

- Soil organic carbon + rainfall
- Rainfall + land use
- Monoculture + biodiversity
- Soil condition + biodiversity
- Habitat fragmentation + biodiversity
- Climate + soil condition + biodiversity

## 2. Scientific RAG

Darukaa.Earth uses scientific documents as a retrieval layer.

Current scientific knowledge sources include:

```
knowledge_base/
│
├── biodiversity/
│   └── FAO_biodiversity.pdf
│
├── land_use/
│   └── FAO_agroforestry.pdf
│
└── soil/
    └── FAO_soil_biodiversity.pdf
```
The system:

1. Extracts scientific text
2. Splits documents into chunks
3. Retrieves relevant evidence
4. Passes the retrieved evidence to the AI generator
5. Links recommendations to retrieved scientific sources


The local environment uses ChromaDB for retrieval, while the deployment-safe retrieval path avoids depending on a writable persistent Chroma database.

## 3. Structured Environmental Knowledge

The project includes structured environmental reference data:
```
data/environmental_dataset.json
```
The dataset provides example/reference environmental profiles containing:

- Soil
- Climate
- Land use
- Biodiversity
- Human impact
- Location

The structured knowledge layer can retrieve:

- Matching regional sites
- Matching biodiversity profiles
- Similar environmental conditions

> The included environmental dataset is a demonstration/reference dataset and should not be interpreted as a complete representation of real-world environmental conditions.


4\. GBIF Biodiversity Integration
=================================

The system integrates the GBIF Occurrence Search API to retrieve biodiversity observations near supplied geographic coordinates.

Input:

```
Latitude
Longitude
```

Output may include:

```
Record count
Returned records
Observed taxa
Occurrence samples
```

Example:

```
Latitude: 30.901
Longitude: 75.8573
Radius: 25 km
```

The system uses GBIF observations as supporting biodiversity context.

> GBIF occurrence records are observations available through the API and are not equivalent to complete ecological species richness. Missing GBIF records must not be interpreted as species absence.

* * * * *

5\. Environmental Validation
============================

The API validates environmental inputs before running the main pipeline.

Examples of validated ranges include:

```
pH                    0 -- 14
Organic carbon        0 -- 100%
Soil moisture         0 -- 100%
Rainfall              0 -- 20,000 mm/year
Temperature           -100 -- 70 °C
Latitude              -90 -- 90
Longitude             -180 -- 180
```

The validation layer also reports:

-   Invalid values
-   Missing information
-   Data completeness
-   Warnings

* * * * *

6\. Conversational Intelligence
===============================

Darukaa.Earth supports multi-turn conversations through the `/chat` endpoint.

The system stores:

```
Environmental context
        +
User messages
        +
Assistant responses
```

This allows follow-up questions such as:

```
User:
How can I improve biodiversity?

User:
Which intervention should I start with?

User:
How would that affect soil moisture?
```

The system can use the previous conversation context when generating later responses.

> Current conversation memory is stored in process memory and resets when the application restarts.

* * * * *

7\. Evidence-Backed Recommendations
===================================

Recommendations are generated in a structured form:

```
{
  "action": "",
  "why_it_works": "",
  "impacted_metrics": [],
  "time_horizon": "",
  "confidence": ""
}
```

Example structure:

```
Recommendation
      ↓
Why it works
      ↓
Impacted metrics
      ↓
Time horizon
      ↓
Confidence
      ↓
Scientific evidence
```

This helps distinguish evidence-backed reasoning from generic AI suggestions.

* * * * *

🏗️ System Architecture
=======================

```
                         USER
                           │
                           ▼
                ┌─────────────────────┐
                │     Web Frontend    │
                │ HTML / CSS / JS     │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │      FastAPI        │
                │      Backend        │
                └──────────┬──────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
   ┌────────────────┐ ┌────────────┐ ┌─────────────┐
   │ Environmental  │ │ Structured │ │    GBIF     │
   │   Reasoning    │ │ Knowledge  │ │ Biodiversity│
   └───────┬────────┘ └─────┬──────┘ └──────┬──────┘
           │                │               │
           ▼                ▼               ▼
   ┌─────────────────────────────────────────────┐
   │             Scientific RAG Layer             │
   │                                               │
   │ FAO PDFs → Chunking → Retrieval → Evidence  │
   └──────────────────────┬──────────────────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Gemini Model   │
                 │ Response Engine  │
                 └────────┬─────────┘
                          │
                          ▼
                Evidence-backed response
```

* * * * *

🔄 Main Pipeline
================

The main biodiversity pipeline follows this flow:

```
Environmental Input
        │
        ▼
Data Validation
        │
        ▼
Environmental Reasoning
        │
        ▼
Scientific RAG Retrieval
        │
        ▼
Structured Knowledge Retrieval
        │
        ▼
GBIF Biodiversity Lookup
        │
        ▼
Gemini Response Generation
        │
        ▼
Structured JSON Response
```

* * * * *

🧠 AI Reasoning Architecture
============================

The system is intentionally designed as more than a generic LLM chatbot.

### Layer 1 --- Input

Structured environmental variables:

```
soil
climate
land
biodiversity
human_impact
location
```

### Layer 2 --- Rule-Based Reasoning

Identifies:

-   Environmental findings
-   Severity
-   Variable interactions
-   Potential environmental pressures
-   Candidate interventions

### Layer 3 --- Scientific Retrieval

Retrieves supporting information from scientific documents.

### Layer 4 --- Structured Knowledge

Finds:

-   Similar environments
-   Matching regions
-   Biodiversity profiles

### Layer 5 --- Biodiversity Context

Queries GBIF for geographically relevant observations.

### Layer 6 --- Generative AI

Gemini combines:

```
Environmental profile
        +
Environmental reasoning
        +
Scientific evidence
        +
Structured data
        +
GBIF observations
        +
Conversation history
```

to generate the final response.

* * * * *

📁 Project Structure
====================

```
Darukaa-Biodiversity-AI/
│
├── backend/
│   ├── main.py
│   ├── biodiversity_pipeline.py
│   ├── llm_generator.py
│   ├── gbif.py
│   ├── validation.py
│   ├── memory.py
│   ├── knowledge_layer.py
│   └── data_loader.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── data/
│   ├── environmental_dataset.json
│   ├── environmental_schema.json
│   └── knowledge_metadata.json
│
├── knowledge_base/
│   ├── biodiversity/
│   │   └── FAO_biodiversity.pdf
│   ├── land_use/
│   │   └── FAO_agroforestry.pdf
│   └── soil/
│       └── FAO_soil_biodiversity.pdf
│
├── rag/
│   ├── environmental_rag.py
│   ├── retrieve.py
│   └── ingest.py
│
├── reasoning/
│   └── environmental_reasoner.py
│
├── tests/
│   ├── test_validation.py
│   ├── test_reasoning.py
│   ├── test_knowledge_layer.py
│   ├── test_rag.py
│   ├── test_gbif.py
│   ├── test_api.py
│   └── test_edge_cases.py
│
├── requirements.txt
├── render.yaml
├── .gitignore
└── README.md
```

* * * * *

🛠️ Technology Stack
====================

Backend
-------

-   Python
-   FastAPI
-   Pydantic
-   Uvicorn

AI / LLM
--------

-   Google Gemini API
-   `google-genai`

RAG / Knowledge Retrieval
-------------------------

-   ChromaDB
-   PyPDF
-   Scientific PDF knowledge base

Environmental Data
------------------

-   JSON-based structured datasets

Biodiversity Data
-----------------

-   GBIF Occurrence Search API

Frontend
--------

-   HTML
-   CSS
-   JavaScript

Deployment
----------

-   Render
-   Railway configuration included

* * * * *

📦 Requirements
===============

The project uses:

```
fastapi
uvicorn
pydantic
python-dotenv
google-genai
chromadb
pypdf
requests
httpx
```

The deployment configuration intentionally avoids large ML dependencies such as:

```
sentence-transformers
torch
torchvision
```

to keep the deployment lightweight.

* * * * *

🚀 Local Setup
==============

1\. Clone the repository
------------------------

```
git clone https://github.com/vasanth-kumar-009/Darukaa-Biodiversity-AI.git
```

```
cd Darukaa-Biodiversity-AI
```

* * * * *

2\. Create a virtual environment
--------------------------------

### Windows

```
python -m venv venv
```

Activate:

```
venv\Scripts\activate
```

### Linux / macOS

```
python3 -m venv venv
```

```
source venv/bin/activate
```

* * * * *

3\. Install dependencies
------------------------

```
pip install -r requirements.txt
```

* * * * *

🔐 Environment Variables
========================

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key
```

Example:

```
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

### Security

Never commit `.env` to GitHub.

Make sure `.gitignore` contains:

```
.env
```

* * * * *

📚 Build the Local Knowledge Base
=================================

For local development, the project can use ChromaDB for scientific retrieval.

Run:

```
python rag/ingest.py
```

This processes the PDFs in:

```
knowledge_base/
```

and creates the local vector database under:

```
data/chroma_db/
```

The generated Chroma database is intended for local development and should not be committed to GitHub.

* * * * *

▶️ Run the Application
======================

Start FastAPI:

```
python -m uvicorn backend.main:app --reload
```

The application will be available at:

```
http://127.0.0.1:8000
```

* * * * *

🌐 Frontend
===========

Open:

```
http://127.0.0.1:8000/
```

The frontend is served directly by FastAPI.

* * * * *

📖 API Documentation
====================

FastAPI automatically provides interactive API documentation.

Open:

```
http://127.0.0.1:8000/docs
```

Alternative documentation:

```
http://127.0.0.1:8000/redoc
```

* * * * *

🔌 API Endpoints
================

GET `/`
-------

Serves the web frontend.

* * * * *

GET `/health`
-------------

Health check endpoint.

Example:

```
{
  "status": "healthy",
  "service": "Darukaa.Earth",
  "version": "1.0.0"
}
```

* * * * *

GET `/info`
-----------

Returns project information and supported components.

* * * * *

POST `/analyze`
---------------

Runs the full biodiversity analysis pipeline.

### Request

```
{
  "question": "How can I improve biodiversity and soil health?",
  "environment": {
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
      "latitude": 30.901,
      "longitude": 75.8573,
      "region": "Punjab"
    }
  }
}
```

* * * * *

POST `/chat`
------------

Supports multi-turn environmental conversations.

Example:

```
{
  "session_id": "demo-session-1",
  "question": "Which intervention should I start with?",
  "environment": {
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
      "latitude": 30.901,
      "longitude": 75.8573,
      "region": "Punjab"
    }
  }
}
```

* * * * *

🧪 Testing
==========

The project includes tests for the major modules.

Run:

```
python tests/test_validation.py
```

```
python tests/test_reasoning.py
```

```
python tests/test_knowledge_layer.py
```

```
python tests/test_rag.py
```

```
python tests/test_gbif.py
```

```
python tests/test_api.py
```

```
python tests/test_edge_cases.py
```

These tests cover:

-   Environmental validation
-   Environmental reasoning
-   Structured knowledge retrieval
-   Scientific RAG
-   GBIF integration
-   API endpoints
-   Edge cases

* * * * *

🌾 Example Environmental Scenario
=================================

### Input

```
Region: Punjab

Soil:
pH = 6.5
Organic Carbon = 0.3%
Moisture = 15%

Climate:
Rainfall = 450 mm/year
Temperature = 31°C

Land:
Cropland
Wheat monoculture

Biodiversity:
Species richness = Low
Habitat diversity = Low

Human Impact:
Pollution = Moderate
Deforestation = Low
Habitat fragmentation = Moderate
```

### Question

```
How can I improve biodiversity and soil health in this
wheat monoculture while dealing with low rainfall and
low soil moisture?
```

### System reasoning

```
Low organic carbon
        +
Low rainfall
        +
Low soil moisture
        +
Monoculture
        +
Low habitat diversity
        +
Low species richness
```

The system can then retrieve relevant scientific evidence and generate recommendations connected to multiple environmental metrics.

* * * * *

📊 Output Structure
===================

The final response follows a structured format:

```
{
  "assessment": "",

  "key_interactions": [
    {
      "interaction": "",
      "reasoning": ""
    }
  ],

  "recommendations": [
    {
      "action": "",
      "why_it_works": "",
      "impacted_metrics": [],
      "time_horizon": "",
      "confidence": ""
    }
  ],

  "scientific_evidence": [
    {
      "source": "",
      "page": "",
      "evidence": ""
    }
  ],

  "data_limitations": []
}
```

* * * * *

📚 Scientific Knowledge Sources
===============================

Current scientific documents included in the repository:

### FAO Biodiversity

```
knowledge_base/biodiversity/FAO_biodiversity.pdf
```

Used for environmental and biodiversity relationships.

### FAO Agroforestry

```
knowledge_base/land_use/FAO_agroforestry.pdf
```

Used for:

-   Agroforestry
-   Crop diversification
-   Soil management
-   Water conservation
-   Crop-livestock systems
-   Habitat-supporting practices

### FAO Soil Biodiversity

```
knowledge_base/soil/FAO_soil_biodiversity.pdf
```

Used for soil organisms, soil biological processes, and soil biodiversity relationships.

* * * * *

🌍 Location-Aware Analysis
==========================

The application supports:

```
Region
Latitude
Longitude
```

When coordinates are supplied, the system can query GBIF for nearby biodiversity observations.

Example:

```
Latitude: 30.901
Longitude: 75.8573
```

The geographic component is optional, but coordinates provide additional biodiversity context.

* * * * *

⚠️ Data Limitations
===================

Darukaa.Earth explicitly communicates important uncertainty.

### GBIF

GBIF records represent observed occurrences and are not a complete biodiversity survey.

Therefore:

```
Observed taxa count ≠ true species richness
```

and:

```
No observation ≠ species absence
```

### Structured Dataset

The environmental dataset contains demonstration/reference records.

It should not be treated as a complete environmental monitoring system.

### Environmental Measurements

A single environmental profile does not capture:

-   Seasonal variation
-   Historical trends
-   Detailed management history
-   Complete ecological interactions

Therefore, recommendations should be interpreted as evidence-supported guidance rather than a replacement for field assessment.

* * * * *

☁️ Render Deployment
====================

The repository includes:

```
render.yaml
```

The intended deployment configuration uses:

```
Build Command:
pip install -r requirements.txt
```

and:

```
Start Command:
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Health check:

```
/health
```

Required environment variable:

```
GEMINI_API_KEY
```

The scientific PDFs remain inside:

```
knowledge_base/
```

and the deployment-safe retrieval path does not depend on a writable persistent Chroma database.

* * * * *


🔒 Security
===========

Do not commit:

```
.env
```

Do not expose:

```
GEMINI_API_KEY
```

Recommended repository protections include:

-   Secret scanning
-   Push protection
-   Dependency security alerts
-   Regular dependency updates

* * * * *

🧩 Design Principles
====================

Darukaa.Earth follows these principles:

### Scientific grounding

Recommendations should be connected to supplied scientific evidence whenever possible.

### Multi-metric reasoning

Environmental variables should be considered together rather than independently.

### Transparency

The system should clearly communicate:

-   Data limitations
-   Uncertainty
-   Evidence source
-   Observation limitations

### No fabricated evidence

The system is instructed not to invent:

-   Scientific papers
-   Authors
-   Measurements
-   Statistics
-   Citations

* * * * *

🛣️ Future Improvements
=======================

Potential future improvements include:

-   Persistent conversational memory
-   PostgreSQL or another external database
-   Advanced vector search infrastructure
-   Semantic embedding retrieval in production
-   Satellite/environmental remote-sensing data
-   Historical environmental time-series
-   More regional biodiversity datasets
-   Weather and climate APIs
-   Habitat connectivity analysis
-   Biodiversity trend detection
-   Automated intervention monitoring
-   GIS-based ecosystem visualization
-   More scientific literature sources
-   Model evaluation against expert-validated cases

* * * * *

🎓 Hackathon Relevance
======================

Darukaa.Earth is designed around the major requirements of the biodiversity intelligence challenge:

```
Knowledge Layer
        +
Scientific Retrieval
        +
Environmental Reasoning
        +
Conversational Intelligence
        +
Evidence-backed Recommendations
        +
Multi-metric Analysis
        +
Location-aware Biodiversity Context
```

The system is therefore structured as an environmental intelligence pipeline rather than a generic LLM-only chatbot.

* * * * *

📸 Demo
=======

### Live Demo

```
https://darukaa-biodiversity-ai-oej4.onrender.com/
```

Replace the above with your actual deployed Render URL.

### API Documentation

```
https://darukaa-biodiversity-ai-oej4.onrender.com/docs
```

### GitHub Repository

```
https://github.com/vasanth-kumar-009/Darukaa-Biodiversity-AI
```

* * * * *

👨‍💻 Project Information
=========================

**Project:** Darukaa.Earth --- AI Biodiversity Intelligence

**Repository:**\
<https://github.com/vasanth-kumar-009/Darukaa-Biodiversity-AI>

**Primary Technologies:**

```
Python
FastAPI
Gemini API
ChromaDB
RAG
GBIF API
Pydantic
JavaScript
HTML
CSS
```

* * * * *

📄 License
==========

Add the project's chosen license here.

Example:

```
MIT License
```

if an MIT `LICENSE` file is added to the repository.

* * * * *

🙌 Acknowledgements
===================

This project uses:

-   FAO scientific publications included in the knowledge base
-   GBIF biodiversity occurrence data
-   Google Gemini for generative reasoning
-   FastAPI for the backend API
-   ChromaDB for local retrieval
-   PyPDF for scientific document extraction
