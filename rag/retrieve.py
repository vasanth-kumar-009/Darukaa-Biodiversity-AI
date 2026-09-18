from pathlib import Path
import os
import re

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from pypdf import PdfReader


# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge_base"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "environmental_knowledge"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

IS_VERCEL = os.getenv("VERCEL") == "1"


# ==========================================================
# PDF EXTRACTION
# ==========================================================

def extract_pdf_pages(pdf_path):
    reader = PdfReader(str(pdf_path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        try:
            text = page.extract_text() or ""
        except Exception as e:
            print(
                f"Warning: Could not extract page "
                f"{page_number} from {pdf_path.name}: {e}"
            )
            text = ""

        text = text.strip()

        if text:
            pages.append({
                "page": page_number,
                "text": text
            })

    return pages


# ==========================================================
# CHUNKING
# ==========================================================

def chunk_text(
    text,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):

    if not text:
        return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

        if start < 0:
            start = 0

    return chunks


# ==========================================================
# LOAD SCIENTIFIC DOCUMENTS
# ==========================================================

def load_scientific_chunks():

    chunks = []

    pdf_files = list(
        KNOWLEDGE_DIR.rglob("*.pdf")
    )

    print(
        f"Found {len(pdf_files)} scientific PDFs."
    )

    for pdf_path in pdf_files:

        print(
            f"Loading scientific source: "
            f"{pdf_path.name}"
        )

        pages = extract_pdf_pages(pdf_path)

        for page_data in pages:

            page_number = page_data["page"]

            page_chunks = chunk_text(
                page_data["text"]
            )

            for chunk_number, chunk in enumerate(
                page_chunks
            ):

                chunks.append({
                    "text": chunk,
                    "source": pdf_path.name,
                    "page": page_number,
                    "chunk": chunk_number
                })

    print(
        f"Loaded {len(chunks)} scientific chunks."
    )

    return chunks


# ==========================================================
# SIMPLE VERCEL RETRIEVAL
# ==========================================================

def keyword_score(query, text):

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

    overlap = query_words.intersection(
        text_words
    )

    return len(overlap)


def retrieve_vercel_evidence(query, top_k=8):

    chunks = load_scientific_chunks()

    scored = []

    for item in chunks:

        score = keyword_score(
            query,
            item["text"]
        )

        if score > 0:

            scored.append({
                **item,
                "_score": score
            })

    scored.sort(
        key=lambda x: x["_score"],
        reverse=True
    )

    results = []

    for item in scored[:top_k]:

        results.append({
            "text": item["text"],
            "source": item["source"],
            "page": item["page"],
            "chunk": item["chunk"],
            "distance": None
        })

    return results


# ==========================================================
# LOCAL CHROMA
# ==========================================================

def get_local_collection():

    embedding_function = DefaultEmbeddingFunction()

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    try:

        return client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_function
        )

    except Exception as e:

        raise RuntimeError(
            "Knowledge base collection was not found. "
            "Run 'python rag/ingest.py' first."
        ) from e


# ==========================================================
# RETRIEVE EVIDENCE
# ==========================================================

def retrieve_evidence(query, top_k=8):

    if not query or not query.strip():
        return []

    # ------------------------------------------------------
    # VERCEL
    # ------------------------------------------------------

    if IS_VERCEL:

        print(
            "Vercel detected: "
            "using filesystem-safe scientific retrieval."
        )

        return retrieve_vercel_evidence(
            query,
            top_k=top_k
        )

    # ------------------------------------------------------
    # LOCAL
    # ------------------------------------------------------

    collection = get_local_collection()

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    evidence = []

    for index, document in enumerate(documents):

        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        distance = (
            distances[index]
            if index < len(distances)
            else None
        )

        evidence.append({
            "text": document,
            "source": metadata.get(
                "source",
                "Unknown source"
            ),
            "page": metadata.get(
                "page",
                "Unknown"
            ),
            "chunk": metadata.get(
                "chunk",
                "Unknown"
            ),
            "distance": distance
        })

    return evidence


# ==========================================================
# TEST
# ==========================================================

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
    print("=" * 60)
    print("RETRIEVAL TEST")
    print("=" * 60)

    for index, item in enumerate(
        results,
        start=1
    ):

        print()
        print(f"Result {index}")

        print(
            f"Source   : {item['source']}"
        )

        print(
            f"Page     : {item['page']}"
        )

        print(
            f"Distance : {item['distance']}"
        )

        print(
            f"Text     : "
            f"{item['text'][:500]}..."
        )