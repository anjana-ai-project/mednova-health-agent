import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "database"
PATIENT_DB = str(DB_DIR / "patient.db")
PHARMACY_DB = str(DB_DIR / "pharmacy.db")
BED_DB = str(DB_DIR / "bed.db")
SCHEDULING_DB = str(DB_DIR / "scheduling.db")


# ---------- Patient tools ----------

def get_patient_by_id(patient_id: str) -> dict:
    """Get patient details by patient ID"""
    conn = sqlite3.connect(PATIENT_DB)
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


def get_all_patients() -> list:
    """Get all current patients"""
    conn = sqlite3.connect(PATIENT_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id, name, disease, attending_doctor, ward FROM patients")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"patient_id": r[0], "name": r[1], "disease": r[2], "doctor": r[3], "ward": r[4]}
        for r in rows
    ]


def get_patients_by_doctor(doctor_name: str) -> list:
    """Get all patients under a specific doctor"""
    conn = sqlite3.connect(PATIENT_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE attending_doctor LIKE ?", (f"%{doctor_name}%",))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"patient_id": r[0], "name": r[1], "disease": r[3], "ward": r[7]}
        for r in rows
    ]


def get_patients_by_ward(ward: str) -> list:
    """Get all patients in a specific ward"""
    conn = sqlite3.connect(PATIENT_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE ward = ?", (ward,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"patient_id": r[0], "name": r[1], "disease": r[3], "doctor": r[6]}
        for r in rows
    ]


# ---------- Pharmacy tools ----------

def get_medicine_by_id(medicine_id: str) -> dict:
    """Get medicine details by medicine ID"""
    conn = sqlite3.connect(PHARMACY_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines WHERE medicine_id = ?", (medicine_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "medicine_id": row[0],
            "name": row[1],
            "category": row[2],
            "stock_quantity": row[3],
            "price": row[4],
            "supplier": row[5],
            "expiry_date": row[6]
        }
    return {"error": f"Medicine {medicine_id} not found"}


def get_medicines_by_category(category: str) -> list:
    """Get all medicines in a specific category"""
    conn = sqlite3.connect(PHARMACY_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines WHERE category LIKE ?", (f"%{category}%",))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"medicine_id": r[0], "name": r[1], "stock": r[3], "price": r[4]}
        for r in rows
    ]


def check_medicine_stock(medicine_name: str) -> dict:
    """Check stock availability for a medicine by name"""
    conn = sqlite3.connect(PHARMACY_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines WHERE name LIKE ?", (f"%{medicine_name}%",))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "name": row[1],
            "stock_quantity": row[3],
            "price": row[4],
            "expiry_date": row[6],
            "available": row[3] > 0
        }
    return {"error": f"Medicine {medicine_name} not found"}


def get_low_stock_medicines() -> list:
    """Get all medicines with stock below 100 units"""
    conn = sqlite3.connect(PHARMACY_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines WHERE stock_quantity < 100")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"medicine_id": r[0], "name": r[1], "stock": r[3], "supplier": r[5]}
        for r in rows
    ]


# ---------- Bed tools ----------

def get_bed_status(bed_id: str) -> dict:
    """Get status of a specific bed by bed ID"""
    conn = sqlite3.connect(BED_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM beds WHERE bed_id = ?", (bed_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "bed_id": row[0],
            "ward": row[1],
            "bed_number": row[2],
            "status": row[3],
            "patient_id": row[4],
            "floor": row[5]
        }
    return {"error": f"Bed {bed_id} not found"}


def get_available_beds() -> list:
    """Get all currently available beds"""
    conn = sqlite3.connect(BED_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM beds WHERE status = 'Available'")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"bed_id": r[0], "ward": r[1], "bed_number": r[2], "floor": r[5]}
        for r in rows
    ]


def get_beds_by_ward(ward: str) -> list:
    """Get all beds in a specific ward"""
    conn = sqlite3.connect(BED_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM beds WHERE ward = ?", (ward,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"bed_id": r[0], "bed_number": r[2], "status": r[3], "patient_id": r[4]}
        for r in rows
    ]


def get_bed_occupancy_summary() -> dict:
    """Get total occupied vs available beds across MedNova"""
    conn = sqlite3.connect(BED_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM beds GROUP BY status")
    rows = cursor.fetchall()
    conn.close()
    summary = {row[0]: row[1] for row in rows}
    total = sum(summary.values())
    return {
        "total_beds": total,
        "occupied": summary.get("Occupied", 0),
        "available": summary.get("Available", 0),
        "occupancy_rate": f"{(summary.get('Occupied', 0) / total * 100):.1f}%"
    }


# ---------- Scheduling tools ----------

def get_appointment_by_id(appointment_id: str) -> dict:
    """Get appointment details by appointment ID"""
    conn = sqlite3.connect(SCHEDULING_DB)
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


def get_appointments_by_doctor(doctor_name: str) -> list:
    """Get all appointments for a specific doctor"""
    conn = sqlite3.connect(SCHEDULING_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE doctor_name LIKE ?", (f"%{doctor_name}%",))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"appointment_id": r[0], "patient": r[1], "date": r[4], "time": r[5], "status": r[6]}
        for r in rows
    ]


def get_appointments_by_date(appointment_date: str) -> list:
    """Get all appointments on a specific date"""
    conn = sqlite3.connect(SCHEDULING_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE appointment_date = ?", (appointment_date,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"appointment_id": r[0], "patient": r[1], "doctor": r[2], "time": r[5], "status": r[6]}
        for r in rows
    ]


def get_available_slots() -> list:
    """Get all available appointment slots"""
    conn = sqlite3.connect(SCHEDULING_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE status = 'Available'")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"appointment_id": r[0], "doctor": r[2], "specialization": r[3], "date": r[4], "time": r[5]}
        for r in rows
    ]


def get_appointments_by_patient(patient_name: str) -> list:
    """Get all appointments for a specific patient"""
    conn = sqlite3.connect(SCHEDULING_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE patient_name LIKE ?", (f"%{patient_name}%",))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"appointment_id": r[0], "doctor": r[2], "date": r[4], "time": r[5], "status": r[6]}
        for r in rows
    ]
