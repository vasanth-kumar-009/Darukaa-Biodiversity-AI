"""
Gemini LLM Generator for Biodiversity AI

Optimized for deployment:
- smaller prompts
- limited GBIF information
- limited evidence size
- short conversation history
- Gemini timeout
- limited retries
- fallback response
"""

import os
import json
import re
import time

from dotenv import load_dotenv

from google import genai

from google.genai import types


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not API_KEY:

    raise ValueError(
        "GEMINI_API_KEY not found."
    )


client = genai.Client(

    api_key=API_KEY,

    http_options=types.HttpOptions(
        timeout=45000
    )
)


MODEL_NAME = "gemini-3.5-flash"


# ============================================================
# GEMINI REQUEST
# ============================================================


def ask_gemini(
    prompt,
    max_retries=2
):

    for attempt in range(
        max_retries
    ):

        try:

            response = (
                client.models.generate_content(

                    model=MODEL_NAME,

                    contents=prompt,

                    config=types.GenerateContentConfig(

                        temperature=0.2,

                        max_output_tokens=1800,

                        response_mime_type=(
                            "application/json"
                        ),

                        automatic_function_calling=(
                            types.AutomaticFunctionCallingConfig(
                                disable=True
                            )
                        )
                    )
                )
            )

            return response.text

        except Exception as exc:

            error_text = str(
                exc
            )

            retryable_errors = [

                "503",

                "UNAVAILABLE",

                "429",

                "RESOURCE_EXHAUSTED",

                "timeout",

                "timed out",
            ]

            retryable = any(

                error in error_text

                for error in
                retryable_errors
            )

            if (
                retryable
                and
                attempt < max_retries - 1
            ):

                wait_time = 2 ** attempt

                print(
                    "Gemini temporarily unavailable."
                    f" Retrying in {wait_time}s..."
                )

                time.sleep(
                    wait_time
                )

            else:

                raise


# ============================================================
# JSON EXTRACTION
# ============================================================


def extract_json(
    text
):

    if not text:

        raise ValueError(
            "Gemini returned an empty response."
        )

    text = text.strip()

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

    try:

        return json.loads(
            text
        )

    except json.JSONDecodeError:

        pass

    start = text.find(
        "{"
    )

    end = text.rfind(
        "}"
    )

    if (
        start != -1
        and
        end != -1
    ):

        json_text = text[
            start:end + 1
        ]

        return json.loads(
            json_text
        )

    raise ValueError(
        "No valid JSON object found."
    )


# ============================================================
# RAG EVIDENCE
# ============================================================


def format_evidence(
    evidence
):

    if not evidence:

        return (
            "No scientific evidence was retrieved."
        )

    formatted = []

    for i, item in enumerate(
        evidence[:5],
        start=1
    ):

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

        text = str(
            text
        )[:900]

        formatted.append(

            f"""
Evidence {i}
Source: {source}
Page: {page}
Content:
{text}
"""
        )

    return "\n".join(
        formatted
    )


# ============================================================
# CHAT HISTORY
# ============================================================


def format_chat_history_for_prompt(
    chat_history
):

    if not chat_history:

        return (
            "No previous conversation."
        )

    lines = []

    for message in chat_history[-6:]:

        if isinstance(
            message,
            dict
        ):

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

    return "\n".join(
        lines
    )


# ============================================================
# GBIF SUMMARY
# ============================================================


def summarize_gbif_data(
    gbif_data
):

    if not gbif_data:

        return {
            "available": False
        }

    return {

        "available":
            gbif_data.get(
                "available",
                False
            ),

        "source":
            gbif_data.get(
                "source",
                "GBIF"
            ),

        "latitude":
            gbif_data.get(
                "latitude"
            ),

        "longitude":
            gbif_data.get(
                "longitude"
            ),

        "radius_km":
            gbif_data.get(
                "radius_km"
            ),

        "record_count":
            gbif_data.get(
                "record_count",
                0
            ),

        "returned_records":
            gbif_data.get(
                "returned_records",
                0
            ),

        "observed_taxa_count":
            gbif_data.get(
                "observed_taxa_count",
                0
            ),

        "observed_taxa":
            gbif_data.get(
                "observed_taxa",
                []
            )[:12]
    }


# ============================================================
# FALLBACK
# ============================================================


def build_fallback_response(
    analysis,
    evidence,
    error_message
):

    interactions = []

    for item in analysis.get(
        "interactions",
        []
    ):

        if isinstance(
            item,
            dict
        ):

            interactions.append({

                "interaction":
                    ", ".join(
                        item.get(
                            "variables",
                            []
                        )
                    ),

                "reasoning":
                    item.get(
                        "reasoning",
                        ""
                    )
            })

    recommendations = []

    for item in analysis.get(
        "recommendations",
        []
    ):

        recommendations.append({

            "action":
                item,

            "why_it_works":
                (
                    "This recommendation is based "
                    "on the environmental reasoning layer "
                    "and the retrieved scientific evidence."
                ),

            "impacted_metrics":
                analysis.get(
                    "impacted_metrics",
                    []
                ),

            "time_horizon":
                "Context dependent",

            "confidence":
                "Moderate"
        })

    scientific_evidence = []

    for item in evidence[:3]:

        scientific_evidence.append({

            "source":
                item.get(
                    "source",
                    "Unknown"
                ),

            "page":
                item.get(
                    "page",
                    "Unknown"
                ),

            "evidence":
                str(
                    item.get(
                        "text",
                        ""
                    )
                )[:900]
        })

    return {

        "assessment":
            analysis.get(
                "overall_assessment",
                "Environmental assessment completed."
            ),

        "key_interactions":
            interactions,

        "recommendations":
            recommendations,

        "scientific_evidence":
            scientific_evidence,

        "data_limitations": [

            "Gemini was unavailable for this request.",

            str(
                error_message
            )
        ]
    }


# ============================================================
# MAIN RESPONSE GENERATOR
# ============================================================


def generate_biodiversity_response(

    profile,

    analysis,

    evidence,

    user_question=None,

    chat_history=None,

    gbif_data=None,

    knowledge_context=None

):

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

    evidence_text = (
        format_evidence(
            evidence
        )
    )

    history_text = (
        format_chat_history_for_prompt(
            chat_history
        )
    )

    gbif_summary = (
        summarize_gbif_data(
            gbif_data
        )
    )

    gbif_text = json.dumps(

        gbif_summary,

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

        else
        "Provide an environmental biodiversity assessment."
    )

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are an AI Biodiversity Intelligence Assistant.

Analyze the supplied environmental profile and provide
scientifically grounded biodiversity recommendations.

USER QUESTION
{question_text}

STRUCTURED ENVIRONMENTAL PROFILE
{profile_text}

RULE-BASED ENVIRONMENTAL ANALYSIS
{analysis_text}

SCIENTIFIC RAG EVIDENCE
{evidence_text}

STRUCTURED ENVIRONMENTAL KNOWLEDGE
{knowledge_text}

GBIF LOCATION BIODIVERSITY SUMMARY
{gbif_text}

CONVERSATION HISTORY
{history_text}

REQUIREMENTS

1. Analyze the supplied environmental conditions.

2. Identify the most important environmental pressures.

3. Connect at least THREE environmental variables when
   the available data supports this.

4. Explain cause-and-effect relationships carefully.

5. Provide practical biodiversity interventions.

6. Each recommendation must contain:
   - action
   - why it works
   - impacted metrics
   - time horizon
   - confidence

7. Ground recommendations in the supplied scientific
   evidence whenever possible.

8. Never invent papers, authors, statistics, measurements,
   or citations.

9. Do not invent precise intervention impact numbers.

10. Clearly state important data limitations.

11. GBIF observations are supporting biodiversity context,
    not complete species richness.

12. Missing GBIF observations must not be interpreted as
    absence of species.

13. The structured dataset contains demonstration/reference
    records. Do not present it as complete real-world data.

14. Be concise enough for a web application.

Return ONLY valid JSON.

Use exactly:

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
"""

    # ========================================================
    # GEMINI CALL
    # ========================================================

    try:

        raw_response = ask_gemini(
            prompt,
            max_retries=2
        )

    except Exception as exc:

        print(
            "Gemini unavailable:",
            repr(exc)
        )

        return build_fallback_response(

            analysis,

            evidence,

            exc
        )

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        result = extract_json(
            raw_response
        )

    except Exception as exc:

        print(
            "Gemini JSON parsing failed:",
            repr(exc)
        )

        return {

            "assessment":
                raw_response,

            "key_interactions":
                [],

            "recommendations":
                [],

            "scientific_evidence":
                [],

            "data_limitations": [

                "Gemini returned a response that "
                "could not be parsed as structured JSON.",

                str(exc)
            ]
        }

    # ========================================================
    # ENSURE REQUIRED FIELDS
    # ========================================================

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


# ============================================================
# TEST
# ============================================================


if __name__ == "__main__":

    print(
        "Run this module through the main pipeline."
    )