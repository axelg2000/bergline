from supabase import create_client
from .config import SUPABASE_URL, SUPABASE_SERVICE_KEY

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def insert_raw_message(source: str, source_chat: str | None, source_message_id: str, ts, text: str):
    payload = {
        "source": source,
        "source_chat": source_chat,
        "source_message_id": source_message_id,
        "ts": ts,
        "text": text,
    }
    # Upsert on unique(source, source_message_id)
    res = sb.table("raw_messages").upsert(payload, on_conflict="source,source_message_id").execute()
    # Return the inserted/updated row id
    return res.data[0]["id"]

def insert_queue_signal(raw_message_id: str, ts, queue_location: str | None, confidence: float | None, model: str):
    payload = {
        "raw_message_id": raw_message_id,
        "ts": ts,
        "queue_location": queue_location,
        "confidence": confidence,
        "model": model,
    }
    sb.table("queue_signals").insert(payload).execute()