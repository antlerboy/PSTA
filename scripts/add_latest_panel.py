#!/usr/bin/env python3
"""Add the curated PSTA 'Latest news and social media' panel to the built home page."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from curated_latest import load_contract, render_cards, runtime_markup, write_assets

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "deploy")
REPO = Path(__file__).resolve().parents[1]
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


def render_panel(contract: dict) -> str:
    cards = render_cards(contract["selected"], "psta-latest", external_tabs=True)
    runtime = runtime_markup(contract, "psta-latest", external_tabs=True, asset_prefix=PREFIX.rstrip("/"))
    return f'''\n<section class="section psta-latest-panel" aria-labelledby="psta-latest-heading" data-latest-panel>\n  <div class="psta-latest-inner">\n    <div class="psta-latest-panel-heading">\n      <div>\n        <p class="psta-latest-eyebrow">News, social media, and useful things</p>\n        <h2 id="psta-latest-heading">Latest from the PSTA</h2>\n      </div>\n      <p>Webinars, programmes, and recent learning for public service practitioners. <a href="/news/">See all news</a></p>\n    </div>\n    <div class="psta-latest-grid" data-latest-grid>\n      {cards}\n    </div>\n  </div>\n{runtime}\n</section>\n'''


def patch_home(contract: dict) -> None:
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

    panel = render_panel(contract)
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
    contract = load_contract(REPO)
    CSS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CSS_PATH.write_text(CSS.strip() + "\n", encoding="utf-8")
    write_assets(REPO, ROOT, contract)
    patch_home(contract)
    print("Added PSTA latest panel:", ", ".join(item["topic"] for item in contract["selected"]))
    if contract["review_needed"]:
        print("Editorial review due; inspect assets/data/latest.json")


if __name__ == "__main__":
    main()
