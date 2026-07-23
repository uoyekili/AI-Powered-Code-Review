# AI-Powered Code Review

An AI-assisted GitHub code review application.

## Services

| Service | Role |
|---------|------|
| `api` | Public HTTP API (submit review, progress, results, report) |
| `worker` | Background poller that runs the review pipeline |
| `frontend` | Next.js UI |
| `postgres` | Shared database |
| `db` | Shared SQLAlchemy models and Alembic migrations (`import database`) |

## Features

- Submit a GitHub repository URL and create a review task
- Worker clones/scans the repository and runs the review pipeline
- Track review progress step by step
- View findings by file and severity
- Download a Markdown report

## Local development

```bash
cp .env.example .env
cp api/.env.example api/.env
cp worker/.env.example worker/.env
cp frontend/.env.example frontend/.env

docker compose -f docker-compose.dev.yml up --build
```

- API: http://localhost:8000/api/health
- Frontend: http://localhost:3000

## Database package

ORM models live in `db/database/` (import as `database.*`); Alembic lives
alongside in `db/alembic/`. The API runs `alembic upgrade head` on
startup; api and worker both import `database.models`.
