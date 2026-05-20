import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import anthropic
from typing import TypedDict
from langgraph.graph import StateGraph, END

from src.agents.rag_agent import rag_agent
from src.agents.patient_agent import patient_agent
from src.agents.pharmacy_agent import pharmacy_agent
from src.agents.bed_agent import bed_agent
from src.agents.scheduling_agent import scheduling_agent

MODEL = "claude-haiku-4-5-20251001"

class MedNovaState(TypedDict):
    question: str
    agent_route: str
    answer: str
    sources: list
    eval_scores: dict

def route_question(state: MedNovaState) -> MedNovaState:
    """Uses Claude Haiku to classify the question and route to the correct agent."""
    question = state["question"]
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=20,
        system=(
            "You are a router for MedNova Hospital Chennai AI system. "
            "Classify the user question into exactly one of these categories: "
            "pharmacy, bed, scheduling, patient, rag. "
            "pharmacy — medicine, drug, stock, prescription, price. "
            "bed — bed, ward, floor, available, occupancy. "
            "scheduling — appointment, schedule, doctor slot, booking. "
            "patient — patient details, admitted, discharge, age, disease. "
            "rag — policy, procedure, protocol, visiting hours, ICU, general hospital info. "
            "Reply with only the category word. Nothing else."
        ),
        messages=[{"role": "user", "content": question}]
    )
    route = response.content[0].text.strip().lower()
    if route not in ["pharmacy", "bed", "scheduling", "patient", "rag"]:
        route = "rag"
    print(f"Routed to: {route}")
    return {**state, "agent_route": route}

def run_rag_agent(state: MedNovaState) -> MedNovaState:
    result = rag_agent(state["question"])
    return {**state, "answer": result["answer"], "sources": result["sources"]}

def run_patient_agent(state: MedNovaState) -> MedNovaState:
    result = patient_agent(state["question"])
    return {**state, "answer": result["answer"], "sources": result["sources"]}

def run_pharmacy_agent(state: MedNovaState) -> MedNovaState:
    result = pharmacy_agent(state["question"])
    return {**state, "answer": result["answer"], "sources": result["sources"]}

def run_bed_agent(state: MedNovaState) -> MedNovaState:
    result = bed_agent(state["question"])
    return {**state, "answer": result["answer"], "sources": result["sources"]}

def run_scheduling_agent(state: MedNovaState) -> MedNovaState:
    result = scheduling_agent(state["question"])
    return {**state, "answer": result["answer"], "sources": result["sources"]}

def select_agent(state: MedNovaState) -> str:
    """Conditional edge — returns which agent node to run next."""
    return state["agent_route"]

def build_graph() -> StateGraph:
    graph = StateGraph(MedNovaState)
    graph.add_node("router", route_question)
    graph.add_node("rag", run_rag_agent)
    graph.add_node("patient", run_patient_agent)
    graph.add_node("pharmacy", run_pharmacy_agent)
    graph.add_node("bed", run_bed_agent)
    graph.add_node("scheduling", run_scheduling_agent)
    graph.set_entry_point("router")
    graph.add_conditional_edges("router", select_agent, {
        "rag": "rag",
        "patient": "patient",
        "pharmacy": "pharmacy",
        "bed": "bed",
        "scheduling": "scheduling"
    })
    graph.add_edge("rag", END)
    graph.add_edge("patient", END)
    graph.add_edge("pharmacy", END)
    graph.add_edge("bed", END)
    graph.add_edge("scheduling", END)
    return graph.compile()

def ask(question: str) -> dict:
    """Main entry point — takes a question and returns answer."""
    graph = build_graph()
    result = graph.invoke({
        "question": question,
        "agent_route": "",
        "answer": "",
        "sources": [],
        "eval_scores": {}
    })
    return result

if __name__ == "__main__":
    questions = [
        "What are the ICU visiting hours?",
        "Which patients are in the Cardiology ward?",
        "Is Insulin Glargine available in pharmacy?",
        "Which beds are available right now?",
        "What appointments are available with Dr. Priya Nair?"
    ]
    for q in questions:
        print(f"\nQuestion: {q}")
        print("-" * 60)
        result = ask(q)
        print(result["answer"])
        print(f"Sources: {result['sources']}")
        print(f"Route: {result['agent_route']}")
