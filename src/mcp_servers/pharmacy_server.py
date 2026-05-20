import sqlite3
import os
from mcp.server.fastmcp import FastMCP

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/pharmacy.db")

mcp = FastMCP("MedNova Pharmacy Server")

@mcp.tool()
def get_medicine_by_id(medicine_id: str) -> dict:
    """Get medicine details by medicine ID"""
    conn = sqlite3.connect(DB_PATH)
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

@mcp.tool()
def get_medicines_by_category(category: str) -> list:
    """Get all medicines in a specific category"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines WHERE category LIKE ?", (f"%{category}%",))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"medicine_id": r[0], "name": r[1], "stock": r[3], "price": r[4]}
        for r in rows
    ]

@mcp.tool()
def check_medicine_stock(medicine_name: str) -> dict:
    """Check stock availability for a medicine by name"""
    conn = sqlite3.connect(DB_PATH)
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

@mcp.tool()
def get_low_stock_medicines() -> list:
    """Get all medicines with stock below 100 units"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines WHERE stock_quantity < 100")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"medicine_id": r[0], "name": r[1], "stock": r[3], "supplier": r[5]}
        for r in rows
    ]

if __name__ == "__main__":
    mcp.run()