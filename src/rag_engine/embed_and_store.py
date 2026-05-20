import shutil
from pathlib import Path

from sentence_transformers import SentenceTransformer
import chromadb

from document_loader import load_and_split_documents


def embed_and_store(documents_dir: str = None, db_path: str = None) -> None:
    root = Path(__file__).resolve().parents[2]
    if documents_dir is None:
        documents_dir = str(root / "data")
    if db_path is None:
        db_path = str(root / "chroma_store")    # Wipe existing ChromaDB so metadata is always fresh
    db_dir = Path(db_path)
    if db_dir.exists():
        shutil.rmtree(db_dir)
        print(f"Deleted existing ChromaDB at '{db_path}'")
    db_dir.mkdir(parents=True, exist_ok=True)

    chunks, sources = load_and_split_documents(documents_dir)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks, show_progress_bar=True)

    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="documents")

    ids = [str(i) for i in range(len(chunks))]
    metadatas = [{"source": source} for source in sources]
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )

    # Verify metadata was stored correctly on the first chunk
    sample = collection.get(ids=["0"], include=["metadatas"])
    print(f"Sample metadata check — chunk 0: {sample['metadatas'][0]}")

    print(f"\nStored {collection.count()} vectors in ChromaDB at '{db_path}'")


if __name__ == "__main__":
    embed_and_store()
