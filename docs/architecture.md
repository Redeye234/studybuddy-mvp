# StudyBuddy+ Architecture (MVP v0.1)

## Overview
StudyBuddy+ combines AI study tools with social focus rooms and light entertainment. MVP is a FastAPI backend with Celery workers, Postgres, Redis, and an S3-compatible store. A minimal PWA provides uploads, summaries, focus rooms, and meme breaks.

## Components
- Backend (FastAPI): REST APIs, WebSockets for focus rooms, auth stub.
- Worker (Celery): OCR + summarization + flashcards generation.
- Storage (S3-compatible): MinIO locally, S3/Wasabi in prod.
- Database (Postgres): core entities; Redis for timers, presence, and rate limits.
- Web (PWA): no-build static app for quick iteration.

## Data Flow
1) Upload note → stored in S3 → enqueue `process_note` job → OCR (if needed) → GPT summary + flashcards → save to DB → user confirms → publish ready state.
2) Focus room → users connect via WebSocket → timer ticks + presence → on session end ≥25 min → meme suggestion → optional share event.
3) Subscription gating → server checks plan on critical endpoints (uploads/rooms).

## Env Vars (core)
- DATABASE_URL, REDIS_URL
- S3_ENDPOINT, S3_REGION, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, S3_BUCKET
- OPENAI_API_KEY (for summarization)
- APP_URL (PWA origin)

## Non-Functional
- Basic rate limiting via Redis.
- Request/Job logs; coarse error boundaries.
- File retention defaults to 30 days.

## Future (Phase 2+)
- Private rooms, richer analytics, OAuth, React app, CI/CD.
