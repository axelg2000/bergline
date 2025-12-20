from datetime import datetime, timedelta, timezone
from .supabase_db import sb

def get_latest_estimate(window_minutes: int = 30):
    since = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)

    # Pull recent signals
    res = (
        sb.table("queue_signals")
        .select("ts,queue_location,confidence")
        .gte("ts", since.isoformat())
        .order("ts", desc=True)
        .execute()
    )
    rows = res.data or []
    if not rows:
        return {"in the last": window_minutes, "location": None, "counts": {}}

    # simple weighted vote
    scores = {}
    for r in rows:
        loc = r["queue_location"]
        if not loc:
            continue
        conf = r.get("confidence") or 0.4
        scores[loc] = scores.get(loc, 0.0) + float(conf)

    if not scores:
        return {"in the last": window_minutes, "location": None, "counts": {}}

    best = max(scores.items(), key=lambda x: x[1])[0]
    return {"in the last": window_minutes, "location": best, "scores": scores}