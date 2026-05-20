import sqlite3
import os
from mcp.server.fastmcp import FastMCP

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/patient.db")

mcp = FastMCP("MedNova Patient Server")

@mcp.tool()
def get_patient_by_id(patient_id: str) -> dict:
    """Get patient details by patient ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "patient_id": row[0],
            "name": row[1],
            "age": row[2],
            "disease": row[3],
            "admission_date": row[4],
            "discharge_date": row[5],
            "attending_doctor": row[6],
            "ward": row[7]
        }
    return {"error": f"Patient {patient_id} not found"}

@mcp.tool()
def get_all_patients() -> list:
    """Get all current patients"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id, name, disease, attending_doctor, ward FROM patients")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"patient_id": r[0], "name": r[1], "disease": r[2], "doctor": r[3], "ward": r[4]}
        for r in rows
    ]

@mcp.tool()
def get_patients_by_doctor(doctor_name: str) -> list:
    """Get all patients under a specific doctor"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE attending_doctor LIKE ?", (f"%{doctor_name}%",))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"patient_id": r[0], "name": r[1], "disease": r[3], "ward": r[7]}
        for r in rows
    ]

@mcp.tool()
def get_patients_by_ward(ward: str) -> list:
    """Get all patients in a specific ward"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE ward = ?", (ward,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"patient_id": r[0], "name": r[1], "disease": r[3], "doctor": r[6]}
        for r in rows
    ]

if __name__ == "__main__":
    mcp.run()