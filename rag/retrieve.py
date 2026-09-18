from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "environmental_knowledge"


# ---------------------------------------------------------
# Chroma client
# ---------------------------------------------------------

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

embedding_function = DefaultEmbeddingFunction()


# ---------------------------------------------------------
# Collection
# ---------------------------------------------------------

def get_collection():

    try:

        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_function
        )

        return collection

    except Exception as e:

        raise RuntimeError(
            "Knowledge base collection was not found. "
            "Run 'python rag/ingest.py' first."
        ) from e


# ---------------------------------------------------------
# Retrieve evidence
# ---------------------------------------------------------

def retrieve_evidence(
    query,
    top_k=8
):
    """
    Retrieve the most relevant scientific knowledge
    from ChromaDB using semantic similarity.
    """

    if not query or not query.strip():
        return []

    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

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


# ---------------------------------------------------------
# Simple test
# ---------------------------------------------------------

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
        print(f"Source   : {item['source']}")
        print(f"Page     : {item['page']}")
        print(f"Distance : {item['distance']}")
        print(f"Text     : {item['text'][:500]}...")