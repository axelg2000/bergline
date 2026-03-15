# Bergline

REST API backend that tracks the Berghain nightclub queue in real time. Collects data from Reddit, Telegram, and user-submitted forms, runs AI analysis on each message, and stores structured queue data.

## Tech Stack

- Django + Django REST Framework
- PostgreSQL
- Celery + Celery Beat (Redis broker)
- OpenAI GPT-4o-mini for message analysis

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis

### Installation

```bash
# Clone and enter project
git clone <repo-url> bergline && cd bergline

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Create database
createdb bergline

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

### Running Celery

```bash
# Worker
celery -A bergline worker -l info

# Beat scheduler (runs fetch every 2 minutes during Berghain hours)
celery -A bergline beat -l info
```

## API Endpoints

All endpoints require `X-API-Key` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/queue/main/latest/` | Most recent main queue snapshots |
| GET | `/api/queue/guestlist/latest/` | Most recent guestlist snapshots |
| GET | `/api/queue/main/history/` | Historical main queue data |
| GET | `/api/queue/guestlist/history/` | Historical guestlist data |
| GET | `/api/schedule/now/` | Currently playing DJs per stage |
| GET | `/api/schedule/` | Full DJ schedule |
| POST | `/api/messages/submit/` | Submit a message (API key) |
| GET | `/api/messages/` | List parsed messages (admin) |

## How It Works

1. Celery Beat triggers `fetch_and_analyze_messages` every 2 minutes (Saturday 22:00 - Monday 11:00 Berlin time)
2. Reddit and Telegram scrapers fetch new messages
3. Each message is sent to GPT-4o-mini for structured analysis
4. Queue location, speed, and bouncer info are extracted and stored as snapshots
5. The API serves this data to the frontend
