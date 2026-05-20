import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_DIR = os.path.join(os.path.dirname(__file__))

def create_patient_db():
    conn = sqlite3.connect(os.path.join(DB_DIR, "patient.db"))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            name TEXT,
            age INTEGER,
            disease TEXT,
            admission_date TEXT,
            discharge_date TEXT,
            attending_doctor TEXT,
            ward TEXT
        )
    ''')
    patients = [
        ("P001", "Rajesh Kumar", 45, "Type 2 Diabetes", "2026-05-01", None, "Dr. Priya Nair", "General"),
        ("P002", "Meena Sundaram", 62, "Hypertension", "2026-05-05", None, "Dr. Arun Menon", "Cardiology"),
        ("P003", "Suresh Babu", 38, "Appendicitis", "2026-05-10", "2026-05-14", "Dr. Kavitha Rajan", "Surgery"),
        ("P004", "Anitha Krishnan", 55, "Knee Replacement", "2026-05-12", None, "Dr. Suresh Iyer", "Orthopaedics"),
        ("P005", "Vikram Chandran", 29, "Dengue Fever", "2026-05-15", None, "Dr. Priya Nair", "General"),
        ("P006", "Lakshmi Patel", 70, "Cardiac Arrest", "2026-05-16", None, "Dr. Arun Menon", "Cardiology"),
        ("P007", "Karthik Raja", 41, "Kidney Stones", "2026-05-17", None, "Dr. Meera Pillai", "Urology"),
        ("P008", "Deepa Venkat", 33, "Asthma", "2026-05-18", None, "Dr. Priya Nair", "General"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO patients VALUES (?,?,?,?,?,?,?,?)", patients)
    conn.commit()
    conn.close()
    print("Patient DB created successfully")

def create_pharmacy_db():
    conn = sqlite3.connect(os.path.join(DB_DIR, "pharmacy.db"))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            medicine_id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            stock_quantity INTEGER,
            price REAL,
            supplier TEXT,
            expiry_date TEXT
        )
    ''')
    medicines = [
        ("M001", "Metformin 500mg", "Antidiabetic", 500, 2.50, "Sun Pharma", "2027-12-01"),
        ("M002", "Amlodipine 5mg", "Antihypertensive", 300, 3.75, "Cipla", "2027-08-01"),
        ("M003", "Paracetamol 650mg", "Analgesic", 1000, 1.20, "GSK", "2026-11-01"),
        ("M004", "Azithromycin 500mg", "Antibiotic", 200, 18.50, "Pfizer", "2027-03-01"),
        ("M005", "Pantoprazole 40mg", "Antacid", 450, 4.00, "Dr Reddys", "2027-06-01"),
        ("M006", "Insulin Glargine", "Antidiabetic", 80, 450.00, "Sanofi", "2026-09-01"),
        ("M007", "Atorvastatin 10mg", "Statin", 350, 6.50, "Cipla", "2027-10-01"),
        ("M008", "Salbutamol Inhaler", "Bronchodilator", 60, 120.00, "GSK", "2027-01-01"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO medicines VALUES (?,?,?,?,?,?,?)", medicines)
    conn.commit()
    conn.close()
    print("Pharmacy DB created successfully")

def create_bed_db():
    conn = sqlite3.connect(os.path.join(DB_DIR, "bed.db"))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS beds (
            bed_id TEXT PRIMARY KEY,
            ward TEXT,
            bed_number TEXT,
            status TEXT,
            patient_id TEXT,
            floor INTEGER
        )
    ''')
    beds = [
        ("B001", "General", "G-101", "Occupied", "P001", 1),
        ("B002", "General", "G-102", "Available", None, 1),
        ("B003", "General", "G-103", "Occupied", "P005", 1),
        ("B004", "Cardiology", "C-201", "Occupied", "P002", 2),
        ("B005", "Cardiology", "C-202", "Occupied", "P006", 2),
        ("B006", "Cardiology", "C-203", "Available", None, 2),
        ("B007", "Surgery", "S-301", "Available", None, 3),
        ("B008", "Orthopaedics", "O-401", "Occupied", "P004", 4),
        ("B009", "Urology", "U-501", "Occupied", "P007", 5),
        ("B010", "General", "G-104", "Occupied", "P008", 1),
    ]
    cursor.executemany("INSERT OR IGNORE INTO beds VALUES (?,?,?,?,?,?)", beds)
    conn.commit()
    conn.close()
    print("Bed DB created successfully")

def create_scheduling_db():
    conn = sqlite3.connect(os.path.join(DB_DIR, "scheduling.db"))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id TEXT PRIMARY KEY,
            patient_name TEXT,
            doctor_name TEXT,
            specialization TEXT,
            appointment_date TEXT,
            appointment_time TEXT,
            status TEXT
        )
    ''')
    appointments = [
        ("A001", "Rajesh Kumar", "Dr. Priya Nair", "General Medicine", "2026-05-21", "09:00 AM", "Confirmed"),
        ("A002", "Meena Sundaram", "Dr. Arun Menon", "Cardiology", "2026-05-21", "10:30 AM", "Confirmed"),
        ("A003", "Anitha Krishnan", "Dr. Suresh Iyer", "Orthopaedics", "2026-05-22", "11:00 AM", "Confirmed"),
        ("A004", "Vikram Chandran", "Dr. Priya Nair", "General Medicine", "2026-05-22", "02:00 PM", "Pending"),
        ("A005", "Deepa Venkat", "Dr. Priya Nair", "General Medicine", "2026-05-23", "09:30 AM", "Confirmed"),
        ("A006", "New Patient", "Dr. Arun Menon", "Cardiology", "2026-05-23", "03:00 PM", "Available"),
        ("A007", "Karthik Raja", "Dr. Meera Pillai", "Urology", "2026-05-24", "10:00 AM", "Confirmed"),
        ("A008", "New Patient", "Dr. Kavitha Rajan", "Surgery", "2026-05-24", "04:00 PM", "Available"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO appointments VALUES (?,?,?,?,?,?,?)", appointments)
    conn.commit()
    conn.close()
    print("Scheduling DB created successfully")

if __name__ == "__main__":
    create_patient_db()
    create_pharmacy_db()
    create_bed_db()
    create_scheduling_db()
    print("\nAll MedNova Hospital Chennai databases created successfully")