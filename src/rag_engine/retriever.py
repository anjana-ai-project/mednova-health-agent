from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = str(ROOT / "chroma_store")
TOP_K = 3

def retrieve(question: str, db_path: str = None, top_k: int = TOP_K) -> list:
    if db_path is None:
        db_path = DB_PATH

    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode(question).tolist()
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(name="documents")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    return [
        {
            "chunk": chunk,
            "source": (meta or {}).get("source", "unknown"),
            "distance": distance
        }
        for chunk, meta, distance in zip(documents, metadatas, distances)
    ]

if __name__ == "__main__":
    results = retrieve("ICU visiting hours at MedNova")
    for rank, r in enumerate(results, start=1):
        print(f"\n[{rank}] Source: {r['source']} (distance: {r['distance']:.4f})")
        print(r["chunk"])
        print("-" * 60)
