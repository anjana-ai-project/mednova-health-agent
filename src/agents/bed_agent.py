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
DB_PATH = str(ROOT / "src" / "database" / "bed.db")

def query_bed_db() -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM beds")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def bed_agent(question: str) -> dict:
    """Answers bed availability queries using SQLite bed database."""
    beds = query_bed_db()
    context = json.dumps(beds, indent=2)
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are a bed management assistant for MedNova Hospital Chennai. "
            "You have access to the bed availability database. "
            "Answer the user's question using only the provided bed data. "
            "Be concise and accurate about bed availability, ward, and floor."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Bed database:\n\n{context}\n\nQuestion: {question}"
            }
        ]
    )
    return {
        "answer": response.content[0].text,
        "sources": ["bed.db"],
        "agent": "bed_agent"
    }

if __name__ == "__main__":
    result = bed_agent("Which beds are available right now?")
    print(result["answer"])
