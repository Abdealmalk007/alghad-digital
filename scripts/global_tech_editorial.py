#!/usr/bin/env python3
"""Editorial ranking for five original technology RSS publishers.

No article rewriting or scraping. Deterministic title-based relevance signals,
real RSS publication timestamps, and publisher attribution only.
Python 3.12+ standard library.
"""
from __future__ import annotations

from datetime import datetime, timezone
import re

GLOBAL_TECH_IDS = ("theverge", "techcrunch", "arstechnica", "wired", "engadget")

PROMOTIONAL = re.compile(
    r"\b(?:promo codes?|coupon codes?|coupons?|discount codes?|deals? of the day|"
    r"flash sales?|black friday deals?|cyber monday deals?|"
    r"save (?:up to|\$|[0-9])|best (?:prices?|deals?|sales?)|"
    r"buy now|gift guides?|shopping guides?|sponsored posts?|"
    r"our favorite (?:deals?|offers?)|shopping|giveaways?|"
    r"cashback|price drops?)\b",
    re.IGNORECASE,
)
SIGNIFICANT = re.compile(
    r"\b(?:announc(?:e|es|ed|ement)|launch(?:es|ed)?|unveil(?:s|ed)?|"
    r"release(?:s|d)?|rollout|rolls? out|introduc(?:e|es|ed)|"
    r"breakthrough|research|regulat(?:ion|or|ory)|ruling|lawsuit|"
    r"breach|vulnerabilit(?:y|ies)|security flaw|exploit|"
    r"hack(?:ing|ed|ers?)?|data leak|acquisit(?:ion|ions)|"
    r"open.source|update(?:s|d)?|new chip|new model|"
    r"major outage|partnership|antitrust)\b",
    re.IGNORECASE,
)
TECHNOLOGY = re.compile(
    r"\b(?:AI|artificial intelligence|LLM|OpenAI|ChatGPT|Gemini|Claude|"
    r"Microsoft|Google|Apple|Android|iPhone|Nvidia|AMD|Intel|"
    r"Windows|Linux|software|cybersecurity|privacy|"
    r"robot(?:s|ics)?|semiconductor|chip(?:s|sets)?|"
    r"datacenter|data center|cloud|GPU|processor|"
    r"quantum|electric vehicle|autonomous|app(?:s|lication)?)\b",
    re.IGNORECASE,
)
LESS_NEWSWORTHY = re.compile(
    r"\b(?:hands.on|review|reviews|how.to|guide|tutorial|"
    r"buying|best .* of 20\d{2}|where to (?:buy|watch)|"
    r"streaming now|roundup|opinion)\b",
    re.IGNORECASE,
)


def published_time(value: str) -> datetime | None:
    try:
        instant = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if instant.tzinfo is None:
            return None
        return instant.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def eligible_title(title: str, published_at: str, now: datetime | None = None) -> bool:
    """Exclude stale and promotional results; do not invent replacements."""
    now = now or datetime.now(timezone.utc)
    stamp = published_time(published_at)
    if not stamp or not isinstance(title, str):
        return False
    age = (now - stamp).total_seconds()
    return 15 <= len(title.strip()) <= 175 and -36 * 3600 <= age <= 7 * 86400 and not PROMOTIONAL.search(title)


def relevance_score(title: str, published_at: str, now: datetime | None = None) -> int:
    """Heuristic editorial relevance, not a claim of universal importance."""
    now = now or datetime.now(timezone.utc)
    stamp = published_time(published_at)
    if stamp is None or PROMOTIONAL.search(title):
        return -100
    hours = max(0, (now - stamp).total_seconds() / 3600)
    recency = 4 if hours <= 12 else 3 if hours <= 24 else 2 if hours <= 48 else 1 if hours <= 72 else 0
    return (
        recency + 5 * bool(SIGNIFICANT.search(title))
        + 3 * bool(TECHNOLOGY.search(title))
        - 5 * bool(LESS_NEWSWORTHY.search(title))
    )


def publisher_highlights(articles: list[dict], each: int = 2,
                         now: datetime | None = None) -> list[dict]:
    """Round-robin up to two significant items per available publisher."""
    now = now or datetime.now(timezone.utc)
    results: list[dict] = []
    seen_urls: set[str] = set()
    for publisher in GLOBAL_TECH_IDS:
        relevant = (
            article for article in articles
            if article.get("source") == publisher
            and eligible_title(article.get("title", ""), article.get("published_at", ""), now)
        )
        ranked = sorted(
            relevant,
            key=lambda a: (
                relevance_score(a["title"], a["published_at"], now),
                a["published_at"],
            ),
            reverse=True,
        )
        for article in ranked[:each]:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                results.append(article)
    return results
