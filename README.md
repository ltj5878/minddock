# MindDock

MindDock is a local-first personal knowledge and project workspace. It captures notes, classifies them with AI, links them to projects, turns project context into tasks, and answers questions over the local knowledge base with citations.

The current app is a Vue 3 + FastAPI prototype with a working local backend, Notion integration hooks, project/task management, local/AI review flows, and an initial RAG path.

## Current Status

| Area | Status | Notes |
| --- | --- | --- |
| Web app shell | Done | Vue 3, Vite, Pinia, Vue Router, Naive UI layout with Inbox, Ask, Projects, Review, and Settings views. |
| Note capture | Done | Create notes from the Inbox, classify content, store locally, filter/search by type and text. |
| Notion sync | Partially done | Supports writing captured notes to Notion and importing pages from a Notion database when credentials are configured. OAuth is not implemented. |
| Projects | Done | Create, list, inspect, and delete projects. Notes can be associated with projects. |
| Tasks | Done | Create, update, complete, delete, and auto-generate project tasks from project context. |
| Knowledge Q&A | Partially done | Uses embeddings/RAG when OpenAI is configured; falls back to local keyword search when embeddings or API keys are unavailable. |
| Reviews | Partially done | Daily and weekly local summaries are available. AI weekly review requires `OPENAI_API_KEY`. |
| Settings | Partially done | Stores Notion and model preferences for a single development user. Production auth/multi-user support is not complete. |
| Supabase | Scaffolded | Initial schema migration exists under `supabase/migrations`, but the app currently runs through SQLAlchemy against `DATABASE_URL`. |

## Features

- Capture notes into a local database from the Inbox UI.
- AI classification for note title, summary, type, tags, and action items.
- Optional Notion page creation for captured notes.
- Pull notes from a configured Notion database.
- Manage projects and project-specific tasks.
- Generate project assistant insights, next actions, recommended tags, and tasks.
- Ask questions over notes with citations.
- Generate daily and weekly review summaries.
- Configure Notion and model preferences from the Settings UI.

## Tech Stack

- Frontend: Vue 3, Vite, TypeScript, Pinia, Vue Router, Naive UI, Axios.
- Backend: FastAPI, SQLAlchemy 2, Pydantic Settings, Uvicorn.
- AI: OpenAI chat and embeddings; config placeholders for Anthropic, Gemini, and DeepSeek.
- Integrations: Notion API, Supabase migration scaffold.
- Databases: MySQL by default if `DATABASE_URL` is omitted; PostgreSQL or SQLite can be used through SQLAlchemy-compatible URLs.

## Project Structure

```text
.
├── backend/                 # FastAPI app, models, services, API routes
├── frontend/                # Vue 3 web app
├── supabase/migrations/     # Initial Supabase/Postgres schema draft
├── start.sh                 # Local start/stop/status helper
├── .env.example             # Root environment template
└── README.md
```

## Requirements

- Node.js and npm
- Python 3.11+
- A running database matching `DATABASE_URL`
- Optional: OpenAI API key for embeddings, RAG answers, classification, and AI reviews
- Optional: Notion integration token and database ID for Notion sync

## Configuration

Copy the example environment file and edit values for your machine:

```bash
cp .env.example .env
```

Important variables:

```bash
DATABASE_URL=mysql+pymysql://root@localhost:3306/minddock
OPENAI_API_KEY=your-openai-key
NOTION_INTEGRATION_TOKEN=your-notion-token
NOTION_NOTES_DATABASE_ID=your-notion-notes-database-id
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_API_KEY=your-deepseek-key
DEEPSEEK_MODEL_NAME=deepseek-chat
```

If `DATABASE_URL` is not set, the backend defaults to:

```bash
mysql+pymysql://root@localhost:3306/minddock
```

For quick local experiments, SQLite also works:

```bash
DATABASE_URL=sqlite:///./minddock.db
```

## Run Locally

Use the helper script from the repository root:

```bash
./start.sh
```

It installs missing frontend dependencies, creates `backend/.venv` if needed, installs backend dependencies, and starts both services:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

Stop or inspect services:

```bash
./start.sh status
./start.sh stop
```

## Manual Development

Backend:

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Build the frontend:

```bash
cd frontend
npm run build
```

## API Overview

Backend routes are mounted under `/api/v1`.

- `GET /api/health` checks service health.
- `GET /api/v1/notes` lists notes.
- `POST /api/v1/notes/capture` captures and classifies a note.
- `POST /api/v1/notes/sync/notion` imports notes from Notion.
- `PATCH /api/v1/notes/{note_id}` updates a note.
- `DELETE /api/v1/notes/{note_id}` deletes a note.
- `GET /api/v1/projects` lists projects and tasks.
- `POST /api/v1/projects` creates a project.
- `GET /api/v1/projects/{project_id}/assistant` generates project insights.
- `POST /api/v1/projects/{project_id}/tasks/generate` generates tasks from project context.
- `POST /api/v1/projects/tasks` creates a task.
- `PATCH /api/v1/projects/tasks/{task_id}` updates a task.
- `POST /api/v1/chat/ask` answers questions over notes.
- `GET /api/v1/review/weekly` generates an AI weekly review.
- `GET/PATCH /api/v1/settings` reads or updates the development user's settings.

## Data and Security Notes

- Do not commit `.env`, local database files, logs, or process files.
- `service_role` and other secret keys must stay server-side only.
- The Settings page is currently a single-user development flow, not production authentication.
- Notion credentials can be stored through the app, but token rotation and OAuth are not implemented yet.
- Supabase RLS policies should be reviewed before exposing the Supabase schema through public APIs.

## Known Gaps

- No production authentication or multi-user isolation yet.
- Supabase schema is present, but the running backend currently depends on SQLAlchemy and `DATABASE_URL`.
- AI features degrade gracefully without API keys, but full RAG answers and weekly reviews require OpenAI configuration.
- No automated test suite is committed yet.
- Deployment configuration is not included.
