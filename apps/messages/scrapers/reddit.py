"""Reddit scraper for r/Bergline using public JSON endpoints."""

import logging
from datetime import datetime, timezone as dt_timezone

import httpx
from django.utils import timezone

from apps.messages.models import RawMessage, Source
from apps.messages.scrapers.constants import FETCH_WINDOW_MINUTES, REDDIT_COMMENT_LIMIT, REDDIT_POST_LIMIT, SUBREDDIT

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "bergline/1.0"}
BASE_URL = "https://www.reddit.com/r"


def fetch_reddit_messages() -> list[RawMessage]:
    """Fetch new posts and comments from r/Bergline via public JSON endpoints.

    Only processes messages from the last FETCH_WINDOW_MINUTES. Skips duplicates
    based on external_id. Returns a list of newly created RawMessage objects.
    """
    source, _ = Source.objects.get_or_create(name="reddit")
    cutoff = timezone.now() - timezone.timedelta(minutes=FETCH_WINDOW_MINUTES)
    new_messages = []

    # Fetch new posts
    try:
        resp = httpx.get(
            f"{BASE_URL}/{SUBREDDIT}/new.json",
            params={"limit": REDDIT_POST_LIMIT},
            headers=HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        posts = resp.json()["data"]["children"]
    except (httpx.HTTPError, KeyError, ValueError) as e:
        logger.error("Failed to fetch Reddit posts: %s", e)
        posts = []

    for item in posts:
        post = item["data"]
        posted_at = datetime.fromtimestamp(post["created_utc"], tz=dt_timezone.utc)
        if posted_at < cutoff:
            continue

        external_id = f"post_{post['id']}"
        if RawMessage.objects.filter(source=source, external_id=external_id).exists():
            continue

        selftext = post.get("selftext", "")
        content = f"{post['title']}\n\n{selftext}" if selftext else post["title"]
        msg = RawMessage.objects.create(
            source=source,
            external_id=external_id,
            content=content,
            posted_at=posted_at,
        )
        new_messages.append(msg)
        logger.info("Saved Reddit post: %s", external_id)

    # Fetch comments per-post (subreddit-level /comments.json doesn't work for small subs)
    recent_post_ids = [item["data"]["id"] for item in posts if datetime.fromtimestamp(item["data"]["created_utc"], tz=dt_timezone.utc) >= cutoff]

    for post_id in recent_post_ids:
        try:
            resp = httpx.get(
                f"https://www.reddit.com/comments/{post_id}.json",
                params={"limit": REDDIT_COMMENT_LIMIT},
                headers=HEADERS,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            comments = [c for c in data[1]["data"]["children"] if c["kind"] == "t1"]
        except (httpx.HTTPError, KeyError, ValueError, IndexError) as e:
            logger.error("Failed to fetch comments for post %s: %s", post_id, e)
            continue

        for item in comments:
            comment = item["data"]
            posted_at = datetime.fromtimestamp(comment["created_utc"], tz=dt_timezone.utc)
            if posted_at < cutoff:
                continue

            external_id = f"comment_{comment['id']}"
            if RawMessage.objects.filter(source=source, external_id=external_id).exists():
                continue

            msg = RawMessage.objects.create(
                source=source,
                external_id=external_id,
                content=comment["body"],
                posted_at=posted_at,
            )
            new_messages.append(msg)
            logger.info("Saved Reddit comment: %s", external_id)

    logger.info("Reddit scraper: fetched %d new messages.", len(new_messages))
    return new_messages
