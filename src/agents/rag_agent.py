import sys
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import anthropic
from src.rag_engine.retriever import retrieve

MODEL = "claude-haiku-4-5-20251001"
ROOT = Path(__file__).resolve().parents[2]
DB_PATH = str(ROOT / "chroma_store")

def rag_agent(question: str) -> dict:
    """Answers clinical and policy questions using ChromaDB retrieval."""
    chunks = retrieve(question, db_path=DB_PATH, top_k=3)

    if not chunks:
        return {
            "answer": "I could not find relevant information in the MedNova documents.",
            "sources": [],
            "agent": "rag_agent"
        }

    context = "\n\n".join([
        f"[{i+1}] Source: {c['source']}\n{c['chunk']}"
        for i, c in enumerate(chunks)
    ])

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are a helpful medical information assistant for MedNova Hospital Chennai. "
            "Answer the user's question using only the provided context excerpts. "
            "Cite the source document when you use information from it. "
            "If the context does not contain enough information, say so clearly."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Context:\n\n{context}\n\nQuestion: {question}"
            }
        ]
    )

    sources = list(set([c["source"] for c in chunks]))

    return {
        "answer": response.content[0].text,
        "sources": sources,
        "agent": "rag_agent"
    }

if __name__ == "__main__":
    result = rag_agent("What are the ICU visiting hours at MedNova?")
    print(result["answer"])
    print("Sources:", result["sources"])
