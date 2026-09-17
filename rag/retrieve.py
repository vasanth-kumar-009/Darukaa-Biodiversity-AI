from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

CHROMA_DIR = Path("data/chroma_db")

COLLECTION_NAME = "environmental_knowledge"


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_collection(
    name=COLLECTION_NAME
)

print(
    f"Knowledge base contains {collection.count()} chunks."
)


# ============================================================
# SEARCH KNOWLEDGE BASE
# ============================================================

def search_knowledge(query, top_k=5):

    # Create embedding for user question
    query_embedding = embedding_model.encode(
        query
    ).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(query, results):

    print()
    print("=" * 70)
    print("USER QUERY")
    print("=" * 70)

    print(query)

    print()
    print("=" * 70)
    print("RETRIEVED SCIENTIFIC EVIDENCE")
    print("=" * 70)

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]

    for i, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1
    ):

        print()
        print(f"RESULT {i}")
        print("-" * 70)

        print("Source:", metadata["source"])
        print("Category:", metadata["category"])
        print("Page:", metadata["page"])
        print("Distance:", round(distance, 4))

        print()
        print(document)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    question = input(
        "\nEnter your environmental question: "
    )

    results = search_knowledge(
        question,
        top_k=5
    )

    display_results(
        question,
        results
    )