#!/usr/bin/env python3
"""Send eligible PSTA news to an optional distribution webhook.

The receiving automation can route the payload to Buffer and the newsletter workflow.
If NEWS_DISTRIBUTION_WEBHOOK_URL is not configured, the website and repository queues
still build. Report the skipped delivery explicitly: a successful optional workflow
does not mean that Buffer posts or newsletter items have been created.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List
from urllib.request import Request, urlopen


def report_distribution(status: str, message: str, count: int = 0) -> None:
    """Expose the actual delivery outcome in logs and the GitHub Actions summary."""
    print(message)
    if status == "skipped_no_webhook" and os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::warning title=PSTA social delivery not confirmed::{message}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if summary:
        with Path(summary).open("a", encoding="utf-8") as handle:
            handle.write(f"### PSTA distribution\n\nStatus: `{status}`. Eligible items: {count}.\n\n{message}\n\n")
    output = os.environ.get("GITHUB_OUTPUT", "").strip()
    if output:
        with Path(output).open("a", encoding="utf-8") as handle:
            handle.write(f"distribution_status={status}\neligible_items={count}\n")


def changed_news_files(before: str, after: str) -> List[Path]:
    if before and set(before) != {"0"}:
        command = ["git", "diff", "--name-only", before, after, "--", "content/news/*.md"]
    else:
        command = ["git", "show", "--pretty=", "--name-only", after, "--", "content/news/*.md"]
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip() and not line.lower().endswith("readme.md")]


def parse_front_matter(path: Path) -> tuple[Dict[str, str], str]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return {}, text
    _, raw_meta, body = text.split("---\n", 2)
    meta: Dict[str, str] = {}
    for line in raw_meta.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        meta[key.strip().lower()] = value.replace('\\"', '"').replace("\\\\", "\\")
    return meta, body.strip()


def slugify(filename: str) -> str:
    stem = Path(filename).stem
    parts = stem.split("-", 3)
    return parts[3] if len(parts) == 4 and all(part.isdigit() for part in parts[:3]) else stem


def main() -> None:
    webhook = os.environ.get("NEWS_DISTRIBUTION_WEBHOOK_URL", "").strip()
    before = os.environ.get("BEFORE_SHA", "").strip()
    after = os.environ.get("AFTER_SHA", "HEAD").strip() or "HEAD"
    files = changed_news_files(before, after)
    if not files:
        report_distribution("no_news_changes", "No changed PSTA news source files to distribute.")
        return

    payload_items = []
    for path in files:
        if not path.exists():
            continue
        meta, body = parse_front_matter(path)
        # Website corrections must not silently resend an existing campaign.
        if meta.get("distribute", "yes").lower() in {"no", "false", "0"}:
            continue
        if meta.get("draft", "false").lower() in {"true", "yes", "1"}:
            continue
        slug = slugify(path.name)
        channels = [part.strip() for part in meta.get("channels", "").split(",") if part.strip()]
        newsletter = meta.get("newsletter", "yes").lower() in {"yes", "true", "1"}
        if not channels and not newsletter:
            continue
        payload_items.append({
            "source_file": str(path),
            "title": meta.get("title", ""),
            "date": meta.get("date", ""),
            "summary": meta.get("summary", ""),
            "full_story_markdown": body,
            "author": meta.get("author", "The PSTA"),
            "social_post": meta.get("social", meta.get("summary", "")),
            "channels": channels,
            "newsletter": newsletter,
            "primary_link": meta.get("primary_link", ""),
            "website_url": f"https://www.publicservicetransformation.org/news/{slug}/",
            "social_queue_url": "https://github.com/antlerboy/PSTA/blob/main/editorial/social-queue.json",
            "newsletter_queue_url": "https://github.com/antlerboy/PSTA/blob/main/editorial/newsletter-queue.csv",
        })

    if not payload_items:
        report_distribution("nothing_to_distribute", "No eligible PSTA news items: drafts, distribution opt-outs, and items without selected destinations are skipped.")
        return
    if not webhook:
        report_distribution(
            "skipped_no_webhook",
            "NEWS_DISTRIBUTION_WEBHOOK_URL is not configured. No webhook was called and this workflow created no Buffer posts or newsletter deliveries. "
            "The repository queues remain available to the separate cloud polling task; check its distribution ledger for confirmed Buffer post IDs. "
            "See docs/NEWS_AND_SOCIAL_PUBLISHING.md.",
            len(payload_items),
        )
        return

    payload = json.dumps({
        "event": "psta_news_published",
        "repository": os.environ.get("GITHUB_REPOSITORY", "antlerboy/PSTA"),
        "commit": after,
        "items": payload_items,
    }, ensure_ascii=False).encode("utf-8")
    request = Request(webhook, data=payload, headers={"Content-Type": "application/json", "User-Agent": "PSTA-news-publisher/1.0"}, method="POST")
    with urlopen(request, timeout=30) as response:
        status = getattr(response, "status", 200)
        if status < 200 or status >= 300:
            raise RuntimeError(f"Distribution webhook returned HTTP {status}")
        report_distribution(
            "delivered_to_webhook",
            f"The distribution webhook accepted {len(payload_items)} PSTA news item(s) (HTTP {status}). "
            "This confirms receipt by the webhook, not publication or scheduling in Buffer; check the receiver's ledger for post IDs.",
            len(payload_items),
        )


if __name__ == "__main__":
    main()
