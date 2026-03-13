"""AI analysis pipeline for raw messages using OpenAI GPT-4o-mini."""

import json
import logging

from django.conf import settings
from django.utils import timezone
from openai import OpenAI

from apps.messages.models import MessageTag, ParsedMessage, RawMessage
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
- Include a "confidence_score" from 0.0 to 1.0 for each tag.
- For queue_location tags, include "queue_type" as either "main" or "guestlist".

Respond in this exact JSON format:
{
  "is_relevant": true/false,
  "tags": [
    {
      "tag_type": "queue_location",
      "queue_type": "main" or "guestlist",
      "extracted_value": "location_value",
      "confidence_score": 0.0-1.0
    },
    {
      "tag_type": "queue_speed",
      "extracted_value": "fast/slow/not_moving",
      "confidence_score": 0.0-1.0
    },
    {
      "tag_type": "bouncer_name",
      "extracted_value": "description or name",
      "confidence_score": 0.0-1.0
    }
  ]
}

Only include tags that are present in the message. The tags array can be empty if is_relevant is false."""


def analyze_message(raw_message: RawMessage) -> ParsedMessage | None:
    """Analyze a raw message using OpenAI and create ParsedMessage + tags.

    Takes a RawMessage, sends its content to GPT-4o-mini, parses the structured
    JSON response, and creates the corresponding ParsedMessage, MessageTag, and
    queue snapshot records.

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
    )

    if not parsed.is_relevant:
        return parsed

    for tag_data in result.get("tags", []):
        tag = MessageTag.objects.create(
            parsed_message=parsed,
            tag_type=tag_data["tag_type"],
            extracted_value=tag_data["extracted_value"],
            confidence_score=tag_data.get("confidence_score", 0.5),
        )
        _create_snapshot_if_needed(tag, tag_data)

    return parsed


def _create_snapshot_if_needed(tag: MessageTag, tag_data: dict) -> None:
    """Create a queue snapshot if the tag is a queue_location."""
    if tag.tag_type != "queue_location":
        return

    queue_type = tag_data.get("queue_type", "")
    location = tag.extracted_value
    now = timezone.now()

    if queue_type == "main" and location in MAIN_QUEUE_LOCATIONS:
        MainQueueSnapshot.objects.create(
            message_tag=tag,
            location=location,
            confidence_score=tag.confidence_score,
            recorded_at=now,
        )
    elif queue_type == "guestlist" and location in GUESTLIST_LOCATIONS:
        GuestlistSnapshot.objects.create(
            message_tag=tag,
            location=location,
            confidence_score=tag.confidence_score,
            recorded_at=now,
        )
