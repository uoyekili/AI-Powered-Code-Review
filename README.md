# AI-Powered GitHub Code Review

A full-stack application that automatically reviews the source code of a public GitHub repository using AI.

A user pastes a repo URL, and the system clones the repo, scans the source code, analyzes it with Azure OpenAI, then returns a review dashboard along with a downloadable Markdown report.

## What It Does

- Accepts a public GitHub repo URL and creates a background review task.
- Clones the repo and scans files (ignoring `node_modules`, `.git`, etc.), collecting language stats, file count, and line count.
- Uses Azure OpenAI (via LangChain) to analyze each file, then aggregates the results into an overall assessment: security, performance, code quality, architecture, and maintainability.
- Scores the repository and tallies issues by severity and by category.
- Lets the frontend track progress in real time and view the report; exports the report as Markdown.

## Tech Stack

- **Frontend**: Next.js, React, TanStack Query
- **Backend**: FastAPI, SQLAlchemy, Alembic, GitPython, LangChain
- **Database**: PostgreSQL
- **AI**: Azure OpenAI

## Main API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/health` | Health check |
| POST | `/api/review` | Submit a repo URL for review |
| GET  | `/api/review/{task_id}` | Get the review result |
| GET  | `/api/review/{task_id}/progress` | Track analysis progress |
| GET  | `/api/report/{task_id}` | Download the Markdown report |

## Workflow

1. The user submits a public GitHub repo URL.
2. The backend validates the URL and creates a review task.
3. The repo is cloned and its source code is scanned.
4. Azure OpenAI analyzes the files and aggregates the results.
5. Results are stored in PostgreSQL.
6. The frontend polls progress and displays the dashboard report.

<!-- Setup, configuration, and run instructions... to be added later -->
