# 🤖 PROJECT 1 MASTER PLAN
# Multi-Agent Research Intelligence Platform

> **Tagline:** *"Give it a topic — it researches, synthesizes, debates, and delivers a structured report"*
> **Build Time:** 3–4 Weeks | **Difficulty:** ⭐⭐⭐⭐ | **Impact:** 🔥🔥🔥🔥🔥

---

## 🎯 PROJECT OVERVIEW

### What It Does
A production-grade multi-agent system where 4 specialized AI agents collaborate in a LangGraph StateGraph to produce structured research reports. The user submits a topic; agents work in parallel/sequence to search the web, retrieve from uploaded documents via RAG, critique the draft, and synthesize a final polished report — all streamed live to the UI via SSE.

### Why Recruiters Love This
This project hits every modern AI engineering checkbox in a single application:
- **LangGraph orchestration** — the most in-demand agentic framework right now
- **RAG with re-ranking** — demonstrates production retrieval, not toy ChromaDB examples
- **LLM-as-Judge** — the critique agent pattern used by OpenAI, Anthropic, and top AI labs
- **SSE streaming** — shows async production engineering, not blocking HTTP calls
- **Full-stack** — FastAPI + Next.js with real-time updates

### Target Companies
Sarvam AI, Krutrim, Sprinklr, any company building AI copilots, research tools, enterprise AI assistants, and document intelligence platforms.

---

## 🏗️ SYSTEM ARCHITECTURE

```
User Query
    │
    ▼
┌─────────────────────────────────────────┐
│          Orchestrator Agent              │
│         (LangGraph StateGraph)           │
└────┬──────────┬──────────┬──────────────┘
     │          │          │
     ▼          ▼          ▼
┌─────────┐ ┌────────┐ ┌──────────────┐
│ Search  │ │  RAG   │ │   Critique   │
│  Agent  │ │ Agent  │ │    Agent     │
│(DuckDuck│ │(Qdrant)│ │ (LLM-judge)  │
│  Go)    │ │        │ │              │
└────┬────┘ └────┬───┘ └──────┬───────┘
     │           │             │
     └───────────┴─────────────┘
                 │
                 ▼
        ┌────────────────┐
        │  Synthesis     │
        │    Agent       │
        └───────┬────────┘
                │
                ▼
     ┌──────────────────────┐
     │  FastAPI Backend     │
     │  (SSE Streaming)     │
     └──────────┬───────────┘
                │
                ▼
     ┌──────────────────────┐
     │  Next.js Frontend    │
     │  (Real-time stream)  │
     └──────────────────────┘
```

### Agent Roles Breakdown

| Agent | Responsibility | Key Technology |
|---|---|---|
| **Search Agent** | Generates 3 targeted queries, runs DuckDuckGo search, deduplicates by URL | DuckDuckGo API, LLM query expansion |
| **RAG Agent** | Embeds query, retrieves top-10 from Qdrant, LLM re-ranks to top-6 | nomic-embed-text, Qdrant cosine similarity |
| **Synthesis Agent** | Combines web + doc context, writes structured markdown report | Qwen3.5 (Ollama Cloud), structured prompting |
| **Critique Agent** | LLM-as-Judge: scores accuracy, completeness, citations (1-10) | LLM judge pattern, iterative refinement |

---

## 📁 FULL PROJECT STRUCTURE

```
research-intelligence-platform/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point + lifespan
│   │   ├── config.py                # Pydantic-settings config
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── research.py      # /stream and /sync endpoints
│   │   │   │   ├── documents.py     # PDF upload + ingestion
│   │   │   │   └── health.py        # /health check
│   │   │   └── middleware.py        # CORS, logging middleware
│   │   ├── agents/
│   │   │   ├── graph.py             # LangGraph StateGraph definition
│   │   │   ├── state.py             # ResearchState TypedDict
│   │   │   ├── search_agent.py      # Web search agent node
│   │   │   ├── rag_agent.py         # Qdrant retrieval + re-rank node
│   │   │   ├── critique_agent.py    # LLM-as-Judge node
│   │   │   └── synthesis_agent.py   # Final synthesis node
│   │   ├── tools/
│   │   │   ├── web_search.py        # DuckDuckGo wrapper
│   │   │   ├── pdf_reader.py        # PDF loading + chunking
│   │   │   └── vector_store.py      # Qdrant upsert + query ops
│   │   ├── models/
│   │   │   ├── schemas.py           # Pydantic request/response
│   │   │   └── db_models.py         # SQLAlchemy ORM
│   │   ├── services/
│   │   │   ├── llm_service.py       # Ollama Cloud LLM wrapper (qwen3.5)
│   │   │   ├── embedding_service.py # nomic-embed-text wrapper
│   │   │   └── report_service.py    # Report persistence
│   │   └── db/
│   │       ├── database.py          # Async SQLAlchemy engine
│   │       └── migrations/          # Alembic migration files
│   ├── tests/
│   │   ├── test_agents.py           # Agent unit tests
│   │   ├── test_api.py              # API integration tests
│   │   └── conftest.py              # Pytest fixtures
│   ├── Dockerfile
│   ├── pyproject.toml           # uv-managed dependencies
│   └── uv.lock                  # Lockfile (commit this)
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx             # Research input UI
│       │   └── reports/[id]/page.tsx # Report viewer
│       └── components/
│           ├── ResearchInput.tsx    # Query form
│           ├── AgentTimeline.tsx    # Live agent progress visualization
│           ├── StreamingReport.tsx  # Markdown streaming renderer
│           ├── SourceCard.tsx       # Citation display
│           └── DocumentUpload.tsx   # PDF drag-and-drop upload
├── docker-compose.yml
├── .github/workflows/ci.yml
└── .env.example
```

---

## 📋 PHASE-BY-PHASE IMPLEMENTATION PLAN

### PHASE 0: Environment Setup — Day 1

**Goals:** Install all infrastructure, verify everything runs.

```bash
# 1. Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env   # or restart terminal

# 2. Install Docker
sudo apt-get update && sudo apt-get install docker.io docker-compose -y
sudo usermod -aG docker $USER

# 3. Project scaffold
mkdir research-intelligence-platform && cd research-intelligence-platform
mkdir backend frontend

# 4. Bootstrap Python project with uv
cd backend
uv init --python 3.11        # creates pyproject.toml + .python-version
uv venv                       # creates .venv
source .venv/bin/activate

# 5. Install Python dependencies via uv
uv add fastapi==0.111.0 "uvicorn[standard]==0.30.0" \
    langchain==0.2.0 langgraph==0.1.0 langchain-community==0.2.0 \
    langchain-ollama==0.1.0 qdrant-client==1.9.0 \
    sqlalchemy==2.0.30 alembic==1.13.1 psycopg2-binary==2.9.9 \
    pydantic-settings==2.2.1 python-multipart==0.0.9 pypdf==4.2.0 \
    duckduckgo-search==6.1.7 celery==5.4.0 redis==5.0.4 \
    httpx==0.27.0 pytest==8.2.0 pytest-asyncio==0.23.7 \
    python-dotenv==1.0.1
# uv auto-generates uv.lock — no manual pip freeze needed

# 6. Ollama Cloud setup — no local install needed
# Sign up at https://ollama.com and get your API key
# Models used: qwen3.5 (LLM) + nomic-embed-text (embeddings)
# Add to .env:  OLLAMA_API_KEY=ollama_...
```

**Checkpoint:** `uv run python -c "import fastapi; print(fastapi.__version__)"` prints version. `.env` has `OLLAMA_API_KEY` set and cloud endpoint reachable.

---

### PHASE 1: Agent State & Graph Definition — Days 2–4

**Goals:** Define shared state, build all 4 agent nodes, wire the LangGraph.

**Key file: `backend/app/agents/state.py`**

```python
from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
import operator

class ResearchState(TypedDict):
    query: str
    messages: Annotated[List[BaseMessage], operator.add]
    search_results: List[dict]        # Web search hits
    rag_context: List[dict]           # Retrieved doc chunks
    draft_report: Optional[str]       # Synthesis agent output
    critique: Optional[str]           # Critique agent feedback
    final_report: Optional[str]       # Final polished output
    sources: List[dict]               # All citations
    agent_logs: Annotated[List[str], operator.add]  # Audit trail
    iteration_count: int              # Loop guard
    error: Optional[str]
```

**Key file: `backend/app/agents/graph.py`**

```python
from langgraph.graph import StateGraph, END
from .state import ResearchState
from .search_agent import search_agent_node
from .rag_agent import rag_agent_node
from .synthesis_agent import synthesis_agent_node
from .critique_agent import critique_agent_node

def build_research_graph():
    graph = StateGraph(ResearchState)
    
    graph.add_node("search", search_agent_node)
    graph.add_node("rag", rag_agent_node)
    graph.add_node("synthesis", synthesis_agent_node)
    graph.add_node("critique", critique_agent_node)
    
    graph.set_entry_point("search")
    graph.add_edge("search", "rag")
    graph.add_edge("rag", "synthesis")
    graph.add_edge("synthesis", "critique")
    
    # Conditional: if critique score < 7, loop back to synthesis
    def should_refine(state: ResearchState):
        if state.get("iteration_count", 0) >= 2:
            return END
        critique = state.get("critique", "")
        if "score: " in critique.lower():
            try:
                score = int(critique.lower().split("score: ")[1].split()[0])
                if score < 7:
                    return "synthesis"
            except Exception:
                pass
        return END
    
    graph.add_conditional_edges("critique", should_refine)
    return graph.compile()

research_graph = build_research_graph()
```

**Search Agent — critical implementation points:**
- LLM generates 3 diverse search queries from the original topic
- DuckDuckGo `ddgs.text()` with `max_results=5` per query
- Deduplication by URL before returning
- Returns max 15 unique results

**RAG Agent — critical implementation points:**
- `OllamaEmbeddings(model="nomic-embed-text", base_url=settings.OLLAMA_CLOUD_URL, headers={"Authorization": f"Bearer {settings.OLLAMA_API_KEY}"})` for query embedding
- Qdrant cosine similarity search with `score_threshold=0.5`, `limit=10`
- LLM re-ranks chunks by relevance score (0–10), keeps top 6
- Gracefully handles empty vector store (returns `[]`)

**Synthesis Agent — structured output format:**
```
# {topic}
## Executive Summary
## Key Findings
## Detailed Analysis
## Conclusion
## Sources
```

**Critique Agent — LLM-as-Judge prompt pattern:**
- Scores the draft on: factual accuracy, completeness, citation quality, writing clarity
- Returns structured feedback with score out of 10
- If score < 7, triggers a refinement loop (max 2 iterations)

**Checkpoint:** `uv run python -c "from app.agents.graph import research_graph; print('Graph built')"` runs without errors.

---

### PHASE 2: FastAPI Backend — Days 5–7

**Goals:** Build the API, SSE streaming endpoint, document upload endpoint.

**`main.py` — FastAPI with lifespan:**
- Initialize Qdrant collection on startup
- Initialize database tables (Alembic or `Base.metadata.create_all`)
- CORS middleware to allow `localhost:3000`

**`/api/v1/research/stream` — SSE endpoint:**
```python
@router.post("/stream")
async def research_stream(request: ResearchRequest):
    return StreamingResponse(
        stream_research_events(request.query, request.use_documents),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )
```

**SSE Event types emitted:**
| Event Type | When Sent | Payload |
|---|---|---|
| `start` | Immediately | `{research_id, query}` |
| `node_complete` | After each agent | `{node, logs}` |
| `complete` | After final synthesis | `{final_report, sources, duration_seconds}` |
| `error` | On exception | `{message}` |

**`/api/v1/documents/upload` — PDF ingestion:**
- Accepts multipart file upload
- Calls `ingest_document(file_path, source_name)` to chunk and embed into Qdrant
- Returns `{chunks_ingested, collection, source}`

**Qdrant vector store setup:**
```python
client.create_collection(
    collection_name="research_docs",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    # nomic-embed-text outputs 768-dimensional vectors
)
```

**Text splitting strategy:**
- `RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)`
- Separators: `["\n\n", "\n", ".", " "]` — respects paragraph structure

**Checkpoint:** `curl -X POST localhost:8000/api/v1/research/sync -H "Content-Type: application/json" -d '{"query":"What is RAG?"}' | python -m json.tool`

---

### PHASE 3: Document Ingestion Pipeline — Day 8

**Goals:** Full PDF → chunks → embeddings → Qdrant pipeline.

**`backend/app/tools/vector_store.py` — key functions:**

```python
def ensure_collection():
    """Create collection if not exists — idempotent."""

def ingest_document(file_path: str, source_name: str) -> dict:
    """
    1. Load PDF with PyPDFLoader or TextLoader
    2. Split into chunks with RecursiveCharacterTextSplitter
    3. Generate embeddings in batch with OllamaEmbeddings
    4. Upsert PointStruct objects to Qdrant with payload metadata
    Returns: {source, chunks_ingested, collection}
    """
```

**Payload stored per chunk:**
```python
payload={
    "text": chunk.page_content,
    "source": source_name,   # Original filename
    "page": chunk.metadata.get("page", i),
    "chunk_index": i
}
```

**Checkpoint:** Upload a PDF via Swagger UI at `localhost:8000/docs`, verify chunks appear in Qdrant dashboard at `localhost:6333/dashboard`.

---

### PHASE 4: Next.js Frontend — Days 9–12

**Goals:** Build the UI — research input form, live agent progress, streaming report renderer.

**Setup:**
```bash
cd frontend
# Install Bun if not already: curl -fsSL https://bun.sh/install | bash
bunx create-next-app@14 . --typescript --tailwind --app
bun add eventsource-parser react-markdown
```

**Component breakdown:**

**`AgentTimeline.tsx`** — Shows agent progress in real-time:
```typescript
// Displays a vertical timeline with 4 agent steps
// Each step: pending (grey) → running (pulsing blue) → done (green tick)
// Updates via SSE events received from /research/stream
```

**`StreamingReport.tsx`** — Renders markdown as it arrives:
```typescript
import ReactMarkdown from 'react-markdown';
// Accumulates SSE chunks and renders incrementally
// Full markdown support: headers, bullets, bold, code blocks
```

**`sse.ts` — SSE hook:**
```typescript
export function useResearchStream(query: string) {
    const [report, setReport] = useState("");
    const [agentLogs, setAgentLogs] = useState<string[]>([]);
    const [status, setStatus] = useState<"idle"|"running"|"done"|"error">("idle");
    
    // EventSource connection to /api/v1/research/stream
    // Parses SSE events by type: start, node_complete, complete, error
}
```

**`DocumentUpload.tsx`** — Drag-and-drop PDF uploader:
```typescript
// Uses HTML5 drag-and-drop events
// POST to /api/v1/documents/upload as FormData
// Shows upload progress + chunks_ingested count on success
```

**Checkpoint:** Visit `localhost:3000`, type a query, see all 4 agents light up in sequence, final report renders in markdown.

---

### PHASE 5: Docker & Deployment — Days 13–14

**`docker-compose.yml` — all services:**

```yaml
services:
  postgres:    # Port 5432 — report metadata storage
  redis:       # Port 6379 — Celery broker
  qdrant:      # Port 6333 — vector database
  backend:     # Port 8000 — FastAPI
  frontend:    # Port 3000 — Next.js
```

**Critical env vars for backend container:**
```env
DATABASE_URL=postgresql://user:password@postgres:5432/research_db
REDIS_URL=redis://redis:6379
QDRANT_URL=http://qdrant:6333
OLLAMA_CLOUD_URL=https://api.ollama.com          # Ollama Cloud endpoint
OLLAMA_API_KEY=ollama_xxxxxxxxxxxxxxxxxxxxxxxx   # From ollama.com dashboard
LLM_MODEL=qwen3.5
EMBED_MODEL=nomic-embed-text
```

**One-command startup:**
```bash
docker-compose up --build -d
docker-compose logs -f backend  # watch for errors
```

**Access points:**
- Frontend: `http://localhost:3000`
- API Swagger: `http://localhost:8000/docs`
- Qdrant dashboard: `http://localhost:6333/dashboard`

---

### PHASE 6: Testing — Day 15

**`tests/test_api.py`:**

```python
def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_research_sync_returns_report():
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/research/sync",
            json={"query": "What is RAG in AI?", "use_documents": False}
        )
    assert response.status_code == 200
    data = response.json()
    assert "final_report" in data
    assert len(data["final_report"]) > 100

def test_empty_query_returns_422():
    response = client.post("/api/v1/research/sync", json={"query": ""})
    assert response.status_code == 422
```

```bash
cd backend && uv run pytest tests/ -v --tb=short --cov=app
```

---

## 🔑 KEY TECHNICAL DECISIONS (Interview Talking Points)

| Decision | Why | Trade-off Acknowledged |
|---|---|---|
| LangGraph over LangChain LCEL | Stateful graphs with cycles, conditional edges | More complex than chains |
| DuckDuckGo over SerpAPI | Free, no API key needed | Rate limits on heavy use |
| Qdrant over ChromaDB | Production-grade, Docker-native, REST API | Heavier setup than in-memory |
| SSE over WebSocket | Simpler server-side (one-way), HTTP native | No bidirectional comms |
| nomic-embed-text over OpenAI ada | Free via Ollama Cloud, 768-dim | Requires OLLAMA_API_KEY |
| Cosine similarity + LLM re-rank | Best recall + precision combo | Double inference cost |

---

## 📊 SKILLS DEMONSTRATED

| Skill | Specific Implementation |
|---|---|
| LangGraph / Agentic AI | 4-node StateGraph with conditional critique loop |
| RAG Pipeline | Qdrant + nomic embeddings + LLM re-ranking |
| LLM-as-Judge | Critique agent evaluates synthesis quality, triggers refinement |
| FastAPI + SSE | Real-time streaming backend with proper headers |
| Next.js + Bun | SSE hook, agent timeline, markdown renderer — Bun for fast installs and dev server |
| Docker | Full containerized multi-service deployment |
| Async Python | `astream()` over LangGraph, async FastAPI routes |
| Vector Databases | Qdrant collections, cosine similarity, metadata filtering |

---

## 🚀 DEPLOYMENT STRATEGY (Free Stack)

| Service | Deploy Target | Notes |
|---|---|---|
| Next.js Frontend | **Vercel** | One-click from GitHub |
| FastAPI Backend | **HuggingFace Spaces** | FastAPI + Gradio wrapper |
| PostgreSQL | **Railway.app** | Free $5 credit |
| Qdrant | **Qdrant Cloud** | Free 1GB cluster |
| LLM | **Ollama Cloud** | `qwen3.5` + `nomic-embed-text` via cloud API — no local GPU needed |

**For demo:** Ollama Cloud handles inference for both LLM and embeddings. No local Ollama install required — just set `OLLAMA_CLOUD_URL` and `OLLAMA_API_KEY` in your deployment env vars.

---

## 📅 DAILY BUILD SCHEDULE

| Day | Task | Done? |
|---|---|---|
| 1 | Environment setup — uv, Docker, Bun, Ollama Cloud API key, all dependency installs | ☐ |
| 2 | `state.py` + `graph.py` — LangGraph skeleton, all nodes stubbed | ☐ |
| 3 | `search_agent.py` — DuckDuckGo integration, query expansion | ☐ |
| 4 | `rag_agent.py` + `vector_store.py` — Qdrant setup, retrieval, re-ranking | ☐ |
| 5 | `synthesis_agent.py` + `critique_agent.py` — prompt engineering | ☐ |
| 6 | `main.py` + `research.py` — FastAPI setup, `/stream` SSE endpoint | ☐ |
| 7 | `documents.py` — PDF upload + Qdrant ingestion pipeline | ☐ |
| 8 | End-to-end backend test via curl / Swagger UI | ☐ |
| 9 | Next.js project setup + `sse.ts` hook | ☐ |
| 10 | `AgentTimeline.tsx` + `StreamingReport.tsx` | ☐ |
| 11 | `DocumentUpload.tsx` + full UI integration | ☐ |
| 12 | Frontend polish — loading states, error handling, dark theme | ☐ |
| 13 | Docker Compose — all services, health checks, env vars | ☐ |
| 14 | End-to-end Docker test + smoke tests | ☐ |
| 15 | Pytest suite — unit + integration tests, coverage report | ☐ |
| 16–18 | GitHub Actions CI, README with GIF, architecture diagram | ☐ |

---

## 📝 README CHECKLIST (Before Marking as Done)

```
□ Architecture diagram (draw.io or Mermaid)
□ Demo GIF showing: upload PDF → type query → agents fire → report streams
□ Tech stack badges (Python/uv, FastAPI, LangGraph, Next.js/Bun, Qdrant, Docker, Ollama Cloud)
□ Quick start: 5 commands to get running
□ API docs link (Swagger auto-generated)
□ GitHub Actions CI badge
□ .env.example with all required vars
□ MIT License
```

---

## 💬 INTERVIEW ANSWER TEMPLATES

**"Walk me through your most complex project"**
> "I built a multi-agent research platform using LangGraph. The system has 4 specialized agents wired in a StateGraph — a search agent that expands the query into 3 targeted DuckDuckGo searches, a RAG agent that retrieves from a Qdrant vector store and uses LLM re-ranking for precision, a synthesis agent that combines both sources into a structured markdown report, and a critique agent acting as an LLM-as-Judge. If the critique score is below 7 out of 10, the graph loops back to synthesis. The final report streams to the frontend via SSE. I used Ollama Cloud with Qwen3.5 for inference and nomic-embed-text for embeddings — so no local GPU required. On the tooling side, I used uv for Python dependency management and Bun for the Next.js frontend. The full stack — PostgreSQL, Redis, Qdrant, backend, frontend — is containerized with Docker Compose with a GitHub Actions CI pipeline."

**"How does SSE differ from WebSocket and why did you choose it?"**
> "SSE is unidirectional — server pushes to client over a standard HTTP connection. WebSocket is bidirectional over a persistent socket. For research streaming, the client only needs to receive events from the server — no client-to-server messages mid-stream — so SSE was simpler, naturally HTTP/2 compatible, and auto-reconnects on drop. WebSocket would have been over-engineered here."

**"What is LLM-as-Judge and why is it better than ROUGE?"**
> "ROUGE measures n-gram overlap against a reference. LLM-as-Judge asks an LLM to holistically evaluate output quality — checking factual accuracy, logical coherence, citation quality, completeness. There's no reference text needed. The tradeoff is LLM evaluation is slower and non-deterministic, but it catches things ROUGE misses completely, like contradictions or hallucinations that happen to share n-grams with a reference."
