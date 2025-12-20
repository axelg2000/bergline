import asyncio
from fastapi import FastAPI, HTTPException, Header

from .ingest_telegram import start_telegram_listener
from .ingest_reddit import start_reddit_poller
from .extract_openai import extract_queue_location
from .supabase_db import insert_raw_message, insert_queue_signal
from .aggregate import get_latest_estimate
import os

API_KEY = os.environ.get("BERGLINE_API_KEY")
app = FastAPI()
q: asyncio.Queue


async def processor_loop(queue: asyncio.Queue):
    while True:
        item = await queue.get()
        try:
            raw_id = insert_raw_message(
                source=item["source"],
                source_chat=item["source_chat"],
                source_message_id=item["source_message_id"],
                ts=item["ts"],
                text=item["text"],
            )

            parsed = extract_queue_location(item["text"])
            if parsed and parsed.get("has_queue_location"):
                insert_queue_signal(
                    raw_message_id=raw_id,
                    ts=item["ts"],
                    queue_location=parsed.get("queue_location"),
                    confidence=float(parsed.get("confidence") or 0.5),
                    model="gpt-4o-mini",
                )

        except Exception:
            # ignore failures for MVP (DB insert, OpenAI, etc.)
            pass
        finally:
            queue.task_done()


@app.on_event("startup")
async def startup():
    global q
    q = asyncio.Queue(maxsize=2000)
    asyncio.create_task(processor_loop(q))
    asyncio.create_task(start_reddit_poller(q, poll_seconds=20))
    asyncio.create_task(start_telegram_listener(q))


@app.get("/v1/queue/latest")
def queue_latest(
    window: int = 30,
    x_api_key: str = Header(default="")
):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return get_latest_estimate(window_minutes=window)