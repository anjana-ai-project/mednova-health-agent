# MedNova Health Agent — System Design

## 1. Overview

The MedNova Health Agent is a multi-agent AI system that answers healthcare
questions for MedNova Hospital Chennai. It combines retrieval-augmented
generation over hospital documents with structured lookups against operational
databases, orchestrated by a LangGraph router and evaluated by an automated
quality agent.

---

## 2. Goals and Non-Goals

### Goals
- Single conversational entry point for clinical-policy, patient, pharmacy,
  bed-availability, and appointment-scheduling queries.
- Deterministic routing of each query to the correct specialist agent.
- Grounded, source-cited answers for policy questions and accurate
  structured-data answers for operational questions.
- Continuous quality measurement via RAGAS, LLM-as-Judge, and routing accuracy.

### Non-Goals
- Real EHR integration (the system uses mock SQLite databases).
- Clinical decision-making or diagnosis.
- Multi-tenant or multi-hospital deployment.
- Real-time streaming or sub-second latency guarantees.

---

## 3. High-Level Architecture

```
                 ┌──────────────────────────┐
                 │      Streamlit UI        │
                 └────────────┬─────────────┘
                              │
                 ┌────────────▼─────────────┐
                 │  Orchestrator (LangGraph)│
                 │  conditional routing     │
                 └────────────┬─────────────┘
        ┌──────────┬──────────┼──────────┬──────────┐
        ▼          ▼          ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
   │  RAG   │ │Patient │ │Pharmacy│ │  Bed   │ │Scheduling│
   │ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │ │  Agent   │
   └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └────┬─────┘
       │          │          │          │           │
       ▼          ▼          ▼          ▼           ▼
   ┌────────┐ ┌────────────────────────────────────────┐
   │Chroma  │ │       FastMCP servers (one per DB)     │
   │ Store  │ ├────────┬────────┬────────┬─────────────┤
   └────────┘ │Patient │Pharmacy│  Bed   │ Scheduling  │
              │ SQLite │ SQLite │ SQLite │  SQLite     │
              └────────┴────────┴────────┴─────────────┘

              ┌──────────────────────────────────────┐
              │  Evaluator Agent                     │
              │  RAGAS + LLM-as-Judge + routing acc. │
              └──────────────────────────────────────┘
```

---

## 4. Components

### 4.1 Streamlit UI
- Chat interface with conversation history and source citations.
- Sidebar shows the routing decision and evaluator score per turn.

### 4.2 Orchestrator Agent (LangGraph)
- Receives the user query, classifies intent, and routes to one specialist
  agent via conditional edges.
- Intent classification uses Claude Haiku with a few-shot prompt covering the
  five agent categories.
- Falls back to the RAG Agent when intent is ambiguous.

### 4.3 Specialist Agents

| Agent | Backend | Responsibility |
|---|---|---|
| RAG Agent | ChromaDB | Clinical policy, ICU procedures, patient services, pharmacy services |
| Patient Agent | FastMCP → Patient SQLite | Patient lookup, demographics, admission history |
| Pharmacy Agent | FastMCP → Pharmacy SQLite | Medicine stock, billing, prescription status |
| Bed Agent | FastMCP → Bed SQLite | Ward/ICU bed availability, occupancy |
| Scheduling Agent | FastMCP → Scheduling SQLite | Doctor availability, appointment booking |

### 4.4 RAG Engine
- Loader: `RecursiveCharacterTextSplitter`, chunk size 500, overlap 50.
- Embeddings: `all-MiniLM-L6-v2` (384-dim).
- Store: `chromadb.PersistentClient` at `chroma_store/`.
- Retrieval: top-k = 3 by default, cosine distance, metadata-filtered by
  document source.

### 4.5 FastMCP Servers
- One server per SQLite database. Each exposes a typed tool surface
  (e.g. `get_patient_by_id`, `check_bed_availability`).
- Servers run as separate processes; agents connect over the MCP protocol.

### 4.6 Evaluator Agent
- RAGAS metrics: faithfulness, answer relevancy, context precision/recall.
- LLM-as-Judge: Claude Haiku scoring helpfulness and clinical safety on a 1-5
  scale with a structured rubric.
- Routing accuracy: compares orchestrator's chosen agent against an
  annotated gold-label set.

---

## 5. Data Model

### 5.1 ChromaDB Collection — `documents`
| Field | Type | Description |
|---|---|---|
| id | string | Sequential chunk id |
| document | string | Chunk text |
| embedding | float[384] | MiniLM embedding |
| metadata.source | string | Source filename (e.g. `icu_procedures.txt`) |

### 5.2 SQLite Schemas (mock)
- **Patient DB** — `patients(id, name, dob, gender, contact, admission_id)`
- **Pharmacy DB** — `medicines(id, name, generic_name, stock, price)`,
  `bills(id, patient_id, total, status)`
- **Bed DB** — `beds(id, ward, type, status, patient_id)`
- **Scheduling DB** — `doctors(id, name, specialty)`,
  `appointments(id, doctor_id, patient_id, slot, status)`

---

## 6. Request Lifecycle

1. User submits query via Streamlit.
2. Orchestrator classifies intent (one of five agent labels).
3. LangGraph conditional edge dispatches to the chosen specialist.
4. Specialist either runs a retrieval against ChromaDB or calls the relevant
   FastMCP server.
5. Agent composes a grounded answer with Claude Haiku.
6. Evaluator scores the turn asynchronously; score is surfaced in the UI.
7. Response and trace are stored for offline analysis.

---

## 7. Technology Choices

| Concern | Choice | Reason |
|---|---|---|
| Orchestration | LangGraph | Native conditional routing, stateful graphs |
| Tool protocol | FastMCP | Clean separation between agents and data |
| Vector store | ChromaDB | Local, persistent, zero-ops |
| Embeddings | all-MiniLM-L6-v2 | Small, fast, good quality on policy text |
| LLM | Claude Haiku | Low latency, low cost, strong instruction following |
| Eval | RAGAS + LLM-as-Judge | Industry-standard RAG metrics plus qualitative review |
| UI | Streamlit | Fast iteration, easy cloud deploy |

---

## 8. Deployment

- Local development: `streamlit run app.py`; MCP servers launched by a
  process supervisor.
- Cloud: Streamlit Community Cloud for the UI; MCP servers and ChromaDB
  bundled in the same container.
- Secrets (Anthropic API key) injected via Streamlit secrets manager.

---

## 9. Open Questions

- Should the Evaluator run inline (blocking the response) or asynchronously?
- How frequently should the ChromaDB index be rebuilt as documents are added?
- Do we need conversation memory across turns, or is each query independent?
- What is the gold-label dataset for measuring routing accuracy?

## 10. Build Sequence

- [x] Step 1 — GitHub repo
- [x] Step 2 — venv + folder structure  
- [x] Step 3 — SQLite databases
- [x] Step 4 — FastMCP servers
- [x] Step 5 — RAG engine copied and updated
- [ ] Step 6 — MedNova documents in data/ folder
- [ ] Step 7 — Embed documents into ChromaDB
- [ ] Step 8 — Build 5 LangGraph agents
- [ ] Step 9 — Build Orchestrator
- [ ] Step 10 — Build Evaluator
- [ ] Step 11 — Build Streamlit UI
- [ ] Step 12 — requirements.txt and .env
- [ ] Step 13 — Deploy to Streamlit Cloud