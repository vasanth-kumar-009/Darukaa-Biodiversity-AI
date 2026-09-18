from pathlib import Path
import os

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from pypdf import PdfReader


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge_base"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "environmental_knowledge"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


# =========================================================
# EMBEDDING FUNCTION
# =========================================================

embedding_function = DefaultEmbeddingFunction()


# =========================================================
# VERCEL DETECTION
# =========================================================

IS_VERCEL = os.getenv("VERCEL") == "1"


# =========================================================
# CLIENT
# =========================================================

if IS_VERCEL:

    # -----------------------------------------------------
    # Vercel filesystem is read-only.
    # Use an in-memory Chroma client.
    # -----------------------------------------------------

    client = chromadb.Client()

else:

    # -----------------------------------------------------
    # Local development.
    # Use persistent Chroma database.
    # -----------------------------------------------------

    CHROMA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf_pages(pdf_path):
    """
    Extract text from all pages of a PDF.
    """

    reader = PdfReader(str(pdf_path))

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        try:
            text = page.extract_text() or ""

        except Exception as e:

            print(
                f"Warning: Could not extract "
                f"page {page_number} from "
                f"{pdf_path.name}: {e}"
            )

            text = ""

        text = text.strip()

        if text:

            pages.append({
                "page": page_number,
                "text": text
            })

    return pages


# =========================================================
# CHUNKING
# =========================================================

def chunk_text(
    text,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):
    """
    Split text into overlapping chunks.
    """

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


# =========================================================
# BUILD IN-MEMORY KNOWLEDGE BASE
# =========================================================

def build_in_memory_collection():

    print()
    print("=" * 60)
    print("BUILDING VERCEL IN-MEMORY KNOWLEDGE BASE")
    print("=" * 60)

    try:

        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_function
        )

        print(
            f"Existing collection found: "
            f"{collection.count()} chunks"
        )

        return collection

    except Exception:

        pass


    # -----------------------------------------------------
    # Create collection
    # -----------------------------------------------------

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={
            "description":
                "Scientific biodiversity and "
                "environmental knowledge"
        }
    )


    # -----------------------------------------------------
    # Find PDFs
    # -----------------------------------------------------

    pdf_files = list(
        KNOWLEDGE_DIR.rglob("*.pdf")
    )

    print(
        f"Found {len(pdf_files)} scientific PDFs."
    )


    documents = []
    metadatas = []
    ids = []


    # -----------------------------------------------------
    # Extract and chunk PDFs
    # -----------------------------------------------------

    for pdf_path in pdf_files:

        print(
            f"Loading: {pdf_path.name}"
        )

        pages = extract_pdf_pages(
            pdf_path
        )

        for page_data in pages:

            page_number = page_data["page"]

            chunks = chunk_text(
                page_data["text"]
            )

            for chunk_number, chunk in enumerate(
                chunks
            ):

                document_id = (
                    f"{pdf_path.stem}"
                    f"_page_{page_number}"
                    f"_chunk_{chunk_number}"
                )

                documents.append(chunk)

                metadatas.append({
                    "source": pdf_path.name,
                    "source_path": str(
                        pdf_path.relative_to(
                            PROJECT_ROOT
                        )
                    ),
                    "page": page_number,
                    "chunk": chunk_number
                })

                ids.append(document_id)


    # -----------------------------------------------------
    # Add documents
    # -----------------------------------------------------

    if documents:

        print(
            f"Creating {len(documents)} "
            f"knowledge chunks..."
        )

        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    print(
        f"Knowledge base ready: "
        f"{collection.count()} chunks"
    )

    return collection


# =========================================================
# GET COLLECTION
# =========================================================

def get_collection():

    if IS_VERCEL:

        return build_in_memory_collection()


    # -----------------------------------------------------
    # Local persistent collection
    # -----------------------------------------------------

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


# =========================================================
# RETRIEVE EVIDENCE
# =========================================================

def retrieve_evidence(
    query,
    top_k=8
):
    """
    Retrieve scientifically relevant evidence.

    Local:
        Uses persistent ChromaDB.

    Vercel:
        Uses an in-memory ChromaDB built from
        the bundled scientific PDFs.
    """

    if not query or not query.strip():

        return []


    collection = get_collection()


    # -----------------------------------------------------
    # Query Chroma
    # -----------------------------------------------------

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


    for index, document in enumerate(
        documents
    ):

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


# =========================================================
# TEST
# =========================================================

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
            f"Source   : "
            f"{item['source']}"
        )

        print(
            f"Page     : "
            f"{item['page']}"
        )

        print(
            f"Distance : "
            f"{item['distance']}"
        )

        print(
            f"Text     : "
            f"{item['text'][:500]}..."
        )