"""
Gemini LLM Generator for Biodiversity AI

Combines:
- Environmental profile
- Rule-based reasoning
- Scientific RAG evidence
- Structured environmental knowledge
- GBIF biodiversity observations
- Conversation history

Returns a structured JSON biodiversity response.
"""

import os
import json
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ==========================================================
# CONFIGURATION
# ==========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Please add GEMINI_API_KEY to your .env file."
    )


client = genai.Client(
    api_key=API_KEY
)

MODEL_NAME = "gemini-3.5-flash"



# ==========================================================
# GEMINI API CALL
# ==========================================================

def ask_gemini(prompt, max_retries=3):
    """
    Send a prompt to Gemini and return the generated text.
    """

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    )
                )
            )

            return response.text

        except Exception as e:

            error_text = str(e)

            retryable_errors = [
                "503",
                "UNAVAILABLE",
                "429",
                "RESOURCE_EXHAUSTED",
                "timeout",
                "timed out"
            ]

            is_retryable = any(
                error in error_text
                for error in retryable_errors
            )

            if is_retryable and attempt < max_retries - 1:

                wait_time = 2 ** attempt

                print(
                    f"Gemini temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:

                raise


# ==========================================================
# JSON EXTRACTION
# ==========================================================

def extract_json(text):
    """
    Extract JSON object from Gemini output.
    """

    if not text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    text = text.strip()

    # Remove markdown code fences
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # Direct JSON
    try:

        return json.loads(text)

    except json.JSONDecodeError:
        pass

    # Find first JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:

        json_text = text[start:end + 1]

        try:

            return json.loads(json_text)

        except json.JSONDecodeError as e:

            raise ValueError(
                f"Could not parse Gemini JSON response: {e}"
            )

    raise ValueError(
        "No valid JSON object found in Gemini response."
    )


# ==========================================================
# FORMAT RAG EVIDENCE
# ==========================================================

def format_evidence(evidence):
    """
    Convert retrieved RAG evidence into readable prompt text.
    """

    if not evidence:
        return "No scientific evidence was retrieved."

    formatted = []

    for i, item in enumerate(evidence, start=1):

        source = item.get(
            "source",
            "Unknown source"
        )

        page = item.get(
            "page",
            "Unknown"
        )

        text = item.get(
            "text",
            item.get(
                "content",
                ""
            )
        )

        formatted.append(
            f"""
Evidence {i}
Source: {source}
Page: {page}
Content:
{text}
"""
        )

    return "\n".join(formatted)


# ==========================================================
# FORMAT CONVERSATION HISTORY
# ==========================================================

def format_chat_history_for_prompt(chat_history):
    """
    Convert conversation history into prompt text.
    """

    if not chat_history:
        return "No previous conversation."

    lines = []

    for message in chat_history[-10:]:

        if isinstance(message, dict):

            role = message.get(
                "role",
                "user"
            )

            content = message.get(
                "content",
                ""
            )

            lines.append(
                f"{role.upper()}: {content}"
            )

        else:

            lines.append(
                str(message)
            )

    return "\n".join(lines)


# ==========================================================
# MAIN BIODIVERSITY RESPONSE GENERATOR
# ==========================================================

def generate_biodiversity_response(
    profile,
    analysis,
    evidence,
    user_question=None,
    chat_history=None,
    gbif_data=None,
    knowledge_context=None
):
    """
    Generate an evidence-backed biodiversity response.

    Parameters
    ----------
    profile : dict
        Structured environmental information.

    analysis : dict
        Rule-based environmental analysis.

    evidence : list
        Scientific evidence retrieved by RAG.

    user_question : str, optional
        User's natural-language question.

    chat_history : list, optional
        Previous conversation.

    gbif_data : dict, optional
        Location-based biodiversity observations.

    knowledge_context : dict, optional
        Structured environmental dataset matches.

    Returns
    -------
    dict
        Structured biodiversity response.
    """

    # ------------------------------------------------------
    # Prepare data
    # ------------------------------------------------------

    profile_text = json.dumps(
        profile,
        indent=2,
        ensure_ascii=False
    )

    analysis_text = json.dumps(
        analysis,
        indent=2,
        ensure_ascii=False
    )

    evidence_text = format_evidence(
        evidence
    )

    history_text = format_chat_history_for_prompt(
        chat_history
    )

    gbif_text = json.dumps(
        gbif_data or {},
        indent=2,
        ensure_ascii=False
    )

    knowledge_text = json.dumps(
        knowledge_context or {},
        indent=2,
        ensure_ascii=False
    )

    question_text = (
        user_question
        if user_question
        else "Provide an environmental biodiversity assessment."
    )

    # ------------------------------------------------------
    # Prompt
    # ------------------------------------------------------

    prompt = f"""
You are an AI Biodiversity Intelligence Assistant.

Your task is to analyze environmental conditions and provide
scientifically grounded biodiversity recommendations.

You MUST reason across multiple environmental variables.

============================================================
USER QUESTION
============================================================

{question_text}


============================================================
STRUCTURED ENVIRONMENTAL PROFILE
============================================================

{profile_text}


============================================================
RULE-BASED ENVIRONMENTAL ANALYSIS
============================================================

{analysis_text}


============================================================
SCIENTIFIC RAG EVIDENCE
============================================================

{evidence_text}


============================================================
STRUCTURED ENVIRONMENTAL KNOWLEDGE
============================================================

{knowledge_text}

Use this structured dataset as contextual evidence.

IMPORTANT:
The structured environmental dataset contains demonstration/
reference records. Do NOT treat it as a complete representation
of real-world environmental conditions.

Do not invent measurements that are not present.


============================================================
GBIF LOCATION BIODIVERSITY DATA
============================================================

{gbif_text}

IMPORTANT:
GBIF occurrence records represent observations available in
GBIF. They are NOT a complete measurement of true species
richness.

Do NOT claim that the observed taxa count equals the total
number of species present.

Missing GBIF records must NOT be interpreted as species absence.


============================================================
CONVERSATION HISTORY
============================================================

{history_text}


============================================================
REASONING REQUIREMENTS
============================================================

1. Analyze the environmental profile.

2. Identify important environmental problems.

3. Connect at least THREE environmental variables whenever
   the available data supports this.

Examples:

- Soil organic carbon + soil moisture + rainfall
- Land use + biodiversity + habitat fragmentation
- Rainfall + crop type + species richness
- Soil condition + climate + habitat diversity

4. Explain cause-and-effect relationships carefully.

5. Generate practical biodiversity interventions.

6. Every recommendation should explain:

   - What to do
   - Why it works
   - Which environmental metrics are affected
   - Expected time horizon

7. Recommendations must be connected to the supplied
   scientific evidence whenever possible.

8. Do NOT invent scientific papers, authors, statistics,
   measurements, or citations.

9. If the supplied evidence does not support a precise
   numerical improvement estimate, do not invent one.

10. Clearly mention important data limitations.

11. Use GBIF observations only as supporting biodiversity
    context.

12. If the user's question is unclear or important environmental
    information is missing, mention what clarification would
    improve the assessment.

13. Do not claim certainty when the available data is limited.


============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "assessment": "",

    "key_interactions": [
        {{
            "interaction": "",
            "reasoning": ""
        }}
    ],

    "recommendations": [
        {{
            "action": "",
            "why_it_works": "",
            "impacted_metrics": [],
            "time_horizon": "",
            "confidence": ""
        }}
    ],

    "scientific_evidence": [
        {{
            "source": "",
            "page": "",
            "evidence": ""
        }}
    ],

    "data_limitations": []
}}

============================================================
QUALITY REQUIREMENTS
============================================================

The answer should be:

- scientifically grounded
- environmentally meaningful
- based on the supplied data
- multi-metric
- actionable
- transparent about uncertainty
- concise but sufficiently detailed

Do not return Markdown.
Do not return explanations outside the JSON.
"""


    # ------------------------------------------------------
    # Call Gemini
    # ------------------------------------------------------

    raw_response = ask_gemini(
        prompt
    )

    # ------------------------------------------------------
    # Parse JSON
    # ------------------------------------------------------

    try:

        result = extract_json(
            raw_response
        )

    except Exception as e:

        print(
            "Gemini JSON parsing failed:",
            str(e)
        )

        return {
            "assessment": raw_response,
            "key_interactions": [],
            "recommendations": [],
            "scientific_evidence": [],
            "data_limitations": [
                "The generated response could not be parsed into the expected JSON structure."
            ]
        }

    # ------------------------------------------------------
    # Ensure required fields exist
    # ------------------------------------------------------

    result.setdefault(
        "assessment",
        ""
    )

    result.setdefault(
        "key_interactions",
        []
    )

    result.setdefault(
        "recommendations",
        []
    )

    result.setdefault(
        "scientific_evidence",
        []
    )

    result.setdefault(
        "data_limitations",
        []
    )

    return result


# ==========================================================
# TEST
# ==========================================================

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
        },

        "location": {
            "latitude": 30.9010,
            "longitude": 75.8573,
            "region": "Punjab"
        }
    }

    test_analysis = {
        "findings": [
            "Low soil organic carbon",
            "Low soil moisture",
            "Low biodiversity"
        ],

        "interactions": [
            {
                "variables": [
                    "soil organic carbon",
                    "rainfall",
                    "soil moisture"
                ],
                "reasoning": (
                    "Low organic carbon and limited rainfall "
                    "can reduce soil water retention."
                )
            }
        ],

        "recommendations": [
            "Increase organic matter",
            "Improve habitat diversity"
        ]
    }

    test_evidence = [
        {
            "source": "FAO Soil Biodiversity",
            "page": "1",
            "text": (
                "Soil organisms contribute to soil health "
                "and ecosystem functions."
            )
        }
    ]

    test_knowledge = {
        "matching_region_sites": [],
        "matching_biodiversity_sites": [],
        "similar_environments": []
    }

    test_gbif = {
        "available": True,
        "record_count": 10,
        "returned_records": 10,
        "observed_taxa_count": 5,
        "observed_taxa": [
            "Example species"
        ]
    }

    result = generate_biodiversity_response(
        profile=test_profile,
        analysis=test_analysis,
        evidence=test_evidence,
        user_question=(
            "How can biodiversity be improved "
            "in this environment?"
        ),
        chat_history=[],
        gbif_data=test_gbif,
        knowledge_context=test_knowledge
    )

    print("\n" + "=" * 60)
    print("GEMINI RESPONSE")
    print("=" * 60)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )