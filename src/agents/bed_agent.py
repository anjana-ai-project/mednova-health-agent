from src.mcp_servers.mednova_server import (
    get_bed_status,
    get_available_beds,
    get_beds_by_ward,
    get_bed_occupancy_summary,
)

DOMAIN = "bed"
SOURCES = ["bed.db"]

TOOLS = [
    {
        "name": "get_bed_status",
        "description": "Get the status (Available/Occupied), ward, floor, and assigned patient of a bed by bed ID like B001.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bed_id": {"type": "string", "description": "Bed ID, e.g. 'B001'"}
            },
            "required": ["bed_id"]
        }
    },
    {
        "name": "get_available_beds",
        "description": "List every currently available (unoccupied) bed across the hospital, with ward and floor.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_beds_by_ward",
        "description": "List all beds in a given ward with their status and assigned patient.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ward": {"type": "string", "description": "Ward name, e.g. 'Cardiology'"}
            },
            "required": ["ward"]
        }
    },
    {
        "name": "get_bed_occupancy_summary",
        "description": "Hospital-wide bed occupancy summary: total beds, occupied count, available count, occupancy rate.",
        "input_schema": {"type": "object", "properties": {}}
    }
]

TOOL_FUNCTIONS = {
    "get_bed_status": get_bed_status,
    "get_available_beds": get_available_beds,
    "get_beds_by_ward": get_beds_by_ward,
    "get_bed_occupancy_summary": get_bed_occupancy_summary,
}


def dispatch(tool_name: str, tool_input: dict):
    """Execute one of this agent's tools and return the raw result."""
    return TOOL_FUNCTIONS[tool_name](**tool_input)
