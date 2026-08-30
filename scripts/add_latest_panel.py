#!/usr/bin/env python3
"""Add the curated PSTA 'Latest news and social media' panel to the built home page."""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "deploy")
REPO = Path(__file__).resolve().parents[1]
DATA_PATH = REPO / "content/latest.json"
CSS_PATH = ROOT / "assets/css/latest-panel.css"
HOME_PATH = ROOT / "index.html"
PREFIX = "/PSTA/"

CSS = r"""
/* One PSTA-native home-page panel for news, social posts, and useful resources. */
.psta-latest-panel {
  background: var(--wash, #f3f6ff);
}
.psta-latest-inner {
  width: min(calc(100% - 40px), var(--shell, 1180px));
  margin: auto;
}
.psta-latest-panel-heading {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(13rem, 24rem);
  gap: 1.5rem;
  align-items: end;
  margin-bottom: 1.5rem;
}
.psta-latest-panel .psta-latest-eyebrow {
  margin: 0 0 .35rem;
  color: var(--blue, #0d19ff);
  font-size: .78rem;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.psta-latest-panel h2 {
  margin: 0;
  font-size: clamp(1.6rem, 3vw, 2.25rem);
  line-height: 1.12;
}
.psta-latest-panel-heading > p {
  margin: 0;
  font-size: .96rem;
  line-height: 1.45;
}
.psta-latest-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}
.psta-latest-grid article {
  display: flex;
  min-height: 15rem;
  flex-direction: column;
  padding: 1.25rem;
  border: 1px solid var(--line, #d9dce6);
  border-top: .4rem solid var(--blue, #0d19ff);
  border-radius: 18px;
  background: #fff;
}
.psta-latest-grid article:nth-child(2) {
  border-top-color: var(--light, #33b2ff);
}
.psta-latest-grid article:nth-child(3) {
  border-top-color: var(--gold, #ff8000);
}
.psta-latest-source {
  margin: 0 0 .65rem;
  color: var(--blue, #0d19ff);
  font-size: .76rem;
  font-weight: 700;
  letter-spacing: .06em;
  text-transform: uppercase;
}
.psta-latest-grid h3 {
  margin: 0 0 .7rem;
  font-size: 1.16rem;
  line-height: 1.25;
}
.psta-latest-grid h3 a {
  color: inherit;
  text-decoration-thickness: .07em;
  text-underline-offset: .14em;
}
.psta-latest-grid article > p:not(.psta-latest-source) {
  margin: 0 0 1rem;
  line-height: 1.45;
}
.psta-latest-read {
  margin-top: auto;
  font-weight: 700;
}
@media (max-width: 820px) {
  .psta-latest-panel-heading,
  .psta-latest-grid {
    grid-template-columns: 1fr;
  }
  .psta-latest-grid article {
    min-height: 0;
  }
}
@media (max-width: 760px) {
  .psta-latest-inner {
    width: min(calc(100% - 28px), var(--shell, 1180px));
  }
}
"""


def load_items() -> list[dict[str, str]]:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) != 3:
        raise SystemExit("content/latest.json must contain exactly three items")

    required = {"source", "title", "summary", "href", "topic"}
    items: list[dict[str, str]] = []
    for index, raw in enumerate(data, start=1):
        if not isinstance(raw, dict) or not required.issubset(raw):
            raise SystemExit(f"Latest item {index} is missing one of: {', '.join(sorted(required))}")
        item = {key: str(raw[key]).strip() for key in required}
        if not all(item.values()):
            raise SystemExit(f"Latest item {index} contains an empty value")
        items.append(item)
    topics = [str(raw["topic"]).strip().casefold() for raw in data]
    hrefs = [item["href"].casefold() for item in items]
    if len(set(topics)) != len(topics):
        raise SystemExit("Latest items must cover three different topics")
    if len(set(hrefs)) != len(hrefs):
        raise SystemExit("Latest items must use three different links")
    return items


def link_attrs(href: str) -> str:
    parsed = urlparse(href)
    if parsed.scheme in {"http", "https"}:
        return ' target="_blank" rel="noreferrer"'
    return ""


def render_panel(items: list[dict[str, str]]) -> str:
    cards = []
    for item in items:
        source = html.escape(item["source"])
        title = html.escape(item["title"])
        summary = html.escape(item["summary"])
        href = html.escape(item["href"], quote=True)
        attrs = link_attrs(item["href"])
        cards.append(
            f'<article>\n'
            f'  <p class="psta-latest-source">{source}</p>\n'
            f'  <h3><a href="{href}"{attrs}>{title}</a></h3>\n'
            f'  <p>{summary}</p>\n'
            f'  <a class="psta-latest-read" href="{href}"{attrs}>Read it <span aria-hidden="true">↗</span></a>\n'
            f'</article>'
        )

    return f'''\n<section class="section psta-latest-panel" aria-labelledby="psta-latest-heading">\n  <div class="psta-latest-inner">\n    <div class="psta-latest-panel-heading">\n      <div>\n        <p class="psta-latest-eyebrow">News, social media, and useful things</p>\n        <h2 id="psta-latest-heading">Latest from the PSTA</h2>\n      </div>\n      <p>Three current things selected for relevance, each on a different topic.</p>\n    </div>\n    <div class="psta-latest-grid">\n      {''.join(cards)}\n    </div>\n  </div>\n</section>\n'''


def patch_home(items: list[dict[str, str]]) -> None:
    if not HOME_PATH.exists():
        raise SystemExit("Built home page is missing")

    markup = HOME_PATH.read_text(encoding="utf-8", errors="ignore")
    if "psta-latest-panel" in markup:
        raise SystemExit("Latest panel is already present in the built home page")

    stylesheet = f'<link rel="stylesheet" href="{PREFIX}assets/css/latest-panel.css">'
    lower = markup.lower()
    if "</head>" not in lower:
        raise SystemExit("Could not find </head> in built home page")
    position = lower.find("</head>")
    markup = markup[:position] + f'  {stylesheet}\n' + markup[position:]

    panel = render_panel(items)
    lower = markup.lower()
    cta_match = re.search(r'<section\b[^>]*class=["\'][^"\']*\bcta-panel\b', markup, flags=re.I)
    if cta_match:
        position = cta_match.start()
        markup = markup[:position] + panel + markup[position:]
    elif "</main>" in lower:
        position = lower.rfind("</main>")
        markup = markup[:position] + panel + markup[position:]
    elif "</body>" in lower:
        position = lower.rfind("</body>")
        markup = markup[:position] + panel + markup[position:]
    else:
        raise SystemExit("Could not find a safe insertion point in built home page")

    HOME_PATH.write_text(markup, encoding="utf-8")


def main() -> None:
    items = load_items()
    CSS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CSS_PATH.write_text(CSS.strip() + "\n", encoding="utf-8")
    patch_home(items)
    print("Added PSTA latest panel with", len(items), "curated items")


if __name__ == "__main__":
    main()
