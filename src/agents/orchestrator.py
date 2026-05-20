import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import anthropic
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

from src.agents.rag_agent import rag_agent
from src.agents.patient_agent import patient_agent
from src.agents.pharmacy_agent import pharmacy_agent
from src.agents.bed_agent import bed_agent
from src.agents.scheduling_agent import scheduling_agent

MODEL = "claude-haiku-4-5-20251001"

class MedNovaState(TypedDict):
    messages: Annotated[list, add_messages]
    question: str
    agent_route: str
    answer: str
    sources: list
    eval_scores: dict

def route_question(state: MedNovaState) -> MedNovaState:
    question = state["question"]
    history = state.get("messages", [])

    history_text = ""
    if history:
        history_text = "\n".join([
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in history[-6:]
        ])

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
            "Use the conversation history to understand follow-up messages like yes, no, book it, confirm. "
            "Reply with only the category word. Nothing else."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Conversation history:\n{history_text}\n\nCurrent message: {question}"
            }
        ]
    )
    route = response.content[0].text.strip().lower()
    if route not in ["pharmacy", "bed", "scheduling", "patient", "rag"]:
        route = "rag"
    print(f"Routed to: {route}")
    return {**state, "agent_route": route}

def build_agent_prompt(question: str, state: MedNovaState) -> str:
    history = state.get("messages", [])
    if not history:
        return question
    history_text = "\n".join([
        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
        for m in history[-6:]
    ])
    return f"Conversation history:\n{history_text}\n\nCurrent question: {question}"

def run_rag_agent(state: MedNovaState) -> MedNovaState:
    prompt = build_agent_prompt(state["question"], state)
    result = rag_agent(prompt)
    return {**state, "answer": result["answer"], "sources": result["sources"],
            "messages": [AIMessage(content=result["answer"])]}

def run_patient_agent(state: MedNovaState) -> MedNovaState:
    prompt = build_agent_prompt(state["question"], state)
    result = patient_agent(prompt)
    return {**state, "answer": result["answer"], "sources": result["sources"],
            "messages": [AIMessage(content=result["answer"])]}

def run_pharmacy_agent(state: MedNovaState) -> MedNovaState:
    prompt = build_agent_prompt(state["question"], state)
    result = pharmacy_agent(prompt)
    return {**state, "answer": result["answer"], "sources": result["sources"],
            "messages": [AIMessage(content=result["answer"])]}

def run_bed_agent(state: MedNovaState) -> MedNovaState:
    prompt = build_agent_prompt(state["question"], state)
    result = bed_agent(prompt)
    return {**state, "answer": result["answer"], "sources": result["sources"],
            "messages": [AIMessage(content=result["answer"])]}

def run_scheduling_agent(state: MedNovaState) -> MedNovaState:
    prompt = build_agent_prompt(state["question"], state)
    result = scheduling_agent(prompt)
    return {**state, "answer": result["answer"], "sources": result["sources"],
            "messages": [AIMessage(content=result["answer"])]}

def select_agent(state: MedNovaState) -> str:
    return state["agent_route"]

memory = MemorySaver()

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
    return graph.compile(checkpointer=memory)

graph = build_graph()

def ask(question: str, thread_id: str = "default") -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(
        {
            "question": question,
            "agent_route": "",
            "answer": "",
            "sources": [],
            "eval_scores": {},
            "messages": [HumanMessage(content=question)]
        },
        config=config
    )
    return result
