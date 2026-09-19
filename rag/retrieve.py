from pathlib import Path
import os
import re

from functools import lru_cache

from pypdf import PdfReader


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

KNOWLEDGE_DIR = (
    PROJECT_ROOT / "knowledge_base"
)

CHROMA_DIR = (
    PROJECT_ROOT
    / "data"
    / "chroma_db"
)

COLLECTION_NAME = (
    "environmental_knowledge"
)

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200


# ============================================================
# DEPLOYMENT DETECTION
# ============================================================

IS_VERCEL = (
    os.getenv("VERCEL") == "1"
)

IS_RENDER = (
    os.getenv("RENDER") == "true"
    or
    os.getenv("RENDER") == "1"
)

IS_DEPLOYED = (
    IS_VERCEL
    or
    IS_RENDER
)


# ============================================================
# LOCAL CHROMA
# ============================================================

client = None

embedding_function = None


if not IS_DEPLOYED:

    import chromadb

    from chromadb.utils.embedding_functions import (
        DefaultEmbeddingFunction
    )

    embedding_function = (
        DefaultEmbeddingFunction()
    )

    CHROMA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    client = (
        chromadb.PersistentClient(
            path=str(
                CHROMA_DIR
            )
        )
    )


# ============================================================
# PDF EXTRACTION
# ============================================================


def extract_pdf_pages(
    pdf_path
):

    reader = PdfReader(
        str(pdf_path)
    )

    pages = []

    for page_number, page in enumerate(

        reader.pages,

        start=1
    ):

        try:

            text = (
                page.extract_text()
                or ""
            )

        except Exception as exc:

            print(

                f"Could not extract "
                f"page {page_number} "
                f"from {pdf_path.name}: "
                f"{exc}"
            )

            text = ""

        text = text.strip()

        if text:

            pages.append({

                "page":
                    page_number,

                "text":
                    text
            })

    return pages


# ============================================================
# CHUNKING
# ============================================================


def chunk_text(
    text,

    chunk_size=CHUNK_SIZE,

    overlap=CHUNK_OVERLAP
):

    if not text:

        return []

    chunks = []

    start = 0

    text_length = len(
        text
    )

    while start < text_length:

        end = min(

            start + chunk_size,

            text_length
        )

        chunk = (
            text[start:end]
            .strip()
        )

        if chunk:

            chunks.append(
                chunk
            )

        if end >= text_length:

            break

        start = (
            end - overlap
        )

        if start < 0:

            start = 0

    return chunks


# ============================================================
# LOAD SCIENTIFIC CHUNKS
#
# Cached for deployed requests.
# PDFs are parsed only once per running instance.
# ============================================================


@lru_cache(
    maxsize=1
)
def load_scientific_chunks():

    chunks = []

    if not KNOWLEDGE_DIR.exists():

        print(

            "Knowledge directory not found:",
            KNOWLEDGE_DIR
        )

        return chunks

    pdf_files = list(

        KNOWLEDGE_DIR.rglob(
            "*.pdf"
        )
    )

    print(

        f"Found {len(pdf_files)} "
        "scientific PDFs."
    )

    for pdf_path in pdf_files:

        print(

            f"Loading: "
            f"{pdf_path.name}"
        )

        pages = (
            extract_pdf_pages(
                pdf_path
            )
        )

        for page_data in pages:

            page_number = (
                page_data["page"]
            )

            page_chunks = (
                chunk_text(
                    page_data["text"]
                )
            )

            for chunk_number, chunk in enumerate(
                page_chunks
            ):

                chunks.append({

                    "text":
                        chunk,

                    "source":
                        pdf_path.name,

                    "source_path":
                        str(
                            pdf_path.relative_to(
                                PROJECT_ROOT
                            )
                        ),

                    "page":
                        page_number,

                    "chunk":
                        chunk_number
                })

    print(

        f"Loaded {len(chunks)} "
        "scientific chunks."
    )

    return chunks


# ============================================================
# KEYWORD SCORING
# ============================================================


def keyword_score(
    query,
    text
):

    query_words = set(

        re.findall(

            r"\b[a-zA-Z][a-zA-Z-]+\b",

            query.lower()
        )
    )

    text_words = set(

        re.findall(

            r"\b[a-zA-Z][a-zA-Z-]+\b",

            text.lower()
        )
    )

    if not query_words:

        return 0

    return len(

        query_words.intersection(
            text_words
        )
    )


# ============================================================
# DEPLOYED RETRIEVAL
# ============================================================


def retrieve_deployed_evidence(

    query,

    top_k=5
):

    chunks = (
        load_scientific_chunks()
    )

    if not chunks:

        print(
            "No scientific PDF chunks found."
        )

        return []

    scored = []

    for item in chunks:

        score = keyword_score(

            query,

            item["text"]
        )

        if score > 0:

            scored.append({

                **item,

                "_score":
                    score
            })

    scored.sort(

        key=lambda item:
            item["_score"],

        reverse=True
    )

    results = []

    for item in scored[:top_k]:

        results.append({

            "text":
                item["text"],

            "source":
                item["source"],

            "page":
                item["page"],

            "chunk":
                item["chunk"],

            "distance":
                None
        })

    print(

        f"Retrieved {len(results)} "
        "scientific evidence chunks."
    )

    return results


# ============================================================
# LOCAL CHROMA COLLECTION
# ============================================================


def get_local_collection():

    if client is None:

        raise RuntimeError(
            "Local Chroma client is not initialized."
        )

    try:

        return client.get_collection(

            name=COLLECTION_NAME,

            embedding_function=(
                embedding_function
            )
        )

    except Exception as exc:

        raise RuntimeError(

            "Knowledge base collection was not found. "
            "Run 'python rag/ingest.py' first "
            "when running locally."

        ) from exc


# ============================================================
# MAIN RETRIEVAL
# ============================================================


def retrieve_evidence(

    query,

    top_k=5
):

    if (
        not query
        or
        not query.strip()
    ):

        return []

    # --------------------------------------------------------
    # RENDER / VERCEL
    # --------------------------------------------------------

    if IS_DEPLOYED:

        return retrieve_deployed_evidence(

            query,

            top_k=top_k
        )

    # --------------------------------------------------------
    # LOCAL
    # --------------------------------------------------------

    collection = (
        get_local_collection()
    )

    results = collection.query(

        query_texts=[
            query
        ],

        n_results=top_k
    )

    documents = (
        results.get(
            "documents",
            [[]]
        )[0]
    )

    metadatas = (
        results.get(
            "metadatas",
            [[]]
        )[0]
    )

    distances = (
        results.get(
            "distances",
            [[]]
        )[0]
    )

    evidence = []

    for index, document in enumerate(
        documents
    ):

        metadata = (

            metadatas[index]

            if index <
            len(metadatas)

            else {}
        )

        distance = (

            distances[index]

            if index <
            len(distances)

            else None
        )

        evidence.append({

            "text":
                document,

            "source":
                metadata.get(
                    "source",
                    "Unknown source"
                ),

            "page":
                metadata.get(
                    "page",
                    "Unknown"
                ),

            "chunk":
                metadata.get(
                    "chunk",
                    "Unknown"
                ),

            "distance":
                distance
        })

    return evidence


# ============================================================
# TEST
# ============================================================


if __name__ == "__main__":

    query = (

        "How does soil organic carbon "
        "affect biodiversity and soil health?"
    )

    results = retrieve_evidence(

        query,

        top_k=5
    )

    print()

    print(
        "=" * 60
    )

    print(
        "RETRIEVAL TEST"
    )

    print(
        "=" * 60
    )

    for index, item in enumerate(

        results,

        start=1
    ):

        print()

        print(
            f"Result {index}"
        )

        print(
            "Source:",
            item["source"]
        )

        print(
            "Page:",
            item["page"]
        )

        print(
            "Text:",
            item["text"][:500],
            "..."
        )