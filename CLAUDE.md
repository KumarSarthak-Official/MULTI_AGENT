# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-Agent Research Intelligence Platform - a production-grade system where 4 specialized AI agents collaborate via LangGraph StateGraph to produce structured research reports. Users submit a topic; agents work in parallel/sequence to search the web, retrieve from uploaded documents via RAG, critique drafts, and synthesize final reports streamed live via SSE.

## Architecture

### Agent Orchestration (LangGraph StateGraph)

The system uses a stateful graph with conditional edges:

```
Entry → Search Agent → RAG Agent → Synthesis Agent → Critique Agent
                                         ↑                    |
                                         └────(if score < 7)──┘
```

**Shared State** (`ResearchState` TypedDict):
- `query`, `messages`, `search_results`, `rag_context`
- `draft_report`, `critique`, `final_report`, `sources`
- `agent_logs`, `iteration_count`, `error`

**Agent Responsibilities:**
- **Search Agent**: Generates 3 diverse queries via LLM, runs DuckDuckGo search, deduplicates by URL (max 15 results)
- **RAG Agent**: Embeds query with nomic-embed-text, retrieves top-10 from Qdrant (cosine similarity, threshold=0.5), LLM re-ranks to top-6
- **Synthesis Agent**: Combines web + doc context into structured markdown report (Executive Summary, Key Findings, Analysis, Conclusion, Sources)
- **Critique Agent**: LLM-as-Judge pattern - scores accuracy, completeness, citations (1-10). If score < 7, triggers refinement loop (max 2 iterations)

**Critical Implementation Detail**: The conditional edge after critique checks `iteration_count` and score. Graph compiles once at startup in `backend/app/agents/graph.py`.

### Tech Stack

**Backend:**
- FastAPI with SSE streaming (`/api/v1/research/stream`)
- LangGraph 0.1.0 + LangChain 0.2.0
- Qdrant vector database (768-dim nomic-embed-text embeddings)
- Ollama Cloud API (qwen3.5 LLM + nomic-embed-text embeddings) - no local GPU needed
- PostgreSQL (report metadata), Redis (Celery broker)
- Python 3.11 managed by `uv` (not pip)

**Frontend:**
- Next.js 14 (App Router) with TypeScript
- Bun for package management and dev server
- SSE client hook for real-time agent progress
- React Markdown for streaming report rendering

**Infrastructure:**
- Docker Compose orchestrates 5 services: postgres, redis, qdrant, backend, frontend
- Qdrant collection: `research_docs` with cosine distance

## Development Commands

### Backend (Python with uv)

```bash
cd backend

# First-time setup
uv venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv sync  # installs from uv.lock

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest tests/ -v --cov=app

# Run single test
uv run pytest tests/test_agents.py::test_search_agent -v

# Add new dependency
uv add package-name  # auto-updates pyproject.toml and uv.lock

# Database migrations (Alembic)
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

### Frontend (Next.js with Bun)

```bash
cd frontend

# First-time setup
bun install

# Run development server
bun dev  # starts on localhost:3000

# Build for production
bun run build

# Type checking
bun run tsc --noEmit
```

### Docker Compose (Full Stack)

```bash
# Start all services
docker-compose up --build -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all services
docker-compose down

# Reset volumes (clears database + Qdrant)
docker-compose down -v
```

**Access Points:**
- Frontend: http://localhost:3000
- API Swagger: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

## Key Technical Patterns

### SSE Streaming Pattern

The `/api/v1/research/stream` endpoint uses FastAPI's `StreamingResponse` with `media_type="text/event-stream"`. Critical headers:
```python
headers={
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive"
}
```

**Event Types Emitted:**
- `start`: `{research_id, query}`
- `node_complete`: `{node, logs}` (after each agent)
- `complete`: `{final_report, sources, duration_seconds}`
- `error`: `{message}`

Frontend uses `eventsource-parser` to consume these events and update UI state.

### RAG Pipeline with Re-Ranking

Two-stage retrieval for precision:
1. **Vector Search**: Qdrant cosine similarity with `score_threshold=0.5`, `limit=10`
2. **LLM Re-Ranking**: LLM scores each chunk 0-10 for relevance, keeps top 6

Text splitting: `RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)` with separators `["\n\n", "\n", ".", " "]` to respect paragraph structure.

### Ollama Cloud Configuration

Set these environment variables (not local Ollama):
```
OLLAMA_CLOUD_URL=https://api.ollama.com
OLLAMA_API_KEY=ollama_xxxxx  # from ollama.com dashboard
LLM_MODEL=qwen3.5
EMBED_MODEL=nomic-embed-text
```

Embeddings service instantiation:
```python
OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=settings.OLLAMA_CLOUD_URL,
    headers={"Authorization": f"Bearer {settings.OLLAMA_API_KEY}"}
)
```

### Qdrant Collection Setup

Collection must be created before first use (typically in FastAPI lifespan):
```python
client.create_collection(
    collection_name="research_docs",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
)
```

Payload structure per chunk:
```python
{
    "text": chunk.page_content,
    "source": source_name,
    "page": chunk.metadata.get("page", i),
    "chunk_index": i
}
```

## Critical Implementation Notes

1. **Graph Compilation**: LangGraph compiles once at module import. State mutations happen via `operator.add` annotations on list fields.

2. **Iteration Guard**: The critique loop has `max_iterations=2` to prevent infinite refinement. Check `state["iteration_count"]` in conditional edge.

3. **Empty Vector Store Handling**: RAG agent must gracefully return `[]` when Qdrant collection is empty (no documents uploaded yet).

4. **DuckDuckGo Rate Limits**: Search agent generates 3 queries with `max_results=5` each. Deduplication by URL prevents returning duplicate sources.

5. **SSE Buffering**: Without `X-Accel-Buffering: no`, nginx/proxies may buffer events, breaking real-time streaming.

6. **uv vs pip**: This project uses `uv` for dependency management. Never run `pip install` - use `uv add` or `uv sync`. The lockfile is `uv.lock`, not `requirements.txt`.

7. **Bun vs npm**: Frontend uses Bun for faster installs and dev server. Commands are `bun install`, `bun dev`, not `npm install`, `npm run dev`.

## Environment Variables

Required in `.env` (see `.env.example`):
```
DATABASE_URL=postgresql://user:password@localhost:5432/research_db
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
OLLAMA_CLOUD_URL=https://api.ollama.com
OLLAMA_API_KEY=ollama_xxxxx
LLM_MODEL=qwen3.5
EMBED_MODEL=nomic-embed-text
```

## Project Structure Philosophy

- `backend/app/agents/` - All LangGraph nodes and state definitions
- `backend/app/tools/` - Reusable utilities (web search, PDF reader, vector store ops)
- `backend/app/services/` - LLM/embedding wrappers, report persistence
- `backend/app/api/routes/` - FastAPI endpoints (research, documents, health)
- `frontend/src/components/` - React components (AgentTimeline, StreamingReport, DocumentUpload)
- `frontend/src/app/` - Next.js App Router pages

State flows through the graph; agents are pure functions that take `ResearchState` and return updated state.
