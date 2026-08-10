#!/usr/bin/env python3
"""Turn the structured '[Publish news]' GitHub issue form into a news Markdown file."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Dict


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"['’]", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:90] or "news"


def parse_issue_form(body: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    current = ""
    lines = body.replace("\r\n", "\n").split("\n")
    for line in lines:
        heading = re.match(r"^###\s+(.+?)\s*$", line)
        if heading:
            current = heading.group(1).strip().lower()
            fields[current] = ""
            continue
        if current:
            fields[current] += line + "\n"
    return {key: value.strip() for key, value in fields.items()}


def field(fields: Dict[str, str], name: str, default: str = "") -> str:
    return fields.get(name.lower(), default).strip()


def clean_checklist(value: str) -> str:
    choices = []
    for line in value.splitlines():
        match = re.match(r"^-\s+\[[xX]\]\s+(.+)$", line.strip())
        if match:
            choices.append(match.group(1).strip())
    return ", ".join(choices)


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip() + '"'


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: news_from_issue.py <github-event.json>")

    event = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    issue = event.get("issue", {})
    fields = parse_issue_form(issue.get("body", ""))

    title = field(fields, "Public title")
    summary = field(fields, "Summary")
    story = field(fields, "Full story")
    primary_link = field(fields, "Primary link")
    author = field(fields, "Author", "The PSTA") or "The PSTA"
    publication_date = field(fields, "Publication date") or date.today().isoformat()
    social = field(fields, "Suggested social post") or summary
    channels = clean_checklist(field(fields, "Social channels"))
    newsletter_answer = field(fields, "Include in the newsletter queue", "Yes")
    newsletter = "yes" if newsletter_answer.lower().startswith("yes") else "no"

    if not title or not summary or not story:
        raise SystemExit("The public title, summary, and full story are required.")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", publication_date):
        raise SystemExit("Publication date must be YYYY-MM-DD.")

    slug = slugify(title)
    target = Path("content/news") / f"{publication_date}-{slug}.md"
    if target.exists():
        target = Path("content/news") / f"{publication_date}-{slug}-{issue.get('number', 'item')}.md"
    target.parent.mkdir(parents=True, exist_ok=True)

    front_matter = [
        "---",
        f"title: {yaml_quote(title)}",
        f"date: {publication_date}",
        f"summary: {yaml_quote(summary)}",
        f"author: {yaml_quote(author)}",
        f"social: {yaml_quote(social)}",
        f"channels: {yaml_quote(channels)}",
        f"newsletter: {newsletter}",
        "draft: false",
    ]
    if primary_link and primary_link.lower() not in {"_no response_", "none", "n/a"}:
        front_matter.append(f"primary_link: {yaml_quote(primary_link)}")
    front_matter.extend(["---", "", story.strip(), ""])
    target.write_text("\n".join(front_matter), encoding="utf-8")
    Path("/tmp/psta-news-path.txt").write_text(str(target), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
