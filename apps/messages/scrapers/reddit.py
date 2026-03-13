"""Reddit scraper for r/Berghain_Community."""

import logging

import praw
from django.conf import settings
from django.utils import timezone

from apps.messages.models import RawMessage, Source
from apps.messages.scrapers.constants import FETCH_WINDOW_MINUTES, REDDIT_COMMENT_LIMIT, REDDIT_POST_LIMIT, SUBREDDIT

logger = logging.getLogger(__name__)


def _get_reddit_client() -> praw.Reddit:
    """Create and return a Reddit API client."""
    return praw.Reddit(
        client_id=settings.REDDIT_CLIENT_ID,
        client_secret=settings.REDDIT_CLIENT_SECRET,
        user_agent=settings.REDDIT_USER_AGENT,
    )


def fetch_reddit_messages() -> list[RawMessage]:
    """Fetch new posts and comments from r/Berghain_Community.

    Only processes messages from the last 2 minutes. Skips duplicates
    based on external_id. Returns a list of newly created RawMessage objects.
    """
    reddit = _get_reddit_client()
    subreddit = reddit.subreddit(SUBREDDIT)
    source, _ = Source.objects.get_or_create(name="reddit")
    cutoff = timezone.now() - timezone.timedelta(minutes=FETCH_WINDOW_MINUTES)
    new_messages = []

    # Fetch new posts
    for submission in subreddit.new(limit=REDDIT_POST_LIMIT):
        posted_at = timezone.datetime.fromtimestamp(
            submission.created_utc, tz=timezone.utc
        )
        if posted_at < cutoff:
            continue

        external_id = f"post_{submission.id}"
        if RawMessage.objects.filter(source=source, external_id=external_id).exists():
            continue

        content = f"{submission.title}\n\n{submission.selftext}" if submission.selftext else submission.title
        msg = RawMessage.objects.create(
            source=source,
            external_id=external_id,
            content=content,
            posted_at=posted_at,
        )
        new_messages.append(msg)
        logger.info("Saved Reddit post: %s", external_id)

    # Fetch new comments from recent posts
    for comment in subreddit.comments(limit=REDDIT_COMMENT_LIMIT):
        posted_at = timezone.datetime.fromtimestamp(
            comment.created_utc, tz=timezone.utc
        )
        if posted_at < cutoff:
            continue

        external_id = f"comment_{comment.id}"
        if RawMessage.objects.filter(source=source, external_id=external_id).exists():
            continue

        msg = RawMessage.objects.create(
            source=source,
            external_id=external_id,
            content=comment.body,
            posted_at=posted_at,
        )
        new_messages.append(msg)
        logger.info("Saved Reddit comment: %s", external_id)

    logger.info("Reddit scraper: fetched %d new messages.", len(new_messages))
    return new_messages
