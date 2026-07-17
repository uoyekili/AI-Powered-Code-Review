# AI-Powered GitHub Code Review

Full-stack application that clones public GitHub repositories, analyzes source code with Azure OpenAI, and presents interactive review dashboards with downloadable Markdown reports.

## Stack

- **Frontend**: Next.js 16, React 19, TanStack Query, Axios
- **Backend**: FastAPI, SQLAlchemy, Alembic, GitPython, LangChain
- **Database**: PostgreSQL 16
- **AI**: Azure OpenAI

## Environment Configuration

Configuration follows the [Twelve-Factor App](https://12factor.net/config) config principle — each service owns its environment variables.

| File | Purpose |
|------|---------|
| `.env` | Shared infrastructure only (PostgreSQL credentials) |
| `backend/.env` | Backend application config |
| `frontend/.env` | Frontend application config |

Setup:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Fill in Azure OpenAI credentials in `backend/.env`.

**Required backend variables** (no defaults — app fails fast if missing):

- `DATABASE_URL`, `CORS_ORIGINS`
- `AZURE_OPENAI_BASE_URL`, `AZURE_OPENAI_CHAT_API_KEY`, `AZURE_OPENAI_CHAT_MODEL`
- `AZURE_OPENAI_EMBEDDING_API_KEY`, `AZURE_OPENAI_EMBEDDING_MODEL`

**Required frontend variables:**

- `NEXT_PUBLIC_API_URL`

## Quick Start (Docker)

### Development

```bash
docker compose -f docker-compose.dev.yml up --build
```

### Production

```bash
docker compose --env-file .env --env-file frontend/.env -f docker-compose.prod.yml up --build -d
```

The extra `--env-file frontend/.env` is needed so Docker Compose can pass `NEXT_PUBLIC_API_URL` as a build argument for the Next.js production image.

Open the app:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Health check: http://localhost:8000/api/health

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/review` | Submit repository URL for review |
| GET | `/api/review/{task_id}` | Get completed review |
| GET | `/api/review/{task_id}/progress` | Poll analysis progress |
| GET | `/api/report/{task_id}` | Download Markdown report |

## Local Development

Start PostgreSQL (via Docker or local install), then:

### Backend

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

Config is loaded from `backend/.env` via `pydantic-settings`.

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

Config is loaded from `frontend/.env` (Next.js reads `NEXT_PUBLIC_*` automatically).

## Architecture

```
backend/app/
├── api/           # REST routes
├── config/        # Settings (pydantic-settings)
├── core/          # Logging, exceptions
├── database/      # SQLAlchemy session
├── models/        # ORM models
├── schemas/       # Pydantic DTOs (camelCase for frontend)
├── repositories/  # Data access layer
├── services/      # Business logic (GitHub, scanner, LangChain, reports)
├── prompts/       # LLM prompts
├── workers/       # Background review tasks
└── utils/         # URL parsing, file utilities
```

## Workflow

1. User submits a public GitHub URL
2. Backend validates URL and creates a review task
3. Repository is cloned and scanned (ignoring `node_modules`, `.git`, etc.)
4. Source files and metadata are analyzed with Azure OpenAI
5. Results are stored in PostgreSQL
6. Frontend polls progress and displays the dashboard report
