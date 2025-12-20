import asyncio
import requests
from .config import REDDIT_THREAD_ID

REDDIT_URL = "https://www.reddit.com/comments/{id}.json?sort=new"

async def start_reddit_poller(queue: asyncio.Queue, poll_seconds: int = 20):
    seen = set()

    while True:
        try:
            url = REDDIT_URL.format(id=REDDIT_THREAD_ID)
            r = requests.get(url, headers={"User-Agent": "bergline/0.1"}, timeout=20)
            r.raise_for_status()
            data = r.json()

            # data[1] = comments listing
            comments = data[1]["data"]["children"]
            for c in comments:
                if c.get("kind") != "t1":
                    continue
                d = c["data"]
                cid = d["id"]
                if cid in seen:
                    continue
                seen.add(cid)

                body = (d.get("body") or "").strip()
                if not body:
                    continue

                # created_utc is seconds
                ts_iso = __import__("datetime").datetime.fromtimestamp(
                    d["created_utc"],
                    tz=__import__("datetime").timezone.utc
                ).isoformat()

                await queue.put({
                    "source": "reddit",
                    "source_chat": f"thread:{REDDIT_THREAD_ID}",
                    "source_message_id": cid,
                    "ts": ts_iso,
                    "text": body,
                })

        except Exception:
            # keep it running no matter what
            pass

        await asyncio.sleep(poll_seconds)