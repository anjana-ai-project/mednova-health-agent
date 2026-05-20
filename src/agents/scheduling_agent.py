from src.mcp_servers.mednova_server import (
    get_appointment_by_id,
    get_appointments_by_doctor,
    get_appointments_by_date,
    get_available_slots,
    get_appointments_by_patient,
)

DOMAIN = "scheduling"
SOURCES = ["scheduling.db"]

TOOLS = [
    {
        "name": "get_appointment_by_id",
        "description": "Get appointment details (patient, doctor, specialization, date, time, status) by appointment ID like A001.",
        "input_schema": {
            "type": "object",
            "properties": {
                "appointment_id": {"type": "string", "description": "Appointment ID, e.g. 'A001'"}
            },
            "required": ["appointment_id"]
        }
    },
    {
        "name": "get_appointments_by_doctor",
        "description": "List a doctor's appointments (patient, date, time, status).",
        "input_schema": {
            "type": "object",
            "properties": {
                "doctor_name": {"type": "string", "description": "Doctor's name, e.g. 'Priya Nair'"}
            },
            "required": ["doctor_name"]
        }
    },
    {
        "name": "get_appointments_by_date",
        "description": "List every appointment scheduled on a specific date (YYYY-MM-DD).",
        "input_schema": {
            "type": "object",
            "properties": {
                "appointment_date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
            },
            "required": ["appointment_date"]
        }
    },
    {
        "name": "get_available_slots",
        "description": "List every currently bookable appointment slot — doctor, specialization, date, time.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_appointments_by_patient",
        "description": "List a patient's appointments (upcoming or past) by patient name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "patient_name": {"type": "string", "description": "Patient name, e.g. 'Rajesh Kumar'"}
            },
            "required": ["patient_name"]
        }
    }
]

TOOL_FUNCTIONS = {
    "get_appointment_by_id": get_appointment_by_id,
    "get_appointments_by_doctor": get_appointments_by_doctor,
    "get_appointments_by_date": get_appointments_by_date,
    "get_available_slots": get_available_slots,
    "get_appointments_by_patient": get_appointments_by_patient,
}


def dispatch(tool_name: str, tool_input: dict):
    """Execute one of this agent's tools and return the raw result."""
    return TOOL_FUNCTIONS[tool_name](**tool_input)
