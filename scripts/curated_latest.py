"""Select three current editorial items, with approved evergreen replacements."""

from __future__ import annotations

import html
import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

REQUIRED = ("topic", "source", "title", "summary", "href", "link_label", "reviewed_on")
REVIEW_DAYS = 14


def timestamp(value: str) -> datetime:
    if not isinstance(value, str) or "T" not in value:
        raise ValueError("Dates with a time must be ISO 8601 timestamps with a timezone")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def validate(items: list, label: str, fallback: bool = False) -> list[dict]:
    if not isinstance(items, list) or (len(items) < 3 if fallback else len(items) != 3):
        raise ValueError(f"{label} must contain {'at least' if fallback else 'exactly'} three items")
    topics, links = set(), set()
    clean = []
    for raw in items:
        if not isinstance(raw, dict) or any(not isinstance(raw.get(k), str) or not raw[k].strip() for k in REQUIRED):
            raise ValueError(f"{label}: every item needs non-empty strings for {', '.join(REQUIRED)}")
        item = dict(raw)
        item.update({key: raw[key].strip() for key in REQUIRED})
        topic, link = item["topic"].casefold(), item["href"].casefold()
        if topic in topics or link in links:
            raise ValueError(f"{label}: items must have distinct topics and links")
        parsed = urlparse(item["href"])
        if not ((parsed.scheme == "https" and parsed.netloc) or (item["href"].startswith("/") and not item["href"].startswith("//"))):
            raise ValueError(f"{label}: links must be HTTPS or root-relative")
        if any(char in item["href"] for char in "\r\n\t\\"):
            raise ValueError(f"{label}: invalid link")
        date.fromisoformat(item["reviewed_on"])
        evergreen = item.get("evergreen") is True
        if evergreen == bool(item.get("expires_at")):
            raise ValueError(f"{label}: choose either evergreen:true or expires_at")
        if fallback and (not evergreen or item.get("valid_from")):
            raise ValueError("Fallbacks must be immediately available evergreen items")
        if item.get("expires_at"):
            timestamp(item["expires_at"])
        if item.get("valid_from"):
            start = timestamp(item["valid_from"])
            if item.get("expires_at") and start >= timestamp(item["expires_at"]):
                raise ValueError("valid_from must be earlier than expires_at")
        topics.add(topic)
        links.add(link)
        clean.append(item)
    return clean


def select(candidates: list[dict], now: datetime) -> list[dict]:
    if now.tzinfo is None:
        raise ValueError("Selection time must include a timezone")
    selected, topics, links = [], set(), set()
    for item in candidates:
        if item.get("valid_from") and now < timestamp(item["valid_from"]):
            continue
        if item.get("expires_at") and now >= timestamp(item["expires_at"]):
            continue
        topic, link = item["topic"].casefold(), item["href"].casefold()
        if topic in topics or link in links:
            continue
        selected.append(item)
        topics.add(topic)
        links.add(link)
        if len(selected) == 3:
            return selected
    raise ValueError("Not enough distinct current items for the three-item panel")


def prepare(primary: list, fallbacks: list, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    primary = validate(primary, "content/latest.json")
    fallbacks = validate(fallbacks, "content/latest-fallbacks.json", fallback=True)
    candidates = [dict(item, selection_role=role) for role, group in (("primary", primary), ("fallback", fallbacks)) for item in group]
    selected = select(candidates, now)
    transitions = [timestamp(item[key]) for item in candidates for key in ("valid_from", "expires_at") if item.get(key) and timestamp(item[key]) > now]
    fallback_topics = [item["topic"] for item in selected if item["selection_role"] == "fallback"]
    review_due = [item["topic"] for item in primary if now.date() >= date.fromisoformat(item["reviewed_on"]) + timedelta(days=REVIEW_DAYS)]
    expired = [item["topic"] for item in primary if item.get("expires_at") and now >= timestamp(item["expires_at"])]
    return {
        "schema_version": 1,
        "selection_as_of": now.isoformat(),
        "source_commit": os.environ.get("GITHUB_SHA"),
        "source_paths": ["content/latest.json", "content/latest-fallbacks.json"],
        "review_after_days": REVIEW_DAYS,
        "review_needed": bool(fallback_topics or review_due or expired),
        "review_due_topics": review_due,
        "expired_topics": expired,
        "fallback_topics": fallback_topics,
        "next_transition_at": min(transitions).isoformat() if transitions else None,
        "selected": selected,
        "candidates": candidates,
    }


def load_contract(repo: Path, now: datetime | None = None) -> dict:
    return prepare(json.loads((repo / "content/latest.json").read_text()), json.loads((repo / "content/latest-fallbacks.json").read_text()), now)


def render_cards(items: list[dict], prefix: str, external_tabs: bool = False) -> str:
    cards = []
    for item in items:
        external = item["href"].startswith("https://")
        attrs = ' target="_blank" rel="noopener noreferrer"' if external_tabs and external else ""
        href = html.escape(item["href"], quote=True)
        cards.append(
            '<article>'
            f'<p class="{prefix}-source">{html.escape(item["source"])}</p>'
            f'<h3><a href="{href}"{attrs}>{html.escape(item["title"])}</a></h3>'
            f'<p>{html.escape(item["summary"])}</p>'
            f'<a class="{prefix}-read" href="{href}"{attrs}>{html.escape(item["link_label"])} <span aria-hidden="true">{"↗" if external else "→"}</span></a>'
            '</article>'
        )
    return "\n".join(cards)


def runtime_markup(contract: dict, prefix: str, external_tabs: bool = False, asset_prefix: str = "") -> str:
    payload = dict(contract, class_prefix=prefix, external_tabs=external_tabs)
    data = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return f'<script type="application/json" data-latest-data>{data}</script>\n<script src="{asset_prefix}/assets/js/curated-latest.js" defer></script>'


def write_assets(repo: Path, root: Path, contract: dict) -> None:
    target = root / "assets/data/latest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n")
    script = root / "assets/js/curated-latest.js"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text((repo / "scripts/curated-latest.js").read_text())
