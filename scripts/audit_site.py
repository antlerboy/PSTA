#!/usr/bin/env python3
"""Fail the release build when public-site quality or migration checks regress."""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree


ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "deploy").resolve()
DOMAIN = "https://www.publicservicetransformation.org"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.title_parts: list[str] = []
        self.in_title = False
        self.description = ""
        self.robots = ""
        self.canonical = ""
        self.h1_count = 0
        self.main_count = 0
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.links: list[tuple[str, str, str]] = []
        self.assets: list[str] = []
        self.images_without_alt = 0
        self.site_nav = False
        self.nav_toggle = False

    @staticmethod
    def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {key.lower(): value or "" for key, value in attrs}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = self.attrs_dict(attrs)
        if tag == "html":
            self.lang = values.get("lang", "")
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            name = values.get("name", "").lower()
            if name == "description":
                self.description = values.get("content", "")
            elif name == "robots":
                self.robots = values.get("content", "")
        if tag == "link":
            rel = set(values.get("rel", "").lower().split())
            if "canonical" in rel:
                self.canonical = values.get("href", "")
            if rel.intersection({"stylesheet", "icon"}) and values.get("href"):
                self.assets.append(values["href"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "main":
            self.main_count += 1
        element_id = values.get("id")
        if element_id:
            if element_id in self.ids:
                self.duplicate_ids.add(element_id)
            self.ids.add(element_id)
        classes = set(values.get("class", "").split())
        if "site-nav" in classes:
            self.site_nav = True
        if "nav-toggle" in classes:
            self.nav_toggle = True
        if tag == "a":
            self.links.append((values.get("href", ""), values.get("target", ""), values.get("rel", "")))
        if tag == "img":
            if "alt" not in values:
                self.images_without_alt += 1
            if values.get("src"):
                self.assets.append(values["src"])
        if tag == "script" and values.get("src"):
            self.assets.append(values["src"])

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()


def route_for(page: Path) -> str:
    rel = page.relative_to(ROOT).as_posix()
    return "/" if rel == "index.html" else "/" + rel.removesuffix("index.html")


def internal_target(raw: str, current_page: Path) -> tuple[Path, str] | None:
    if not raw or raw.startswith(("mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlsplit(raw)
    if parsed.scheme in {"http", "https"}:
        if f"{parsed.scheme}://{parsed.netloc}" != DOMAIN:
            return None
        path = parsed.path
    elif parsed.scheme or parsed.netloc:
        return None
    else:
        path = parsed.path
    fragment = unquote(parsed.fragment)
    if not path:
        return current_page, fragment
    path = unquote(path)
    if path.startswith("/"):
        relative = path.lstrip("/")
    else:
        relative = (current_page.parent.relative_to(ROOT) / path).as_posix()
    candidate = (ROOT / relative).resolve()
    if ROOT != candidate and ROOT not in candidate.parents:
        return None
    if path.endswith("/") or candidate.is_dir():
        candidate = candidate / "index.html"
    elif not candidate.suffix:
        candidate = candidate / "index.html"
    return candidate, fragment


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return parser


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Build root does not exist: {ROOT}")
    failures: list[str] = []
    html_paths = sorted(ROOT.rglob("*.html"))
    parsed: dict[Path, PageParser] = {path: parse_page(path) for path in html_paths}

    if len(list(ROOT.rglob("index.html"))) < 55:
        failures.append("fewer than 55 routed pages were produced")

    banned_copy = re.compile(
        r"before public launch|pre-launch|included in this test build|migration plan|until that work is complete|approved documents required before launch",
        re.I,
    )
    for path, page in parsed.items():
        rel = path.relative_to(ROOT).as_posix()
        markup = path.read_text(encoding="utf-8", errors="ignore")
        non_indexable = "noindex" in page.robots.lower()
        if re.search(r'(?:href|src)="/PSTA/', markup):
            failures.append(f"{rel}: old /PSTA/ asset or route prefix remains")
        if "https://github.com/antlerboy/issues/2" in markup:
            failures.append(f"{rel}: feedback URL was damaged by the domain switch")
        if banned_copy.search(markup):
            failures.append(f"{rel}: pre-release or migration-note copy remains public")
        if "wp-content/" in markup:
            failures.append(f"{rel}: depends on a legacy WordPress asset")
        if not page.lang:
            failures.append(f"{rel}: html language is missing")
        if not page.title:
            failures.append(f"{rel}: title is missing")
        if page.duplicate_ids:
            failures.append(f"{rel}: duplicate IDs: {', '.join(sorted(page.duplicate_ids))}")
        if page.images_without_alt:
            failures.append(f"{rel}: {page.images_without_alt} image(s) lack alt attributes")
        for href, target, rel_value in page.links:
            if target.lower() == "_blank":
                rel_values = set(rel_value.lower().split())
                if not {"noopener", "noreferrer"}.issubset(rel_values):
                    failures.append(f"{rel}: target=_blank link lacks noopener and noreferrer: {href}")
            target_info = internal_target(href, path)
            if target_info is None:
                continue
            target_path, fragment = target_info
            if not target_path.exists():
                failures.append(f"{rel}: broken internal link: {href}")
                continue
            if fragment and target_path.suffix.lower() == ".html":
                target_page = parsed.get(target_path) or parse_page(target_path)
                if fragment not in target_page.ids:
                    failures.append(f"{rel}: missing fragment target in {href}")
        for source in page.assets:
            target_info = internal_target(source, path)
            if target_info and not target_info[0].exists():
                failures.append(f"{rel}: missing asset: {source}")

        if non_indexable:
            continue
        if page.robots.lower().replace(" ", "") != "index,follow":
            failures.append(f"{rel}: public page is not explicitly index, follow")
        if not page.description:
            failures.append(f"{rel}: meta description is missing")
        if page.h1_count != 1:
            failures.append(f"{rel}: expected one H1, found {page.h1_count}")
        if page.main_count != 1:
            failures.append(f"{rel}: expected one main element, found {page.main_count}")
        if not page.canonical.startswith(DOMAIN):
            failures.append(f"{rel}: production canonical is missing")
        if page.site_nav and not page.nav_toggle:
            failures.append(f"{rel}: responsive navigation toggle is missing")

    required = [
        "index.html",
        "programmes/national-commissioning-academy/index.html",
        "programmes/commissioning-simulation/index.html",
        "programmes/commissioning-ten-step-introduction/index.html",
        "commissioning-academy/testimonials/index.html",
        "policies/index.html",
        "accessibility/index.html",
        "assets/img/psta-logo-official.svg",
        "assets/img/psta-logo-web.jpg",
        "news/feed.xml",
        "CNAME",
    ]
    for rel in required:
        target = ROOT / rel
        if not target.exists() or (target.is_file() and target.stat().st_size == 0):
            failures.append(f"required release file is missing or empty: {rel}")

    cname = ROOT / "CNAME"
    if cname.exists() and cname.read_text(encoding="ascii", errors="ignore").strip() != "www.publicservicetransformation.org":
        failures.append("CNAME does not contain the production host")
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8", errors="ignore") if (ROOT / "robots.txt").exists() else ""
    if "Allow: /" not in robots or "Disallow: /" in robots or f"Sitemap: {DOMAIN}/sitemap.xml" not in robots:
        failures.append("robots.txt does not allow crawling and advertise the sitemap")

    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        failures.append("sitemap.xml is missing")
    else:
        try:
            tree = ElementTree.parse(sitemap)
            locations = [node.text or "" for node in tree.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
            if len(locations) < 30:
                failures.append(f"sitemap has only {len(locations)} public URLs")
            if any(not url.startswith(DOMAIN) for url in locations):
                failures.append("sitemap contains a non-production URL")
        except ElementTree.ParseError as exc:
            failures.append(f"sitemap.xml is invalid XML: {exc}")

    home = (ROOT / "index.html").read_text(encoding="utf-8", errors="ignore")
    nca = (ROOT / "programmes/national-commissioning-academy/index.html").read_text(encoding="utf-8", errors="ignore")
    evidence = (ROOT / "commissioning-academy/testimonials/index.html").read_text(encoding="utf-8", errors="ignore")
    for text, label in [
        ("Applications are open for the September 2026 cohort", "home-page application message"),
        ("Read more participant experiences", "home-page proof link"),
        ("2,500+", "graduate evidence"),
    ]:
        if text not in home:
            failures.append(f"missing {label}")
    for text, label in [
        ("£2,490", "current National Commissioning Academy price"),
        ("Apply or ask a question", "National Commissioning Academy action"),
        ("14 September 2026", "launch webinar date"),
        ("23 September 2026", "first anchor-day date"),
    ]:
        if text not in nca:
            failures.append(f"missing {label}")
    for name in ("Gareth Symonds", "Linda Uren", "Damian Roberts", "Tom Woodcock"):
        if name not in evidence:
            failures.append(f"participant evidence missing: {name}")

    all_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in ROOT.rglob("*") if path.is_file() and path.suffix.lower() in {".html", ".css", ".js", ".xml", ".txt", ".json"})
    if "https://github.com/antlerboy/PSTA/issues/2" not in all_text:
        failures.append("website feedback URL is missing")
    if "PSTA accessible navigation state" not in all_text:
        failures.append("accessible mobile-navigation state handling is missing")
    if "http://eepurl.com" in all_text:
        failures.append("newsletter links still use insecure HTTP")
    if "</dl><a" in (ROOT / "programmes/commissioning-simulation/index.html").read_text(encoding="utf-8", errors="ignore")[:2000]:
        failures.append("commissioning simulation still contains the truncated page fragment")

    if failures:
        unique = list(dict.fromkeys(failures))
        raise SystemExit("Public-site audit failed:\n- " + "\n- ".join(unique))
    public_count = sum("noindex" not in page.robots.lower() for page in parsed.values())
    print(f"Public-site audit passed: {len(html_paths)} HTML files, {public_count} indexable pages, all internal links valid")


if __name__ == "__main__":
    main()
