# AI-Powered GitHub Code Review (Skeleton)

Clean project skeleton for an AI-assisted GitHub code review application.

This repository is intentionally incomplete. Business logic is stubbed with `NotImplementedError` or mock return values so you can implement each stage yourself.

## Architecture

```text
User → FastAPI → ReviewService → ReviewRepository → PostgreSQL
                 ReviewService → WorkerService → ReviewPipeline
                                      ├─ RepositoryService
                                      ├─ StaticAnalysisService
                                      ├─ LLMReviewService
                                      └─ ReportService
Frontend (Next.js) polls progress and renders the final mock report.
```

## Project Layout

```text
backend/app/
  api/routes/       # Thin HTTP routes
  config/           # Settings
  core/             # Exceptions and logging
  database/         # Engine and sessions
  models/           # Single ReviewTask ORM model
  repositories/     # Persistence helpers
  review/           # Pipeline sequencing
  schemas/          # Pydantic API contracts
  services/         # Service interfaces (stubs)
  workers/          # Background task adapter
  utils/            # Small helpers

frontend/
  app/              # Next.js App Router pages
  components/       # Small UI components
  hooks/            # Client state/polling
  services/         # API client
  types/            # Shared TypeScript contracts
  utils/            # Env and formatting helpers
```

## Mock Data Flow

1. `POST /api/review` validates a GitHub URL and creates a `review_tasks` row.
2. An in-process worker advances mock pipeline steps and stores a zeroed result.
3. `GET /api/review/{id}/progress` returns step status for the loading page.
4. `GET /api/review/{id}` returns the mock review payload.
5. `GET /api/report/{id}` returns a placeholder Markdown report.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/review` | Submit a repository URL |
| GET | `/api/review/{task_id}` | Get review result |
| GET | `/api/review/{task_id}/progress` | Track progress |
| GET | `/api/report/{task_id}` | Download Markdown report |

## Setup

### Prerequisites

- Python 3.13 + [uv](https://github.com/astral-sh/uv)
- Node.js 20+ + pnpm
- PostgreSQL 16 (or Docker Compose)

### Environment

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Backend

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

### Docker (dev)

```bash
docker compose -f docker-compose.dev.yml up --build
```

## Implementation Checklist

Implement these stages in order:

1. **Clone repository** — `RepositoryService.clone_repository`
2. **Scan repository** — language, framework, structure, file counts
3. **Static analysis** — parse, lint, security, complexity, duplicates
4. **Chunk repository** — `LLMReviewService.chunk_repository`
5. **Parallel LLM review** — durable queue + worker pool
6. **Merge results** — dedupe issues, rank severity, calculate scores
7. **Generate report** — project summary, issue details, recommendations
8. **Frontend polish** — richer issue detail and statistics views

## Database

The skeleton uses a single `review_tasks` table:

- task state (`status`, `progress`, `current_step`)
- `steps` JSON for progress UI
- `result` JSON for the completed review payload
- `report_markdown` for the downloadable report

Existing multi-table schemas were intentionally discarded. Run migrations on a fresh database.

## Tests

```bash
cd backend
uv sync
uv run pytest
uv run ruff check app tests
```

```bash
cd frontend
pnpm install
pnpm lint
pnpm typecheck
pnpm build
```
