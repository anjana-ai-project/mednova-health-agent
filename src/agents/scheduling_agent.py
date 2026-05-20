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
DB_PATH = str(ROOT / "src" / "database" / "scheduling.db")

def query_scheduling_db() -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def scheduling_agent(question: str) -> dict:
    """Answers appointment and scheduling queries using SQLite scheduling database."""
    appointments = query_scheduling_db()
    context = json.dumps(appointments, indent=2)
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are a scheduling assistant for MedNova Hospital Chennai. "
            "You have access to the doctor appointments database. "
            "Answer the user's question using only the provided appointment data. "
            "Be concise and accurate about doctor availability and appointment slots."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Scheduling database:\n\n{context}\n\nQuestion: {question}"
            }
        ]
    )
    return {
        "answer": response.content[0].text,
        "sources": ["scheduling.db"],
        "agent": "scheduling_agent"
    }

if __name__ == "__main__":
    result = scheduling_agent("What slots are available with Dr. Arun Menon?")
    print(result["answer"])
