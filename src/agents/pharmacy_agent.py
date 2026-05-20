import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
import sqlite3
import anthropic

MODEL = "claude-haiku-4-5-20251001"
ROOT = Path(__file__).resolve().parents[2]
DB_PATH = str(ROOT / "src" / "database" / "pharmacy.db")

def query_pharmacy_db() -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def pharmacy_agent(question: str) -> dict:
    """Answers pharmacy and medicine queries using SQLite pharmacy database."""
    medicines = query_pharmacy_db()
    context = json.dumps(medicines, indent=2)
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are a pharmacy information assistant for MedNova Hospital Chennai. "
            "You have access to the pharmacy medicine database. "
            "Answer the user's question using only the provided medicine data. "
            "Be concise and accurate about stock, pricing, and availability."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Pharmacy database:\n\n{context}\n\nQuestion: {question}"
            }
        ]
    )
    return {
        "answer": response.content[0].text,
        "sources": ["pharmacy.db"],
        "agent": "pharmacy_agent"
    }

if __name__ == "__main__":
    result = pharmacy_agent("Which medicines are low on stock?")
    print(result["answer"])
