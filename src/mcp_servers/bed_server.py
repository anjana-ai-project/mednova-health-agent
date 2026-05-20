import sqlite3
import os
from mcp.server.fastmcp import FastMCP

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/bed.db")

mcp = FastMCP("MedNova Bed Server")

@mcp.tool()
def get_bed_status(bed_id: str) -> dict:
    """Get status of a specific bed by bed ID"""
    conn = sqlite3.connect(DB_PATH)
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

@mcp.tool()
def get_available_beds() -> list:
    """Get all currently available beds"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM beds WHERE status = 'Available'")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"bed_id": r[0], "ward": r[1], "bed_number": r[2], "floor": r[5]}
        for r in rows
    ]

@mcp.tool()
def get_beds_by_ward(ward: str) -> list:
    """Get all beds in a specific ward"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM beds WHERE ward = ?", (ward,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"bed_id": r[0], "bed_number": r[2], "status": r[3], "patient_id": r[4]}
        for r in rows
    ]

@mcp.tool()
def get_bed_occupancy_summary() -> dict:
    """Get total occupied vs available beds across MedNova"""
    conn = sqlite3.connect(DB_PATH)
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

if __name__ == "__main__":
    mcp.run()