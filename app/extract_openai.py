import json
from openai import OpenAI
from .config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_queue_location(text: str) -> dict | None:
    """
    Returns dict with:
      has_queue_location: bool
      queue_location: free text short phrase or null
      confidence: float 0..1
    """
    prompt = f"""
You extract Berghain QUEUE LOCATION from ONE message.

Be recall-heavy: if the message even vaguely indicates where the queue is, set has_queue_location=true.

Return STRICT JSON only (no markdown, no extra text).

Rules:
- "has_queue_location": true only if the message indicates a place/landmark/position for the queue.
- "queue_location": a SHORT phrase (1–6 words) describing where the queue is.
  Examples: "kiosk", "near kiosk", "wriezener karree", "metro sign", "by the snake", "past the concrete blocks".
- If no location is mentioned, set has_queue_location=false and queue_location=null.
- "confidence": 0 to 1 (higher when explicit).

JSON schema:
{{
  "has_queue_location": boolean,
  "queue_location": string|null,
  "confidence": number
}}

Message:
{text}
""".strip()

    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )
        return json.loads(resp.output_text.strip())
    except Exception:
        return None