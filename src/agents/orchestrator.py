import sys
import json
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

from src.agents import patient_agent, pharmacy_agent, bed_agent, scheduling_agent
from src.rag_engine.retriever import retrieve

MODEL = "claude-haiku-4-5-20251001"


SEARCH_DOCUMENTS_TOOL = {
    "name": "search_documents",
    "description": (
        "Retrieve relevant excerpts from MedNova policy and procedure documents. "
        "Use for questions about hospital policies, ICU procedures, visiting hours, "
        "patient services, pharmacy services, or any general hospital information "
        "that is NOT a structured database lookup."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query — typically the user's question"}
        },
        "required": ["query"]
    }
}

_AGENT_MODULES = [patient_agent, pharmacy_agent, bed_agent, scheduling_agent]

TOOL_REGISTRY: dict = {}
for _agent in _AGENT_MODULES:
    for _tool in _agent.TOOLS:
        TOOL_REGISTRY[_tool["name"]] = {
            "dispatch": _agent.dispatch,
            "domain": _agent.DOMAIN,
            "sources": _agent.SOURCES,
        }

ALL_TOOLS = [SEARCH_DOCUMENTS_TOOL]
for _agent in _AGENT_MODULES:
    ALL_TOOLS.extend(_agent.TOOLS)


def _execute_tool(tool_name: str, tool_input: dict):
    """Run the selected tool and return (result, sources, agent_route)."""
    if tool_name == "search_documents":
        chunks = retrieve(tool_input.get("query", ""))
        sources = sorted({c["source"] for c in chunks})
        return chunks, sources, "rag"
    entry = TOOL_REGISTRY.get(tool_name)
    if entry is None:
        return {"error": f"Unknown tool '{tool_name}'"}, [], "rag"
    return entry["dispatch"](tool_name, tool_input), list(entry["sources"]), entry["domain"]


def _history_text(messages: list) -> str:
    if not messages:
        return ""
    prior = messages[:-1] if isinstance(messages[-1], HumanMessage) else messages
    if not prior:
        return ""
    lines = []
    for m in prior[-6:]:
        role = "User" if isinstance(m, HumanMessage) else "Assistant"
        lines.append(f"{role}: {m.content}")
    return "\n".join(lines)


class MedNovaState(TypedDict):
    messages: Annotated[list, add_messages]
    question: str
    agent_route: str
    answer: str
    sources: list
    eval_scores: dict
    tool_name: str
    tool_input: dict


def run_turn(state: MedNovaState) -> MedNovaState:
    """Single LangGraph node: pick tool, execute, formulate answer."""
    question = state["question"]
    history = _history_text(state.get("messages", []))
    client = anthropic.Anthropic()

    pick_response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        tools=ALL_TOOLS,
        tool_choice={"type": "auto"},
        system=(
            "You are the routing brain for MedNova Hospital Chennai's AI assistant. "
            "Given the user's current message and the recent conversation history, "
            "select exactly one tool and extract its parameters. "
            "Use search_documents for policy / procedure / visiting-hours / ICU-protocol / "
            "general hospital-info questions. Use the structured tools for patient, pharmacy, "
            "bed, and scheduling lookups. "
            "Resolve follow-ups like 'yes', 'book it', 'tell me more' using the conversation history."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Conversation history:\n{history or '(none)'}\n\nCurrent message: {question}"
            }
        ]
    )

    tool_use = next((b for b in pick_response.content if b.type == "tool_use"), None)
    if tool_use is None:
        tool_name = "search_documents"
        tool_input = {"query": question}
    else:
        tool_name = tool_use.name
        tool_input = dict(tool_use.input) if tool_use.input else {}

    result, sources, route = _execute_tool(tool_name, tool_input)
    print(f"Tool: {tool_name}  Route: {route}")

    result_json = json.dumps(result, indent=2, default=str)
    answer_response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are the MedNova Hospital Chennai AI assistant. "
            "Compose a clear, concise answer to the user's question using ONLY the tool result provided. "
            "Cite specific facts from the result. If the result contains an 'error' key or is empty, "
            "say so politely. Protect patient privacy — share only what was asked. "
            "Be conversational but accurate."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Conversation history:\n{history or '(none)'}\n\n"
                    f"User question: {question}\n\n"
                    f"Tool used: {tool_name}\n"
                    f"Tool input: {json.dumps(tool_input)}\n"
                    f"Tool result:\n{result_json}\n\n"
                    "Write the user-facing answer."
                )
            }
        ]
    )
    answer = answer_response.content[0].text

    return {
        **state,
        "agent_route": route,
        "answer": answer,
        "sources": sources,
        "messages": [AIMessage(content=answer)],
        "tool_name": tool_name,
        "tool_input": tool_input,
    }


memory = MemorySaver()


def build_graph() -> StateGraph:
    graph = StateGraph(MedNovaState)
    graph.add_node("run_turn", run_turn)
    graph.set_entry_point("run_turn")
    graph.add_edge("run_turn", END)
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
            "messages": [HumanMessage(content=question)],
            "tool_name": "",
            "tool_input": {},
        },
        config=config,
    )
    return result
