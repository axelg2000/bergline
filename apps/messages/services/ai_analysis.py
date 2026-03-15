"""AI analysis pipeline for raw messages using OpenAI GPT-4o-mini."""

import json
import logging

from django.conf import settings
from django.utils import timezone
from openai import OpenAI

from apps.messages.models import ParsedMessage, RawMessage
from apps.queuedata.models import GuestlistSnapshot, MainQueueSnapshot

logger = logging.getLogger(__name__)

AI_MODEL = "gpt-4o-mini"

MAIN_QUEUE_LOCATIONS = [
    "snake", "concrete_blocks", "magic_cube", "kiosk",
    "20m_behind_kiosk", "wriezener_karree", "metro_sign",
]

GUESTLIST_LOCATIONS = [
    "barriers", "love_sculpture", "garten_door", "atm", "park",
]

SYSTEM_PROMPT = """You are an AI that analyzes messages about the Berghain nightclub queue in Berlin.
Given a message, extract structured queue information. Respond ONLY with valid JSON, no extra text.

Rules:
- Set "is_relevant" to false if the message contains no useful queue information.
- For "queue_location", classify ONLY from these allowed values:
  Main queue: snake, concrete_blocks, magic_cube, kiosk, 20m_behind_kiosk, wriezener_karree, metro_sign
  Guestlist queue: barriers, love_sculpture, garten_door, atm, park
- For "queue_speed", use one of: fast, slow, not_moving, or null if unknown.
- For "bouncer_name", extract the bouncer's name or physical description exactly as written.
  Only "Sven" and "Mischa" are real names. All other bouncers must be stored as physical descriptions
  or celebrity nicknames (e.g. "German Vin Diesel", "braids", "tunnel earring", "septum piercing").
- Include a "confidence_score" from 0.0 to 1.0 for each field.
- For queue_location, include "queue_type" as either "main" or "guestlist".

Respond in this exact JSON format:
{
  "is_relevant": true/false,
  "queue_location": "location_value or null",
  "queue_location_confidence": 0.0-1.0,
  "queue_type": "main" or "guestlist",
  "queue_speed": "fast/slow/not_moving or null",
  "queue_speed_confidence": 0.0-1.0,
  "bouncer_name": "description or name or null",
  "bouncer_name_confidence": 0.0-1.0
}

Only include non-null values for fields that are present in the message."""


def analyze_message(raw_message: RawMessage) -> ParsedMessage | None:
    """Analyze a raw message using OpenAI and create ParsedMessage + snapshots.

    Takes a RawMessage, sends its content to GPT-4o-mini, parses the structured
    JSON response, and creates the corresponding ParsedMessage and queue snapshot records.

    Returns the ParsedMessage if created, or None if already parsed.
    """
    if hasattr(raw_message, "parsed"):
        logger.info("Message %s already parsed, skipping.", raw_message.id)
        return None

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": raw_message.content},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
    except (json.JSONDecodeError, Exception) as e:
        logger.error("AI analysis failed for message %s: %s", raw_message.id, e)
        return None

    parsed = ParsedMessage.objects.create(
        raw_message=raw_message,
        is_relevant=result.get("is_relevant", False),
        ai_model=AI_MODEL,
        queue_location=result.get("queue_location") or "",
        queue_location_confidence=result.get("queue_location_confidence"),
        queue_type=result.get("queue_type") or "",
        queue_speed=result.get("queue_speed") or "",
        queue_speed_confidence=result.get("queue_speed_confidence"),
        bouncer_name=result.get("bouncer_name") or "",
        bouncer_name_confidence=result.get("bouncer_name_confidence"),
    )

    if parsed.is_relevant and parsed.queue_location:
        _create_snapshot_if_needed(parsed)

    return parsed


def _create_snapshot_if_needed(parsed: ParsedMessage) -> None:
    """Create a queue snapshot if the parsed message has a queue_location."""
    location = parsed.queue_location
    now = timezone.now()

    if parsed.queue_type == "main" and location in MAIN_QUEUE_LOCATIONS:
        MainQueueSnapshot.objects.create(
            parsed_message=parsed,
            location=location,
            confidence_score=parsed.queue_location_confidence or 0.5,
            recorded_at=now,
        )
    elif parsed.queue_type == "guestlist" and location in GUESTLIST_LOCATIONS:
        GuestlistSnapshot.objects.create(
            parsed_message=parsed,
            location=location,
            confidence_score=parsed.queue_location_confidence or 0.5,
            recorded_at=now,
        )
