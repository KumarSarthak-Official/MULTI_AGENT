# 🧠 Multi-Agent Research Platform

A full-stack, containerized AI research platform powered by a multi-agent LLM pipeline. Upload research documents, ask complex questions, and receive structured, synthesized answers via a coordinated crew of AI agents.

---

## ✨ Features

- **Multi-Agent Pipeline** — Specialized agents for research, RAG retrieval, synthesis, and critique
- **RAG (Retrieval-Augmented Generation)** — Upload PDFs and query them using vector embeddings
- **Hybrid AI Models** — Ollama Cloud for LLM tasks + Google Gemini for embeddings
- **Vector Search** — Qdrant for fast semantic similarity search
- **Persistent Storage** — PostgreSQL for conversation history, Redis for caching
- **Containerized** — Full Podman/Docker Compose setup for one-command deployment

---

## 🏗️ Architecture

```
frontend (Next.js)  ──►  backend (FastAPI)  ──►  Agents (LangGraph)
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
                PostgreSQL    Redis      Qdrant
                (history)   (cache)   (vectors)
```

---

## 🚀 Quick Start

### Prerequisites

- [Podman](https://podman.io/) or [Docker](https://www.docker.com/) + Compose
- [Bun](https://bun.sh/) (for frontend local dev)
- [uv](https://github.com/astral-sh/uv) (for backend local dev)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/MULTI_AGENT.git
cd MULTI_AGENT
```

### 2. Configure environment

```bash
# Root env (used by docker-compose for service URLs)
cp .env.example .env

# Backend env (used inside the backend container)
cp backend/.env.example backend/.env
```

Edit both `.env` files and fill in your API keys:

| Variable | Where to get it |
|----------|----------------|
| `OLLAMA_API_KEY` | [ollama.com](https://ollama.com) |
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |
| `QDRANT_API_KEY` | [Qdrant Cloud](https://cloud.qdrant.io) (optional, for remote Qdrant) |

### 3. Run with Podman/Docker

```bash
podman-compose up -d --build
# or
docker compose up -d --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8001 |
| API Docs | http://localhost:8001/docs |

---

## 🔧 Development

### Backend (FastAPI + Python)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8001
```

### Frontend (Next.js + Bun)

```bash
cd frontend
bun install
bun run dev
```

### Database Migrations

```bash
cd backend
uv run alembic upgrade head
```

---

## 📁 Project Structure

```
MULTI_AGENT/
├── backend/
│   ├── app/
│   │   ├── agents/        # LangGraph multi-agent logic
│   │   ├── api/           # FastAPI route handlers
│   │   ├── db/            # Database session & models
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── services/      # Embedding, RAG, search services
│   │   └── tools/         # Agent tools
│   ├── alembic/           # Database migrations
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── app/               # Next.js app router pages
│   ├── components/        # React components
│   ├── hooks/             # Custom React hooks
│   ├── lib/               # API client & utilities
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🤖 Models

| Task | Model | Provider |
|------|-------|----------|
| LLM / Agents | `gemma4:31b-cloud` | Ollama Cloud |
| Embeddings | `gemini-embedding-2-flash` | Google Gemini |

---

## 📄 License

MIT
