# MedNova Health Agent

A comprehensive multi-agent AI system for MedNova Hospital Chennai.
Built with LangGraph, FastMCP, ChromaDB, SQLite, Claude Haiku, RAGAS, and Streamlit.

---

## What this system does

A user asks a healthcare question via the Streamlit UI.
The Orchestrator Agent decides which agent handles it.
The right agent fetches data and returns an answer.
The Evaluator Agent scores every response for quality.

---

## The 5 Agents

| Agent | What it does | Data source |
|---|---|---|
| RAG Agent | Answers clinical and policy questions | ChromaDB — MedNova documents |
| Patient Agent | Looks up patient details | SQLite — Patient DB |
| Pharmacy Agent | Checks medicines and billing | SQLite — Pharmacy DB |
| Bed Agent | Checks bed availability | SQLite — Bed DB |
| Scheduling Agent | Books doctor appointments | SQLite — Scheduling DB |

---

## Architecture
Streamlit UI
|
Orchestrator Agent (LangGraph — conditional routing)
|
|--- RAG Agent        --> ChromaDB (MedNova docs)
|--- Patient Agent    --> FastMCP --> SQLite (Patient DB)
|--- Pharmacy Agent   --> FastMCP --> SQLite (Pharmacy DB)
|--- Bed Agent        --> FastMCP --> SQLite (Bed DB)
|--- Scheduling Agent --> FastMCP --> SQLite (Scheduling DB)
|
Evaluator Agent (RAGAS + LLM-as-Judge + Routing accuracy)


---

## Folder Structure
mednova-health-agent/
│
├── src/
│   ├── rag_engine/       # ChromaDB + embeddings + retrieval
│   ├── agents/           # All 5 LangGraph agents + Orchestrator
│   ├── mcp_servers/      # FastMCP servers — one per SQLite DB
│   ├── database/         # SQLite mock database builders
│   └── evaluation/       # Evaluator agent — RAGAS + LLM-as-Judge
│
├── chroma_store/         # Persisted ChromaDB vector store
├── data/                 # MedNova source documents
└── README.md

---

## Build Sequence

- [x] Step 1 — GitHub repo created
- [x] Step 2 — venv + folder structure ready
- [x] Step 3 — Build 4 SQLite mock databases
- [x] Step 4 — Build 4 FastMCP servers
- [x] Step 5 — Copy + enrich RAG engine
- [x] Step 6 — Build 5 LangGraph agents
- [x] Step 7 — Build Orchestrator Agent
- [x] Step 8 — Build Evaluator Agent
- [x] Step 9 — Build Streamlit UI
- [x] Step 10 — Deploy to Streamlit Cloud

---

## Tech Stack

- LangGraph — multi-agent orchestration
- FastMCP — MCP servers connecting agents to databases
- ChromaDB — vector store for RAG
- all-MiniLM-L6-v2 — embedding model
- Claude Haiku — answer generation + LLM-as-Judge
- RAGAS — RAG evaluation framework
- SQLite — mock hospital databases
- Streamlit — user interface
- Python 3.11

---

## Portfolio note

apollo-rag (anjanakaladhar86-cloud/apollo-rag) remains deployed separately.
mednova-health-agent is the next-generation comprehensive system built on top of those foundations.