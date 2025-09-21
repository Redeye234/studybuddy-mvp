# StudyBuddy+ (MVP v0.1)

Minimal full-stack scaffold: FastAPI API, Celery worker, Postgres, Redis, MinIO, and a no-build PWA.

## Quick Start
1) Copy `.env.example` to `.env` and adjust if needed.
2) Start stack:
   - `docker compose up --build`
   - First run will download the Mistral model via Ollama (free/open-source runtime). If the API starts before Ollama is ready, retry after Ollama finishes pulling the model.
3) Open API: `http://localhost:8000/docs` and PWA: open `web/index.html` in a browser (or serve statically).

## Key Endpoints
- Health: `GET /healthz`
- Auth: `POST /v1/auth/email`, `GET /v1/me`
- Notes: `POST /v1/notes`, `POST /v1/notes/{id}/summarize` (async; accepts `page_start`, `page_end`, `max_pages`), `GET /v1/notes/{id}/summary`
- Focus: `GET/POST /v1/rooms`, `WS /v1/rooms/{id}/socket`, sessions start/stop
- Memes: `GET /v1/memes/random`, `POST /v1/memes/{id}/share`
- Jobs: `GET /v1/jobs/{id}` for status
- Subscription: `GET/POST /v1/subscription*`

### Health details
- `/healthz` returns `{ ok, storage, db, redis }`:
  - `storage`: MinIO bucket status `{ ok, bucket, error? }`
  - `db`: Postgres connectivity `{ ok, error? }`
  - `redis`: Redis connectivity `{ ok, error? }`

## Dev Notes
- Backing services via Docker; API auto-reloads.
- DB schema in `db/schema.sql` (use migrations later).
- AI/OCR: OCR uses Tesseract + pdf2image (via Poppler). Summarization/flashcards use Ollama `mistral` model by default. Configure with `OLLAMA_MODEL`.
  - Optional OCR via vision LLM: set `OCR_ENGINE=ollama` and `OLLAMA_OCR_MODEL=mistral-ocr-2503` (or another OCR-capable model). Pages capped by `OCR_MAX_PAGES` (default 20). Falls back to Tesseract if LLM OCR fails.
- PWA is plain JS to avoid build tooling; swap for React later if desired.

## Structure
- `backend/` FastAPI app and Celery worker
- `web/` minimal PWA (no build)
- `docs/` architecture notes
- `scripts/seed_memes.py` helper

## Roadmap Fit
Aligns to PRD: uploads→summary, public rooms, meme break, basic subscription gating.
