from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from pypdf import PdfReader


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge_base"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "environmental_knowledge"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
BATCH_SIZE = 32


# ---------------------------------------------------------
# Chroma client
# ---------------------------------------------------------

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)


embedding_function = DefaultEmbeddingFunction()


# ---------------------------------------------------------
# PDF extraction
# ---------------------------------------------------------

def extract_pdf_pages(pdf_path):
    """
    Extract text from every page of a PDF.
    """

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


# ---------------------------------------------------------
# Text chunking
# ---------------------------------------------------------

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Split text into overlapping chunks.
    """

    if not text:
        return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(start + chunk_size, text_length)

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

        if start < 0:
            start = 0

    return chunks


# ---------------------------------------------------------
# Build documents
# ---------------------------------------------------------

def build_documents():

    documents = []
    metadatas = []
    ids = []

    pdf_files = list(KNOWLEDGE_DIR.rglob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files.")

    document_id = 0

    for pdf_path in pdf_files:

        print(f"Processing: {pdf_path}")

        pages = extract_pdf_pages(pdf_path)

        for page_data in pages:

            page_number = page_data["page"]
            text = page_data["text"]

            chunks = chunk_text(text)

            for chunk_number, chunk in enumerate(chunks):

                document_id += 1

                doc_id = (
                    f"{pdf_path.stem}"
                    f"_page_{page_number}"
                    f"_chunk_{chunk_number}"
                )

                documents.append(chunk)

                metadatas.append({
                    "source": pdf_path.name,
                    "source_path": str(
                        pdf_path.relative_to(PROJECT_ROOT)
                    ),
                    "page": page_number,
                    "chunk": chunk_number
                })

                ids.append(doc_id)

    return documents, metadatas, ids


# ---------------------------------------------------------
# Main ingestion
# ---------------------------------------------------------

def ingest():

    print("=" * 60)
    print("DARUKAA.EARTH - KNOWLEDGE BASE INGESTION")
    print("=" * 60)

    CHROMA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Delete existing collection
    # -----------------------------------------------------

    try:
        client.delete_collection(
            name=COLLECTION_NAME
        )

        print("Existing collection deleted.")

    except Exception:
        print("No existing collection found.")

    # -----------------------------------------------------
    # Create collection
    # -----------------------------------------------------

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={
            "description": (
                "Scientific biodiversity and "
                "environmental knowledge"
            )
        }
    )

    # -----------------------------------------------------
    # Build documents
    # -----------------------------------------------------

    documents, metadatas, ids = build_documents()

    print(f"Total chunks created: {len(documents)}")

    # -----------------------------------------------------
    # Add documents in batches
    # -----------------------------------------------------

    for start in range(
        0,
        len(documents),
        BATCH_SIZE
    ):

        end = min(
            start + BATCH_SIZE,
            len(documents)
        )

        batch_documents = documents[start:end]
        batch_metadatas = metadatas[start:end]
        batch_ids = ids[start:end]

        collection.add(
            documents=batch_documents,
            metadatas=batch_metadatas,
            ids=batch_ids
        )

        print(
            f"Added chunks "
            f"{start + 1}-{end} "
            f"of {len(documents)}"
        )

    # -----------------------------------------------------
    # Verify
    # -----------------------------------------------------

    total = collection.count()

    print()
    print("=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"Collection : {COLLECTION_NAME}")
    print(f"Total chunks: {total}")
    print(f"Database   : {CHROMA_DIR}")


if __name__ == "__main__":
    ingest()