# 13 Development Setup

## Prerequisites

Suggested local prerequisites:

- Python
- npm
- a local Azure OpenAI configuration for backend testing
- an MCP-capable IDE such as Cursor if IDE workflows are being tested

## Backend Setup

```text
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn local_api.main:app --host 127.0.0.1 --port 8000
```

## Frontend Setup

```text
cd frontend
npm install
copy .env.example .env
npm run dev
```

## MCP Setup

Conceptually:

- Cursor connects to `backend/mcp_server/server.py`
- MCP tools call `graphpilot_core` directly
- backend `.env` provides runtime configuration

## Environment Files

GraphPilot uses separate env files by runtime:

- frontend: `frontend/.env` and `frontend/.env.example`
- backend: `backend/.env` and `backend/.env.example`

Key rules:

- frontend Vite variables must start with `VITE_`
- frontend env files must not contain Azure OpenAI secrets
- backend env files own Azure OpenAI secrets and local path configuration
- root `.env` is not the active MVP configuration path

## Suggested Repo Structure

High-level only:

```text
graphpilot/
  README.md
  docs/
  backend/
  frontend/
```

Detailed frontend and backend structures are described in:

- `docs/04-backend-architecture.md`
- `docs/05-frontend-architecture.md`

## Development Constraints

- docs-first before implementation
- keep frontend and backend separately deployable
- do not reintroduce database or auth assumptions into setup guidance
- do not add real secrets to the repository
- do not assume Docker is required for MVP setup
