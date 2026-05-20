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
DB_PATH = str(ROOT / "src" / "database" / "patient.db")

def query_patient_db(question: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def patient_agent(question: str) -> dict:
    """Answers patient-related queries using SQLite patient database."""
    patients = query_patient_db(question)

    context = json.dumps(patients, indent=2)

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are a hospital information assistant for MedNova Hospital Chennai. "
            "You have access to the patient database. "
            "Answer the user's question using only the provided patient data. "
            "Be concise and accurate. Protect patient privacy — share only what is asked."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Patient database:\n\n{context}\n\nQuestion: {question}"
            }
        ]
    )

    return {
        "answer": response.content[0].text,
        "sources": ["patient.db"],
        "agent": "patient_agent"
    }

if __name__ == "__main__":
    result = patient_agent("Which patients are in the Cardiology ward?")
    print(result["answer"])
