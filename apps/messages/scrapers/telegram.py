"""Telegram scraper for Berghain-related groups using Telethon."""

import logging
from datetime import datetime, timedelta, timezone as dt_timezone

from django.conf import settings
from django.utils import timezone
from telethon import TelegramClient

from apps.messages.models import RawMessage, Source
from apps.messages.scrapers.constants import FETCH_WINDOW_MINUTES, TELEGRAM_MESSAGE_LIMIT

logger = logging.getLogger(__name__)


def _get_telegram_client() -> TelegramClient:
    """Create and return a Telegram client."""
    return TelegramClient(
        "telethon",
        int(settings.TELEGRAM_API_ID),
        settings.TELEGRAM_API_HASH,
    )


async def _fetch_raw_from_group(client: TelegramClient, group: str, cutoff: datetime) -> list[dict]:
    """Fetch raw message data from a Telegram group. No DB access."""
    raw_messages = []

    entity = await client.get_entity(group)
    async for message in client.iter_messages(entity, limit=TELEGRAM_MESSAGE_LIMIT):
        if not message.text:
            continue
        if message.date < cutoff:
            break

        raw_messages.append({
            "id": message.id,
            "text": message.text,
            "date": message.date,
        })

    return raw_messages


def fetch_telegram_messages() -> list[RawMessage]:
    """Fetch new messages from configured Telegram groups.

    Fetches messages from the last FETCH_WINDOW_MINUTES from all groups
    defined in settings.TELEGRAM_GROUPS. Skips duplicates based on external_id.
    Returns a list of newly created RawMessage objects.
    """
    import asyncio

    source, _ = Source.objects.get_or_create(name="telegram")
    groups = settings.TELEGRAM_GROUPS
    cutoff = datetime.now(dt_timezone.utc) - timedelta(minutes=FETCH_WINDOW_MINUTES)

    # Async part: only Telethon calls, no Django ORM
    raw_by_group: dict[str, list[dict]] = {}

    async def _run():
        client = _get_telegram_client()
        await client.start(phone=settings.TELEGRAM_PHONE)
        for group in groups:
            try:
                raw_by_group[group] = await _fetch_raw_from_group(client, group, cutoff)
            except Exception as e:
                logger.error("Error fetching from Telegram group %s: %s", group, e)
        await client.disconnect()

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_run())
    finally:
        loop.close()

    # Sync part: all Django ORM operations
    all_messages = []
    for group, raw_msgs in raw_by_group.items():
        for raw in raw_msgs:
            external_id = f"tg_{group}_{raw['id']}"
            if RawMessage.objects.filter(source=source, external_id=external_id).exists():
                continue

            posted_at = timezone.make_aware(
                raw["date"].replace(tzinfo=None),
                timezone=dt_timezone.utc,
            ) if raw["date"].tzinfo is None else raw["date"]

            msg = RawMessage.objects.create(
                source=source,
                external_id=external_id,
                content=raw["text"],
                posted_at=posted_at,
            )
            all_messages.append(msg)
            logger.info("Saved Telegram message: %s", external_id)

    logger.info("Telegram scraper: fetched %d new messages.", len(all_messages))
    return all_messages
