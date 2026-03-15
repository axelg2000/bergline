# Bergline Project - Code Review Memory

## Project Overview
- Django 5.2 REST API tracking Berghain nightclub queue
- Data sources: Reddit (PRAW), Telegram (Telethon), user form submissions
- AI analysis: OpenAI GPT-4o-mini
- Task scheduling: Celery + Redis + django-celery-beat
- Auth: API key (X-API-Key header) + Google OAuth2 ID tokens
- DB: PostgreSQL via psycopg2-binary

## Key File Paths
- Settings: `/bergline/settings.py`
- API key auth: `/apps/messages/authentication.py`
- Google auth: `/apps/users/authentication.py`
- AI analysis: `/apps/messages/services/ai_analysis.py`
- Scrapers: `/apps/messages/scrapers/{reddit,telegram}.py`
- Views: `/apps/messages/views.py`, `/apps/queuedata/views.py`, `/apps/schedule/views.py`

## Critical Security Findings (2026-03-15)
- CRITICAL: Real `.env` with live secrets on disk (OpenAI key, Telegram creds, API key)
- CRITICAL: `telethon.session` committed in initial git commit (contains Telegram auth session)
- HIGH: API key comparison uses `!=` instead of `hmac.compare_digest()` (timing attack)
- HIGH: `ALLOWED_HOSTS = ["*"]` default in production settings
- HIGH: Google OAuth has no `audience` parameter validation
- HIGH: No rate limiting on any endpoint
- MEDIUM: No CORS, HSTS, or cookie security headers configured
- See `security-findings.md` for full detail
