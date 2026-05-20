from dotenv import load_dotenv
load_dotenv()

import anthropic
from sentence_transformers import SentenceTransformer
import chromadb

DB_PATH = "data/chromadb"
TOP_K = 3
MODEL = "claude-haiku-4-5-20251001"


def retrieve_chunks(question: str, db_path: str = DB_PATH, top_k: int = TOP_K) -> list[dict]:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode(question).tolist()

    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_collection(name="documents")

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"],
    )

    chunks = []
    for text, meta in zip(results["documents"][0], results["metadatas"][0]):
        meta = meta if meta else {}
        chunks.append({"text": text, "source": meta.get("source", "unknown")})

    return chunks


def build_prompt_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f"[{i}] Source: {chunk['source']}\n{chunk['text']}")
    return "\n\n".join(parts)


def ask_claude(question: str, chunks: list[dict]) -> str:
    context = build_prompt_context(chunks)

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are a helpful medical information assistant. "
            "Answer the user's question using only the provided context excerpts. "
            "Cite the source document name (e.g. 'According to <filename>...') "
            "when you use information from it. "
            "If the context does not contain enough information to answer, say so."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Context excerpts:\n\n{context}\n\nQuestion: {question}",
            }
        ],
    )

    return response.content[0].text


def main() -> None:
    question = input("Enter your question: ").strip()
    if not question:
        question = "What is the ICU discharge procedure at Apollo Hospitals?"
        print(f"Using default question: {question}")

    print(f"\nRetrieving top {TOP_K} relevant chunks...\n" + "-" * 60)
    chunks = retrieve_chunks(question)

    for i, chunk in enumerate(chunks, start=1):
        print(f"\n[{i}] Source: {chunk['source']}")
        print(chunk["text"])

    print("\n" + "=" * 60)
    print("Sending to Claude...\n")
    answer = ask_claude(question, chunks)

    print("Answer:")
    print("=" * 60)
    print(answer)

    unique_sources = list(dict.fromkeys(c["source"] for c in chunks))
    print("\nSources:")
    for source in unique_sources:
        print(f"  - {source}")


if __name__ == "__main__":
    main()
