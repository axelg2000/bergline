"""Celery tasks for fetching and analyzing messages."""

import logging
from datetime import datetime

from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def _is_within_berghain_window() -> bool:
    """Check if current time is within Berghain operating hours.

    Returns True if current Berlin time is between Saturday 22:00 and Monday 11:00.
    """
    berlin_now = timezone.localtime(timezone.now())
    weekday = berlin_now.weekday()  # 0=Monday, 5=Saturday, 6=Sunday
    hour = berlin_now.hour

    # Saturday 22:00+
    if weekday == 5 and hour >= 22:
        return True
    # All of Sunday
    if weekday == 6:
        return True
    # Monday before 11:00
    if weekday == 0 and hour < 11:
        return True

    return False


@shared_task
def fetch_and_analyze_messages():
    """Fetch messages from all sources and run AI analysis on each.

    This task runs every 2 minutes via Celery Beat. It exits immediately
    if the current time is outside the Berghain operating window
    (Saturday 22:00 to Monday 11:00, Berlin time).
    """
    if not settings.FORCE_FETCH and not _is_within_berghain_window():
        logger.info("Outside Berghain window, skipping fetch.")
        return "Outside operating window"

    from apps.messages.scrapers.reddit import fetch_reddit_messages
    from apps.messages.scrapers.telegram import fetch_telegram_messages
    from apps.messages.services.ai_analysis import analyze_message

    new_messages = []

    try:
        new_messages.extend(fetch_reddit_messages())
    except Exception as e:
        logger.error("Reddit scraper failed: %s", e)

    try:
        new_messages.extend(fetch_telegram_messages())
    except Exception as e:
        logger.error("Telegram scraper failed: %s", e)

    max_calls = getattr(settings, "OPENAI_MAX_CALLS_PER_CYCLE", 10)
    analyzed = 0
    for msg in new_messages:
        if analyzed >= max_calls:
            logger.warning("OpenAI rate limit reached (%d/%d), deferring remaining.", analyzed, max_calls)
            break
        try:
            result = analyze_message(msg)
            if result:
                analyzed += 1
        except Exception as e:
            logger.error("AI analysis failed for message %s: %s", msg.id, e)

    summary = f"Fetched {len(new_messages)} messages, analyzed {analyzed}."
    logger.info(summary)
    return summary
