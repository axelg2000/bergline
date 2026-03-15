# Bergline — Local Development Guide

## 1. Architecture Overview

```
Reddit ──┐
Telegram ─┤──→ Scrapers ──→ RawMessage ──→ GPT-4o-mini ──→ ParsedMessage ──→ QueueSnapshot ──→ API
Form ─────┘                                                      │
                                                          flat fields:
                                                          • queue_location
                                                          • queue_speed
                                                          • bouncer_name
                                                          • confidence scores
```

**Django apps:**

| App | Purpose |
|-----|---------|
| `messages` | Scraping, AI parsing, raw + parsed message models |
| `queuedata` | Queue snapshots, location/speed aggregation |
| `schedule` | DJ lineup & currently-playing logic |
| `users` | API key auth |

**Celery Beat** runs `fetch_and_analyze_messages` every 2 minutes, but **only during Berghain hours** (Saturday 22:00 → Monday 11:00, Berlin time). Override this locally by setting `FORCE_FETCH=True` in `.env`.

**Queue location landmarks:**
- Main queue: `snake → wriezener_karree`
- Guestlist queue: `barriers → park`

---

## 2. Prerequisites

- [UV](https://docs.astral.sh/uv/) (`brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Python 3.11+ (UV can install this for you)
- Redis running locally
- PostgreSQL (only if using `development_psql` settings — SQLite is the default)
- API keys: OpenAI, Reddit, Telegram (see [Environment Variables](#7-environment-variables))

---

## 3. Initial Setup

```bash
cd ~/VisualStudioCodeProjects/bergline

# Install dependencies (creates .venv automatically)
uv sync

# Copy env template and fill in your keys
cp .env.example .env
```

---

## 4. Database

By default Bergline uses **SQLite** — no setup needed beyond running migrations.

To switch to **PostgreSQL**, uncomment these two lines in `.env`:

```env
DJANGO_SETTINGS_MODULE=bergline.settings.development_psql
DATABASE_URL=postgres://user:password@localhost:5432/bergline
```

### SQLite (default)

```bash
uv run python manage.py migrate
```

### PostgreSQL

```bash
brew services start postgresql
createdb bergline
uv run python manage.py migrate
```

### Create admin user (either database)

```bash
uv run python manage.py createsuperuser --email admin@example.com
```

---

## 5. Running the Project

### One command (recommended)

```bash
make run-bergline
```

This starts Redis, Celery worker, Celery Beat, and Django in one terminal. **Ctrl+C stops everything.**

Django runs on **http://localhost:8004**.

### Individual services

| Command | What it starts |
|---------|---------------|
| `make run` | Django dev server (port 8004) |
| `make run-redis` | Redis server |
| `make run-celery` | Celery worker |
| `make run-beat` | Celery Beat scheduler |

---

## 6. Manual Testing & Debugging

### Trigger a fetch manually

Don't wait for Beat — run the scrape + AI pipeline on demand:

```bash
make fetch
```

Or equivalently in the Django shell:

```bash
uv run python manage.py shell -c "from apps.messages.tasks import fetch_and_analyze_messages; fetch_and_analyze_messages()"
```

> Make sure `FORCE_FETCH=True` is set in `.env`, otherwise the task exits immediately outside Berghain hours.

### Inspect data in Django shell

```bash
uv run python manage.py shell
```

```python
from apps.messages.models import RawMessage, ParsedMessage

RawMessage.objects.count()
ParsedMessage.objects.filter(is_relevant=True).order_by('-created_at')[:5]
```

### Test API with curl

```bash
# Latest main queue
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8004/api/queue/main/latest/

# Submit a queue update
curl -X POST http://localhost:8004/api/messages/submit/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Queue is at the snake, moving fast"}'
```

### Django admin

Browse to **http://localhost:8004/admin/** (requires `createsuperuser` from step 4).

### Monitor Celery tasks

```bash
uv run celery -A bergline events
```

### Check Django configuration

```bash
uv run python manage.py check
```

---

## 7. Environment Variables

Edit your `.env` file with:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://localhost:5432/bergline
ALLOWED_HOSTS=*

# API Authentication
BERGLINE_API_KEY=your-api-key

# Redis / Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# OpenAI (for queue message analysis)
OPENAI_API_KEY=sk-...

# Reddit scraper
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=bergline/1.0

# Telegram scraper (Telethon)
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
TELEGRAM_PHONE=+33...
TELEGRAM_GROUPS=berghainberlin

# Force fetching outside Berghain hours (Sat 22h → Mon 11h)
FORCE_FETCH=True
```

> Set `FORCE_FETCH=True` for local testing — otherwise the fetch task only runs during Berghain operating hours (Saturday 22:00 → Monday 11:00, Berlin time).

---

## 8. API Endpoints

All endpoints require the `X-API-Key` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/queue/main/latest/` | Latest main queue snapshots |
| GET | `/api/queue/main/history/` | Main queue history |
| GET | `/api/queue/guestlist/latest/` | Latest guestlist snapshots |
| GET | `/api/queue/guestlist/history/` | Guestlist history |
| GET | `/api/schedule/now/` | Currently playing DJs |
| GET | `/api/schedule/` | Full DJ schedule |
| POST | `/api/messages/submit/` | Submit a queue update |
| GET | `/api/messages/` | List parsed messages |

---

## 9. Stopping Everything

With `make run-bergline`: just press **Ctrl+C** — all services stop together.

If you started services individually, Ctrl+C each terminal, then:

```bash
brew services stop redis
brew services stop postgresql
```

---

## 10. Troubleshooting

| Problem | Fix |
|---------|-----|
| `redis.exceptions.ConnectionError` | Make sure Redis is running: `redis-cli ping` |
| `OperationalError: database "bergline" does not exist` | Run `createdb bergline` |
| Celery tasks not running | Check Redis is up, check Celery worker logs |
| Telegram auth prompt | First run requires phone code — run `make fetch` manually once |
| Tasks return immediately | Set `FORCE_FETCH=True` in `.env` if testing outside Berghain hours |
