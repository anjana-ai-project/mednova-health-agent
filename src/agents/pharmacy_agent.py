from src.mcp_servers.mednova_server import (
    get_medicine_by_id,
    get_medicines_by_category,
    check_medicine_stock,
    get_low_stock_medicines,
)

DOMAIN = "pharmacy"
SOURCES = ["pharmacy.db"]

TOOLS = [
    {
        "name": "get_medicine_by_id",
        "description": "Get full medicine details (name, category, stock, price, supplier, expiry) by medicine ID like M001.",
        "input_schema": {
            "type": "object",
            "properties": {
                "medicine_id": {"type": "string", "description": "Medicine ID, e.g. 'M001'"}
            },
            "required": ["medicine_id"]
        }
    },
    {
        "name": "get_medicines_by_category",
        "description": "List medicines in a category such as 'Antidiabetic', 'Antibiotic', 'Analgesic', 'Antihypertensive', 'Antacid', 'Statin', or 'Bronchodilator'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Medicine category"}
            },
            "required": ["category"]
        }
    },
    {
        "name": "check_medicine_stock",
        "description": "Check current stock quantity, price, expiry, and availability for a specific medicine by name (e.g. 'Insulin Glargine').",
        "input_schema": {
            "type": "object",
            "properties": {
                "medicine_name": {"type": "string", "description": "Medicine name or partial name"}
            },
            "required": ["medicine_name"]
        }
    },
    {
        "name": "get_low_stock_medicines",
        "description": "List all medicines with stock below 100 units — useful for restocking and shortage queries.",
        "input_schema": {"type": "object", "properties": {}}
    }
]

TOOL_FUNCTIONS = {
    "get_medicine_by_id": get_medicine_by_id,
    "get_medicines_by_category": get_medicines_by_category,
    "check_medicine_stock": check_medicine_stock,
    "get_low_stock_medicines": get_low_stock_medicines,
}


def dispatch(tool_name: str, tool_input: dict):
    """Execute one of this agent's tools and return the raw result."""
    return TOOL_FUNCTIONS[tool_name](**tool_input)
