# StudyBuddy+ (MVP v0.1)

Study companion stack built with FastAPI, Celery, Postgres, Redis, MinIO, Mistral-powered OCR, and a static PWA frontend.

## Quick Start
1. Copy .env.example to .env.
   - Provide values for secrets such as MISTRAL_API_KEY, S3_ACCESS_KEY_ID, and S3_SECRET_ACCESS_KEY.
   - Adjust APP_URL, DATABASE_URL, and other settings to match your environment if needed.
2. Start the stack: docker compose up --build.
3. Open the API docs at http://localhost:8000/docs and load the PWA by opening web/index.html (or serve it from a static host).
4. Optional: run python scripts/seed_memes.py to generate SQL inserts for sample memes.

## Compose Services
- db: Postgres 15 (port 5432) for persistent storage.
- 
edis: Redis 7 (port 6379) for queues, locks, and cache.
- minio: MinIO server (ports 9000/9001) providing an S3-compatible object store for uploads.
- create-bucket: one-shot MinIO client container that ensures the studybuddy bucket exists.
- api: FastAPI app served by Uvicorn with autoreload enabled; depends on db, redis, and minio.
- worker: Celery worker handling OCR, summarization, and flashcard generation jobs.

## Environment & Secrets
Keep sensitive values in .env.
- APP_URL � allowed frontend origin.
- DATABASE_URL, REDIS_URL � connection strings used by the API and worker.
- S3_ENDPOINT, S3_REGION, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, S3_BUCKET � object storage configuration.
- MISTRAL_API_KEY, MISTRAL_OCR_MODEL � required for the Mistral OCR pipeline.
- OPENAI_API_KEY � placeholder for future summarization options.
- OLLAMA_HOST, OLLAMA_MODEL � LLM endpoint used for summaries and flashcards (defaults to an Ollama runtime).
- OCR_MAX_PAGES, JWT_SECRET, ENV, and other knobs documented in .env.example.

## API Surface
**Health**
- GET /healthz � returns { ok, storage, db, redis } with sub-status details.

**Auth**
- POST /v1/auth/email
- GET /v1/me

**Notes & Summaries**
- GET /v1/notes
- POST /v1/notes � multipart upload endpoint.
- GET /v1/notes/{id}
- POST /v1/notes/{id}/summarize � accepts page_start, page_end, max_pages.
- GET /v1/notes/{id}/summary

**Focus Rooms**
- GET /v1/rooms
- POST /v1/rooms
- GET /v1/rooms/{id}
- POST /v1/rooms/{id}/sessions/start
- POST /v1/rooms/{id}/sessions/stop
- WS /v1/rooms/{id}/socket

**Memes & Jobs**
- GET /v1/memes/random (category query param optional)
- POST /v1/memes/{id}/share
- GET /v1/jobs/{id}

**Subscription**
- GET /v1/subscription
- POST /v1/subscription/activate
- POST /v1/subscription/cancel

## Dev Notes
- API and worker share the same codebase and dependencies; hot reload is enabled inside the API container.
- Database schema reference lives in db/schema.sql; plan to replace with migrations later.
- OCR is powered by Mistral's OCR API (MISTRAL_API_KEY required) with optional page range trimming before upload.
- Summaries and flashcards call the configured LLM endpoint (defaults to an Ollama host defined by OLLAMA_HOST).
- Static PWA (web/) stays framework-free for fast iteration.

## Project Layout
- ackend/ � FastAPI app, service layer, Celery tasks.
- web/ � minimal PWA assets.
- db/ � SQL schema snapshot.
- docs/ � architecture and design notes.
- scripts/ � utility scripts such as seed_memes.py.

## Roadmap Fit
Delivers MVP goals: upload notes, run OCR and summaries, host shared focus rooms with timers, surface meme breaks, and gate features via basic subscription checks.
