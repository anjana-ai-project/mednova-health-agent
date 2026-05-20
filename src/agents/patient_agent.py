from src.mcp_servers.mednova_server import (
    get_patient_by_id,
    get_all_patients,
    get_patients_by_doctor,
    get_patients_by_ward,
)

DOMAIN = "patient"
SOURCES = ["patient.db"]

TOOLS = [
    {
        "name": "get_patient_by_id",
        "description": "Get full patient details (name, age, disease, attending doctor, ward, admission/discharge dates) by patient ID like P001.",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_id": {"type": "string", "description": "Patient ID, e.g. 'P001'"}
            },
            "required": ["patient_id"]
        }
    },
    {
        "name": "get_all_patients",
        "description": "List every currently admitted patient with disease, attending doctor, and ward.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_patients_by_doctor",
        "description": "List patients under a specific attending doctor's care.",
        "input_schema": {
            "type": "object",
            "properties": {
                "doctor_name": {"type": "string", "description": "Doctor's name, e.g. 'Priya Nair' or 'Dr. Arun Menon'"}
            },
            "required": ["doctor_name"]
        }
    },
    {
        "name": "get_patients_by_ward",
        "description": "List all patients in a specific ward (e.g. 'Cardiology', 'General', 'Surgery', 'Orthopaedics', 'Urology').",
        "input_schema": {
            "type": "object",
            "properties": {
                "ward": {"type": "string", "description": "Ward name"}
            },
            "required": ["ward"]
        }
    }
]

TOOL_FUNCTIONS = {
    "get_patient_by_id": get_patient_by_id,
    "get_all_patients": get_all_patients,
    "get_patients_by_doctor": get_patients_by_doctor,
    "get_patients_by_ward": get_patients_by_ward,
}


def dispatch(tool_name: str, tool_input: dict):
    """Execute one of this agent's tools and return the raw result."""
    return TOOL_FUNCTIONS[tool_name](**tool_input)
