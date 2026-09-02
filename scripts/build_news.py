#!/usr/bin/env python3
"""Build PSTA news pages, RSS, social queue, and newsletter queue from Markdown sources."""

from __future__ import annotations

import csv
import html
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Dict, Iterable, List
from urllib.parse import quote

SITE_URL = "https://www.publicservicetransformation.org"
SITE_PREFIX = ""
FEEDBACK_URL = "https://github.com/antlerboy/PSTA/issues/2"


@dataclass
class NewsItem:
    source: Path
    title: str
    date: str
    summary: str
    author: str
    social: str
    channels: List[str]
    newsletter: bool
    primary_link: str
    slug: str
    body: str

    @property
    def url(self) -> str:
        return f"{SITE_URL}/news/{self.slug}/"


def parse_front_matter(path: Path) -> tuple[Dict[str, str], str]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not text.startswith("---\n"):
        raise ValueError(f"Missing front matter in {path}")
    _, raw_meta, body = text.split("---\n", 2)
    meta: Dict[str, str] = {}
    for line in raw_meta.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        meta[key.strip().lower()] = value.replace('\\"', '"').replace("\\\\", "\\")
    return meta, body.strip()


def slugify(value: str) -> str:
    value = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", value.lower())
    value = re.sub(r"['’]", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:90] or "news"


def inline_markdown(value: str) -> str:
    value = html.escape(value, quote=False)
    value = re.sub(r"\[([^\]]+)\]\((https?://[^)]+|mailto:[^)]+|tel:[^)]+)\)", r'<a href="\2">\1</a>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", value)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    return value


def markdown_to_html(markdown: str) -> str:
    lines = markdown.replace("\r\n", "\n").splitlines()
    output: List[str] = []
    paragraph: List[str] = []
    list_type = ""

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{inline_markdown(' '.join(part.strip() for part in paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            output.append(f"</{list_type}>")
            list_type = ""

    for line in lines + [""]:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            close_list()
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1)) + 1
            output.append(f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>")
            continue
        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        numbered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if bullet or numbered:
            flush_paragraph()
            wanted = "ul" if bullet else "ol"
            if list_type != wanted:
                close_list()
                list_type = wanted
                output.append(f"<{wanted}>")
            output.append(f"<li>{inline_markdown((bullet or numbered).group(1))}</li>")
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            close_list()
            output.append(f"<blockquote><p>{inline_markdown(stripped.lstrip('> ').strip())}</p></blockquote>")
            continue
        paragraph.append(stripped)
    return "\n".join(output)


def load_items(source_dir: Path) -> List[NewsItem]:
    items: List[NewsItem] = []
    for path in sorted(source_dir.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        meta, body = parse_front_matter(path)
        if meta.get("draft", "false").lower() in {"true", "yes", "1"}:
            continue
        title = meta.get("title", "").strip()
        published = meta.get("date", "").strip()
        summary = meta.get("summary", "").strip()
        if not title or not published or not summary:
            raise ValueError(f"title, date, and summary are required in {path}")
        datetime.strptime(published, "%Y-%m-%d")
        channels = [part.strip() for part in meta.get("channels", "").split(",") if part.strip()]
        items.append(
            NewsItem(
                source=path,
                title=title,
                date=published,
                summary=summary,
                author=meta.get("author", "The PSTA") or "The PSTA",
                social=meta.get("social", summary) or summary,
                channels=channels,
                newsletter=meta.get("newsletter", "yes").lower() in {"yes", "true", "1"},
                primary_link=meta.get("primary_link", "").strip(),
                slug=slugify(path.stem),
                body=body,
            )
        )
    return sorted(items, key=lambda item: (item.date, item.title), reverse=True)


def logo_path(root: Path) -> str:
    marker = root / "assets" / "img" / "psta-logo-path.txt"
    if marker.exists():
        value = marker.read_text(encoding="utf-8").strip()
        if value:
            return value
    return f"{SITE_PREFIX}/assets/img/psta-logo-web.jpg"


def header(root: Path, title: str, description: str, canonical: str) -> str:
    logo = logo_path(root)
    return f'''<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="{html.escape(description, quote=True)}">
  <link rel="canonical" href="{html.escape(canonical, quote=True)}">
  <link rel="stylesheet" href="{SITE_PREFIX}/assets/css/site.css">
  <link rel="alternate" type="application/rss+xml" title="The PSTA news" href="{SITE_PREFIX}/news/feed.xml">
  <title>{html.escape(title)} | The Public Service Transformation Academy</title>
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<header class="site-header">
  <div class="shell header-inner">
    <a class="brand" href="{SITE_PREFIX}/" aria-label="The Public Service Transformation Academy home">
      <img src="{logo}" alt="The Public Service Transformation Academy">
    </a>
    <nav class="site-nav" aria-label="Primary navigation">
      <a href="{SITE_PREFIX}/programmes/">Programmes</a>
      <a href="{SITE_PREFIX}/tools/">Tools</a>
      <a href="{SITE_PREFIX}/in-house/">In-house work</a>
      <a href="{SITE_PREFIX}/community/">Community</a>
      <a href="{SITE_PREFIX}/partners/">Partners</a>
      <a href="{SITE_PREFIX}/news/" aria-current="page">News</a>
      <a href="{SITE_PREFIX}/about/">About</a>
      <a class="nav-cta" href="{SITE_PREFIX}/contact/">Talk to us</a>
    </nav>
  </div>
</header>'''


def footer() -> str:
    return f'''
<footer class="site-footer">
  <div class="shell footer-grid">
    <div class="footer-brand">
      <h2>The Public Service Transformation Academy</h2>
      <p>Applied learning, practical tools, and peer relationships for people making change work in public services.</p>
    </div>
    <div><h2>Explore</h2><a href="{SITE_PREFIX}/programmes/">Programmes</a><a href="{SITE_PREFIX}/tools/">Tools</a><a href="{SITE_PREFIX}/news/">News</a></div>
    <div><h2>Work with us</h2><a href="{SITE_PREFIX}/in-house/">In-house work</a><a href="{SITE_PREFIX}/partners/">Partners</a><a href="{SITE_PREFIX}/contact/">Contact</a></div>
    <div><h2>Assurance</h2><a href="{SITE_PREFIX}/accessibility/">Accessibility</a><a href="{SITE_PREFIX}/privacy/">Privacy</a><a href="{SITE_PREFIX}/policies/">Policies</a></div>
  </div>
  <div class="shell footer-legal">
    <span>Registered Social Enterprise. The Public Service Transformation Academy Limited is a company limited by guarantee, registered in England and Wales, company number 10046052. VAT number 244 4776 87.</span>
    <span>7 Bell Yard, London, WC2A 2JR, UK</span>
  </div>
</footer>
<a class="iteration-secret-link" href="{FEEDBACK_URL}" aria-label="Website feedback" title="Website feedback"></a>
<script>document.addEventListener('keydown',function(e){{if(e.altKey&&e.shiftKey&&e.key.toLowerCase()==='n'){{window.location.href='{FEEDBACK_URL}';}}}});</script>
</body></html>'''


def build_item_page(root: Path, item: NewsItem) -> None:
    target = root / "news" / item.slug / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    primary = ""
    if item.primary_link:
        primary = f'<p><a class="button" href="{html.escape(item.primary_link, quote=True)}">Find out more</a></p>'
    content = f'''{header(root, item.title, item.summary, item.url)}
<main id="main">
  <section class="section section-wash">
    <div class="shell">
      <p class="eyebrow">News and insight</p>
      <h1>{html.escape(item.title)}</h1>
      <p class="lede">{html.escape(item.summary)}</p>
      <p><time datetime="{item.date}">{datetime.strptime(item.date, '%Y-%m-%d').strftime('%-d %B %Y')}</time> · {html.escape(item.author)}</p>
    </div>
  </section>
  <article class="section">
    <div class="shell" style="max-width:820px">
      {markdown_to_html(item.body)}
      {primary}
      <p><a class="text-link" href="{SITE_PREFIX}/news/">Back to all news</a></p>
    </div>
  </article>
</main>
{footer()}'''
    target.write_text(content, encoding="utf-8")


def build_index(root: Path, items: Iterable[NewsItem]) -> None:
    cards = []
    for item in items:
        display_date = datetime.strptime(item.date, "%Y-%m-%d").strftime("%-d %B %Y")
        cards.append(f'''<article class="card">
  <div class="card-topline"><time datetime="{item.date}">{display_date}</time><span class="status">News</span></div>
  <h2><a href="{SITE_PREFIX}/news/{item.slug}/">{html.escape(item.title)}</a></h2>
  <p>{html.escape(item.summary)}</p>
  <a class="text-link" href="{SITE_PREFIX}/news/{item.slug}/">Read the full item</a>
</article>''')
    content = f'''{header(root, "News and insight", "News, programme announcements, practical insight, and resources from the PSTA.", f"{SITE_URL}/news/")}
<main id="main">
  <section class="section section-wash"><div class="shell"><p class="eyebrow">News and insight</p><h1>News from the PSTA</h1><p class="lede">Programme announcements, practical insight, useful resources, and work from the PSTA's partners and community.</p><p><a href="{SITE_PREFIX}/news/feed.xml">Subscribe to the RSS feed</a></p></div></section>
  <section class="section"><div class="shell"><div class="card-grid">{''.join(cards) if cards else '<p>No news items have been published yet.</p>'}</div></div></section>
</main>
{footer()}'''
    target = root / "news" / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_rss(root: Path, items: List[NewsItem]) -> None:
    rows = []
    for item in items[:30]:
        dt = datetime.strptime(item.date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        rows.append(f'''<item>
<title>{html.escape(item.title)}</title>
<link>{item.url}</link>
<guid isPermaLink="true">{item.url}</guid>
<pubDate>{format_datetime(dt)}</pubDate>
<description>{html.escape(item.summary)}</description>
</item>''')
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>The PSTA news and insight</title>
<link>{SITE_URL}/news/</link>
<description>News, programmes, tools, and practical insight from the Public Service Transformation Academy.</description>
<language>en-gb</language>
{''.join(rows)}
</channel></rss>'''
    (root / "news" / "feed.xml").write_text(rss, encoding="utf-8")


def add_news_to_navigation(root: Path) -> None:
    for path in root.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        if f'href="{SITE_PREFIX}/news/' not in text and "site-nav" in text:
            marker = f'<a href="{SITE_PREFIX}/about/">'
            if marker in text:
                text = text.replace(marker, f'<a href="{SITE_PREFIX}/news/">News</a>\n      {marker}', 1)
            else:
                marker = f'<a class="nav-cta" href="{SITE_PREFIX}/contact/">'
                if marker in text:
                    text = text.replace(marker, f'<a href="{SITE_PREFIX}/news/">News</a>\n      {marker}', 1)
        path.write_text(text, encoding="utf-8")


def add_latest_to_home(root: Path, items: List[NewsItem]) -> None:
    home = root / "index.html"
    if not home.exists() or not items:
        return
    text = home.read_text(encoding="utf-8")
    text = re.sub(r"<!-- PSTA_NEWS_START -->.*?<!-- PSTA_NEWS_END -->", "", text, flags=re.S)
    cards = []
    for item in items[:3]:
        display_date = datetime.strptime(item.date, "%Y-%m-%d").strftime("%-d %B %Y")
        cards.append(f'''<article class="card"><div class="card-topline"><time datetime="{item.date}">{display_date}</time><span class="status">News</span></div><h3><a href="{SITE_PREFIX}/news/{item.slug}/">{html.escape(item.title)}</a></h3><p>{html.escape(item.summary)}</p><a class="text-link" href="{SITE_PREFIX}/news/{item.slug}/">Read more</a></article>''')
    section = f'''<!-- PSTA_NEWS_START -->
<section class="section section-wash" aria-labelledby="latest-news-heading"><div class="shell"><div class="section-heading"><div><p class="eyebrow">News and insight</p><h2 id="latest-news-heading">Latest from the PSTA</h2></div><p><a class="text-link" href="{SITE_PREFIX}/news/">See all news</a></p></div><div class="card-grid">{''.join(cards)}</div></div></section>
<!-- PSTA_NEWS_END -->'''
    if "</main>" in text:
        text = text.replace("</main>", section + "\n</main>", 1)
    else:
        text = text.replace("</body>", section + "\n</body>", 1)
    home.write_text(text, encoding="utf-8")


def build_queues(repo_root: Path, items: List[NewsItem]) -> None:
    editorial = repo_root / "editorial"
    editorial.mkdir(parents=True, exist_ok=True)
    social_rows = []
    for item in items:
        try:
            source = item.source.relative_to(repo_root).as_posix()
        except ValueError:
            source = item.source.as_posix()
        social_rows.append({
            "date": item.date,
            "title": item.title,
            "url": item.url,
            "post": item.social,
            "channels": item.channels,
            "source": source,
            "status": "queued",
        })
    (editorial / "social-queue.json").write_text(json.dumps(social_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with (editorial / "newsletter-queue.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "title", "summary", "url", "author", "status"])
        writer.writeheader()
        for item in items:
            if item.newsletter:
                writer.writerow({"date": item.date, "title": item.title, "summary": item.summary, "url": item.url, "author": item.author, "status": "queued"})


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "deploy")
    repo_root = Path.cwd()
    source_dir = repo_root / "content" / "news"
    source_dir.mkdir(parents=True, exist_ok=True)
    items = load_items(source_dir)
    for item in items:
        build_item_page(root, item)
    build_index(root, items)
    build_rss(root, items)
    add_news_to_navigation(root)
    # The curated home-page panel owns the single public 'latest' section.
    # News remains available through the panel, the news index, and RSS.
    build_queues(repo_root, items)
    print(f"Built {len(items)} news item(s)")


if __name__ == "__main__":
    main()
