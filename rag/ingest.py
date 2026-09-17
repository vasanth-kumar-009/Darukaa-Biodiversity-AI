from pathlib import Path
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

KNOWLEDGE_DIR = Path("knowledge_base")
CHROMA_DIR = Path("data/chroma_db")

COLLECTION_NAME = "environmental_knowledge"

# Number of chunks processed at once
BATCH_SIZE = 32


# ============================================================
# EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# ============================================================
# CHROMADB
# ============================================================

print("Initializing ChromaDB...")

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)

print("ChromaDB ready.")


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(pdf_path):

    reader = PdfReader(str(pdf_path))

    pages = []

    for page_number, page in enumerate(reader.pages):

        text = page.extract_text()

        if text and text.strip():

            pages.append({
                "page": page_number + 1,
                "text": text.strip()
            })

    return pages


# ============================================================
# TEXT CHUNKING
# ============================================================

def create_chunks(text, chunk_size=1000, overlap=200):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:

            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ============================================================
# PROCESS PDF
# ============================================================

def process_pdf(pdf_path):

    print()
    print("=" * 60)
    print(f"Processing: {pdf_path}")
    print("=" * 60)

    pages = extract_pdf_text(pdf_path)

    print(f"Extracted {len(pages)} pages.")

    all_chunks = []

    for page in pages:

        chunks = create_chunks(page["text"])

        for chunk in chunks:

            all_chunks.append({
                "text": chunk,
                "page": page["page"]
            })

    print(f"Created {len(all_chunks)} chunks.")

    return all_chunks


# ============================================================
# BATCH INSERT
# ============================================================

def add_chunks_to_chromadb(chunks, pdf_path, start_id):

    total = len(chunks)

    for start in range(0, total, BATCH_SIZE):

        end = min(start + BATCH_SIZE, total)

        batch = chunks[start:end]

        texts = [
            item["text"]
            for item in batch
        ]

        # ----------------------------------------------------
        # Create embeddings for the entire batch
        # ----------------------------------------------------

        embeddings = embedding_model.encode(
            texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=False
        ).tolist()

        # ----------------------------------------------------
        # IDs
        # ----------------------------------------------------

        ids = [
            f"doc_{start_id + i}"
            for i in range(len(batch))
        ]

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        metadatas = []

        for item in batch:

            metadatas.append({
                "source": pdf_path.name,
                "category": pdf_path.parent.name,
                "page": item["page"]
            })

        # ----------------------------------------------------
        # Add batch to ChromaDB
        # ----------------------------------------------------

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        print(
            f"Added {end}/{total} chunks "
            f"from {pdf_path.name}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("DARUKAA BIODIVERSITY AI")
    print("Knowledge Base Ingestion")
    print("=" * 60)

    pdf_files = list(
        KNOWLEDGE_DIR.rglob("*.pdf")
    )

    print()
    print(f"Found {len(pdf_files)} PDF files.")

    if not pdf_files:

        print()
        print("ERROR: No PDF files found.")
        print("Put your PDFs inside the knowledge_base folder.")
        return

    # --------------------------------------------------------
    # IMPORTANT:
    # Start fresh every time we run ingestion.
    # --------------------------------------------------------

    try:

        client.delete_collection(
            name=COLLECTION_NAME
        )

        print("Old collection deleted.")

    except Exception:

        print("No previous collection found.")

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    # Make collection globally available
    globals()["collection"] = collection

    # --------------------------------------------------------
    # Process every PDF
    # --------------------------------------------------------

    document_id = 0

    for pdf_path in pdf_files:

        chunks = process_pdf(pdf_path)

        add_chunks_to_chromadb(
            chunks,
            pdf_path,
            document_id
        )

        document_id += len(chunks)

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("KNOWLEDGE BASE CREATED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"Total chunks stored: {collection.count()}"
    )

    print(
        f"Database location: {CHROMA_DIR}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()