import sqlite3
import os
from mcp.server.fastmcp import FastMCP

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/scheduling.db")

mcp = FastMCP("MedNova Scheduling Server")

@mcp.tool()
def get_appointment_by_id(appointment_id: str) -> dict:
    """Get appointment details by appointment ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE appointment_id = ?", (appointment_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "appointment_id": row[0],
            "patient_name": row[1],
            "doctor_name": row[2],
            "specialization": row[3],
            "appointment_date": row[4],
            "appointment_time": row[5],
            "status": row[6]
        }
    return {"error": f"Appointment {appointment_id} not found"}

@mcp.tool()
def get_appointments_by_doctor(doctor_name: str) -> list:
    """Get all appointments for a specific doctor"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE doctor_name LIKE ?", (f"%{doctor_name}%",))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"appointment_id": r[0], "patient": r[1], "date": r[4], "time": r[5], "status": r[6]}
        for r in rows
    ]

@mcp.tool()
def get_appointments_by_date(appointment_date: str) -> list:
    """Get all appointments on a specific date"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE appointment_date = ?", (appointment_date,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"appointment_id": r[0], "patient": r[1], "doctor": r[2], "time": r[5], "status": r[6]}
        for r in rows
    ]

@mcp.tool()
def get_available_slots() -> list:
    """Get all available appointment slots"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE status = 'Available'")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"appointment_id": r[0], "doctor": r[2], "specialization": r[3], "date": r[4], "time": r[5]}
        for r in rows
    ]

@mcp.tool()
def get_appointments_by_patient(patient_name: str) -> list:
    """Get all appointments for a specific patient"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE patient_name LIKE ?", (f"%{patient_name}%",))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"appointment_id": r[0], "doctor": r[2], "date": r[4], "time": r[5], "status": r[6]}
        for r in rows
    ]

if __name__ == "__main__":
    mcp.run()