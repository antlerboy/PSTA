#!/usr/bin/env python3
"""Add low-key PSTA website Easter eggs after the static site has been assembled."""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "deploy")
PREFIX = "/PSTA/"
CSS_PATH = ROOT / "assets/css/easter-eggs.css"
JS_PATH = ROOT / "assets/js/easter-eggs.js"

RESOURCE_WEIGHTS = {
    "commissioning compass": 8,
    "self-assessment": 6,
    "resource": 5,
    "tool": 5,
    "guide": 4,
    "workbook": 4,
    "playbook": 4,
    "framework": 3,
    "download": 2,
    "systems thinking": 1,
    "commissioning": 1,
}
EXCLUDED_TOP_LEVEL = {
    "404",
    "accessibility",
    "about",
    "contact",
    "news",
    "partners",
    "policies",
    "privacy",
    "programmes",
    "privacy-policy",
    "iteration-notes-7d4f9c2b81e6a5",
}


def plain_text(markup: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", markup, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def page_title(markup: str, fallback: str) -> str:
    for pattern in (r"<h1\b[^>]*>(.*?)</h1>", r"<title\b[^>]*>(.*?)</title>"):
        match = re.search(pattern, markup, flags=re.I | re.S)
        if match:
            value = plain_text(match.group(1))
            if value:
                return value
    return fallback


def page_url(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if rel.name == "index.html":
        parent = rel.parent.as_posix().strip(".")
        if not parent:
            return PREFIX
        return f"{PREFIX}{parent.strip('/')}/"
    return f"{PREFIX}{rel.as_posix()}"


def resource_pool() -> list[dict[str, str]]:
    scored: list[tuple[int, str, str]] = []
    fallback: list[tuple[str, str]] = []

    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if rel.name == "404.html" or rel == Path("index.html"):
            continue
        top = rel.parts[0] if len(rel.parts) > 1 else ""
        if top in {"assets", *EXCLUDED_TOP_LEVEL}:
            continue

        markup = path.read_text(encoding="utf-8", errors="ignore")
        title = page_title(markup, rel.parent.name.replace("-", " ").title())
        text = plain_text(markup).lower()
        url = page_url(path)
        fallback.append((title, url))

        score = sum(weight for phrase, weight in RESOURCE_WEIGHTS.items() if phrase in text)
        if score >= 4:
            scored.append((score, title, url))

    source = sorted(scored, key=lambda item: (-item[0], item[1].lower()))
    if len(source) < 8:
        seen = {url for _, _, url in source}
        for title, url in sorted(fallback, key=lambda item: item[0].lower()):
            if url not in seen:
                source.append((0, title, url))
                seen.add(url)
            if len(source) >= 24:
                break

    resources = [{"title": title, "url": url} for _, title, url in source[:40]]
    if not resources:
        resources = [{"title": "Public Service Transformation Academy", "url": PREFIX}]
    return resources


CSS = r"""
/* PSTA Easter eggs: intentionally quiet until someone pokes them. */
.psta-compass-egg {
  width: 1.85rem;
  height: 1.85rem;
  margin-left: .35rem;
  padding: 0;
  border: 1px solid currentColor;
  border-radius: 50%;
  background: transparent;
  color: inherit;
  opacity: .32;
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
  cursor: pointer;
  transition: opacity .2s ease, transform .2s ease, background .2s ease;
}
.psta-compass-egg:hover,
.psta-compass-egg:focus-visible {
  opacity: .78;
}
.psta-compass-egg .psta-compass-north {
  position: absolute;
  top: .08rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: .46rem;
  font-weight: 700;
  line-height: 1;
}
.psta-compass-egg .psta-compass-needle {
  display: block;
  font-size: .82rem;
  line-height: 1;
  transform-origin: 50% 55%;
  transition: transform .62s cubic-bezier(.2,.8,.2,1);
}
.psta-egg-dialog {
  max-width: min(34rem, calc(100vw - 2rem));
  border: 0;
  border-radius: .75rem;
  padding: 0;
  box-shadow: 0 1rem 4rem rgba(0,0,0,.28);
}
.psta-egg-dialog::backdrop {
  background: rgba(0,0,0,.44);
}
.psta-egg-dialog-inner {
  padding: 1.4rem 1.5rem 1.5rem;
}
.psta-egg-dialog h2 {
  margin: 0 2.25rem .75rem 0;
  font-size: 1.28rem;
}
.psta-egg-dialog p {
  margin: .55rem 0;
}
.psta-egg-dialog .psta-egg-question {
  margin-top: 1rem;
  padding: .85rem 1rem;
  border-left: .22rem solid currentColor;
  background: rgba(127,127,127,.08);
}
.psta-egg-dialog .psta-egg-actions {
  margin-top: 1rem;
  display: flex;
  gap: .65rem;
  flex-wrap: wrap;
  align-items: center;
}
.psta-egg-dialog button,
.psta-egg-dialog a,
.psta-edge-404 a,
.psta-edge-404 button {
  font: inherit;
}
.psta-egg-close {
  position: absolute;
  top: .6rem;
  right: .7rem;
  border: 0;
  background: transparent;
  cursor: pointer;
  font-size: 1.5rem;
  line-height: 1;
}
.psta-edge-404 {
  min-height: 72vh;
  display: grid;
  place-items: center;
  padding: 3rem 1.25rem;
}
.psta-edge-404-card {
  width: min(42rem, 100%);
}
.psta-edge-404-logo {
  width: min(19rem, 78vw);
  height: auto;
  display: block;
  margin-bottom: 2.5rem;
}
.psta-edge-404 h1 {
  font-size: clamp(2rem, 7vw, 4.4rem);
  line-height: .98;
  margin: 0 0 1rem;
}
.psta-edge-404 p {
  max-width: 36rem;
}
.psta-edge-404-actions {
  display: flex;
  flex-wrap: wrap;
  gap: .8rem;
  margin-top: 1.6rem;
}
.psta-edge-404-actions a,
.psta-edge-404-actions button {
  display: inline-block;
  padding: .72rem 1rem;
  border: 1px solid currentColor;
  border-radius: .35rem;
  background: transparent;
  color: inherit;
  text-decoration: none;
  cursor: pointer;
}
@media (prefers-reduced-motion: reduce) {
  .psta-compass-egg,
  .psta-compass-egg .psta-compass-needle {
    transition: none;
  }
}
"""

COMPASS_PROMPTS = [
    {
        "aspect": "Whole system design",
        "question": "What would have to be true for the whole system, not just your organisation, to improve?",
    },
    {
        "aspect": "Relationships and organisation across the system",
        "question": "Which relationship, hand-off, or boundary is quietly deciding the outcome?",
    },
    {
        "aspect": "Capacity, capability, and confidence",
        "question": "Where does the system lack the capacity or confidence to act on what it already knows?",
    },
    {
        "aspect": "Citizen, place, and outcome centred",
        "question": "Whose outcomes are actually shaping the work?",
    },
    {
        "aspect": "Information, insight, and innovation",
        "question": "What signal are you not seeing, or seeing too late?",
    },
    {
        "aspect": "Making room to make a difference",
        "question": "Where are governance, finance, procurement, or politics narrowing your room for manoeuvre?",
    },
    {
        "aspect": "Commissioning process",
        "question": "Which part of the commissioning process has quietly become the purpose?",
    },
    {
        "aspect": "Models and tactics",
        "question": "Which commissioning approach fits this place now, rather than the one you habitually reach for?",
    },
]


def make_js(resources: list[dict[str, str]]) -> str:
    return f"""(() => {{
  'use strict';

  const resources = {json.dumps(resources, ensure_ascii=False)};
  const prompts = {json.dumps(COMPASS_PROMPTS, ensure_ascii=False)};
  window.PSTA_EGG_RESOURCES = resources;

  const pick = items => items[Math.floor(Math.random() * items.length)];

  function showCompassDialog(sourceHref) {{
    const prompt = pick(prompts);
    let dialog = document.getElementById('psta-compass-dialog');
    if (!dialog) {{
      dialog = document.createElement('dialog');
      dialog.id = 'psta-compass-dialog';
      dialog.className = 'psta-egg-dialog';
      dialog.innerHTML = `
        <div class="psta-egg-dialog-inner">
          <button class="psta-egg-close" type="button" aria-label="Close">&times;</button>
          <h2>Going round in circles is diagnostic information.</h2>
          <p>Try a Commissioning Compass question:</p>
          <div class="psta-egg-question">
            <strong data-psta-aspect></strong>
            <p data-psta-question></p>
          </div>
          <div class="psta-egg-actions">
            <a data-psta-compass-link href="https://link.redquadrant.com/commissioningcompass">Open the Commissioning Compass</a>
            <button type="button" data-psta-another>Another question</button>
          </div>
        </div>`;
      document.body.appendChild(dialog);
      dialog.querySelector('.psta-egg-close').addEventListener('click', () => dialog.close());
      dialog.addEventListener('click', event => {{
        if (event.target === dialog) dialog.close();
      }});
      dialog.querySelector('[data-psta-another]').addEventListener('click', () => {{
        const next = pick(prompts);
        dialog.querySelector('[data-psta-aspect]').textContent = next.aspect;
        dialog.querySelector('[data-psta-question]').textContent = next.question;
      }});
    }}

    dialog.querySelector('[data-psta-aspect]').textContent = prompt.aspect;
    dialog.querySelector('[data-psta-question]').textContent = prompt.question;
    const link = dialog.querySelector('[data-psta-compass-link]');
    if (sourceHref && !sourceHref.startsWith('#') && !sourceHref.toLowerCase().startsWith('javascript:')) {{
      link.href = sourceHref;
    }}
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open', 'open');
  }}

  function addCompassMisbehaviour() {{
    const candidates = [...document.querySelectorAll('a, button, img')].filter(el => {{
      const haystack = [
        el.textContent || '',
        el.getAttribute('href') || '',
        el.getAttribute('title') || '',
        el.getAttribute('alt') || '',
        el.getAttribute('aria-label') || ''
      ].join(' ').toLowerCase();
      return haystack.includes('commissioning') && haystack.includes('compass');
    }});

    const anchors = [];
    for (const el of candidates) {{
      const anchor = el.matches('a') ? el : el.closest('a');
      const host = anchor || el;
      if (!host || anchors.includes(host)) continue;
      anchors.push(host);

      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'psta-compass-egg';
      button.setAttribute('aria-label', 'Spin the Commissioning Compass');
      button.setAttribute('title', 'Commissioning Compass');
      button.innerHTML = '<span class="psta-compass-north">N</span><span class="psta-compass-needle" aria-hidden="true">&#9650;</span>';

      let spins = 0;
      const threshold = 4 + Math.floor(Math.random() * 4);
      const needle = button.querySelector('.psta-compass-needle');
      button.addEventListener('click', event => {{
        event.preventDefault();
        event.stopPropagation();
        spins += 1;
        needle.style.transform = `rotate(${{spins * 437}}deg)`;
        if (spins >= threshold) {{
          spins = 0;
          const href = anchor ? anchor.getAttribute('href') : '';
          window.setTimeout(() => showCompassDialog(href), 260);
        }}
      }});

      host.insertAdjacentElement('afterend', button);
      if (anchors.length >= 3) break;
    }}
  }}

  function wireLearningEdge() {{
    const trigger = document.querySelector('[data-psta-random-resource]');
    if (!trigger) return;
    trigger.addEventListener('click', event => {{
      event.preventDefault();
      const choice = pick(resources);
      if (choice && choice.url) window.location.assign(choice.url);
    }});
  }}

  document.addEventListener('DOMContentLoaded', () => {{
    addCompassMisbehaviour();
    wireLearningEdge();
  }});
}})();
"""


def make_404() -> str:
    return f"""<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>You appear to be at the learning edge. | Public Service Transformation Academy</title>
  <link rel="stylesheet" href="{PREFIX}assets/css/site.css">
  <link rel="stylesheet" href="{PREFIX}assets/css/easter-eggs.css">
</head>
<body>
  <main class="psta-edge-404">
    <div class="psta-edge-404-card">
      <a href="{PREFIX}" aria-label="Public Service Transformation Academy home">
        <img class="psta-edge-404-logo" src="{PREFIX}assets/img/psta-logo-official.svg" alt="Public Service Transformation Academy">
      </a>
      <h1>You appear to be at the learning edge.</h1>
      <p>The page you expected is not here. That may or may not be useful information.</p>
      <div class="psta-edge-404-actions">
        <a href="{PREFIX}">Return to what I thought I knew</a>
        <button type="button" data-psta-random-resource>Show me something unexpected</button>
      </div>
    </div>
  </main>
  <script defer src="{PREFIX}assets/js/easter-eggs.js"></script>
</body>
</html>
"""


def inject_assets(path: Path) -> None:
    markup = path.read_text(encoding="utf-8", errors="ignore")
    css_tag = f'<link rel="stylesheet" href="{PREFIX}assets/css/easter-eggs.css">'
    js_tag = f'<script defer src="{PREFIX}assets/js/easter-eggs.js"></script>'

    if "easter-eggs.css" not in markup:
        if re.search(r"</head>", markup, flags=re.I):
            markup = re.sub(r"</head>", css_tag + "\n</head>", markup, count=1, flags=re.I)
        else:
            markup = css_tag + "\n" + markup
    if "easter-eggs.js" not in markup:
        if re.search(r"</body>", markup, flags=re.I):
            markup = re.sub(r"</body>", js_tag + "\n</body>", markup, count=1, flags=re.I)
        else:
            markup = markup + "\n" + js_tag

    path.write_text(markup, encoding="utf-8")


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Site root does not exist: {ROOT}")

    resources = resource_pool()
    CSS_PATH.parent.mkdir(parents=True, exist_ok=True)
    JS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CSS_PATH.write_text(CSS.strip() + "\n", encoding="utf-8")
    JS_PATH.write_text(make_js(resources), encoding="utf-8")
    (ROOT / "404.html").write_text(make_404(), encoding="utf-8")

    for page in ROOT.rglob("*.html"):
        inject_assets(page)

    print(f"Installed PSTA Easter eggs with {len(resources)} random-resource destinations")


if __name__ == "__main__":
    main()
