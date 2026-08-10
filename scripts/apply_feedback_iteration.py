#!/usr/bin/env python3
"""Apply the second public-copy, identity, partner, and programme iteration to the built PSTA site.

The source site is static. This script deliberately makes the repeated language and assurance
rules executable, so later content additions are checked rather than relying on memory.
"""

from __future__ import annotations

import html as html_module
import json
import re
import ssl
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "deploy")
PUBLIC_SITE = "https://www.publicservicetransformation.org/"
PREFIX = "/PSTA"
FEEDBACK_URL = "https://github.com/antlerboy/PSTA/issues/2"
USER_AGENT = "Mozilla/5.0 (compatible; PSTA-site-builder/2.0; +https://github.com/antlerboy/PSTA)"

LEGAL_FOOTER = (
    '<div class="footer-legal">'
    '<span>Registered Social Enterprise. The Public Service Transformation Academy Limited is a company limited by guarantee, '
    'registered in England and Wales, company number 10046052. VAT number 244 4776 87.</span>'
    '<span>7 Bell Yard, London, WC2A 2JR, UK</span>'
    '</div>'
)

PARTNERS = {
    "e3m": ("E3M", ["e3m"]),
    "nesta": ("Nesta", ["nesta", "alliance for useful evidence"]),
    "tsip": ("The Social Innovation Partnership", ["social innovation partnership", "tsip"]),
    "localgov-digital": ("LocalGov Digital", ["localgov digital", "local gov digital", "localgovdigital"]),
    "browne-jacobson": ("Browne Jacobson", ["browne jacobson"]),
    "redquadrant": ("RedQuadrant", ["redquadrant", "red quadrant"]),
    "basis": ("Basis", ["basis", "changing the change"]),
}

VISIBLE_REPLACEMENTS: Sequence[Tuple[str, str]] = (
    ("1,500+ Commissioning Academy graduates across public services", "2,500+ Academy and Programme graduates across public services"),
    ("1,500+ National Commissioning Academy graduates across public services", "2,500+ Academy and Programme graduates across public services"),
    ("See what the system is producing", "See what your system is producing"),
    ("Choose by pressure, not by course title", "Choose what meets your needs, not by course title"),
    ("Choose by pressure", "Choose what meets your needs"),
    ("Start with the pressure", "Start with what you need"),
    ("Buyer pressure", "What you need to achieve"),
    ("Where the pressure sits", "What you need"),
    ("lead partner RedQuadrant", ""),
    ("Lead partner RedQuadrant", ""),
    ("Lead partner: RedQuadrant", ""),
    ("Wider partner history", ""),
    ("wider partner history", ""),
    ("Draft for launch review", ""),
    ("Included in this test build", "Website policies and assurance"),
    ("Approved documents required before launch", "Further organisational documents"),
    ("Known work before launch", "Ongoing accessibility work"),
    ("The test build does not use analytics, advertising cookies, user accounts or an embedded contact form.", "This website does not currently use advertising cookies, user accounts, or an embedded contact form."),
    ("This static test site deliberately uses email links rather than a third-party contact form. That keeps hosting simple and avoids collecting personal data through the site itself. A managed form can be added before launch if it is genuinely useful.", "We use direct email links rather than an embedded third-party form, keeping contact simple and avoiding unnecessary collection of personal data through the website."),
    ("This statement describes the test build. Complete assisted-technology and user testing before replacing the current public site.", "We review this statement as the website changes and continue to test the site with different devices and ways of accessing content."),
    ("Before replacing the current public site, complete:", "We continue to improve accessibility through:"),
    ("Before public launch, add or link the academy’s approved versions of:", "The PSTA also maintains organisational policies and statements including:"),
    ("Before public launch, add or link the Academy’s approved versions of:", "The PSTA also maintains organisational policies and statements including:"),
    ("a concise notice for this static test site.", "how this website handles personal information."),
    ("insight, confidence, practical tools and peer relationships", "insight, confidence, practical tools, and peer relationships"),
    ("commissioning, transformation and system leadership", "commissioning, transformation, and system leadership"),
    ("services, partnerships, systems, markets or outcomes", "services, partnerships, systems, markets, or outcomes"),
    ("local government, NHS and public health", "local government, the NHS, and public health"),
    ("adult social care, housing and community safety", "adult social care, housing, and community safety"),
    ("police, VCSE, central government and other public bodies", "police, VCSE organisations, central government, and other public bodies"),
    ("action learning, peer challenge and live application", "action learning, peer challenge, and live application"),
    ("people, organisations and systems", "people, organisations, and systems"),
    ("tools, insight and relationships", "tools, insight, and relationships"),
    ("strategy, design and delivery", "strategy, design, and delivery"),
    ("commissioning, leadership and transformation", "commissioning, leadership, and transformation"),
    ("public, health, uniformed and civil service bodies", "public, health, uniformed, and civil service bodies"),
)

FORBIDDEN_PUBLIC_PHRASES = (
    "Choose by pressure",
    "Lead partner RedQuadrant",
    "lead partner RedQuadrant",
    "Wider partner history",
    "wider partner history",
    "1,500+ Commissioning Academy graduates",
    "See what the system is producing",
    "Draft for launch review",
    "This static test site",
    "This statement describes the test build",
    "Before replacing the current public site",
)


def fetch(url: str, *, binary: bool = False, timeout: int = 25) -> bytes | str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    context = ssl.create_default_context()
    with urlopen(request, timeout=timeout, context=context) as response:
        data = response.read()
        if binary:
            return data
        charset = response.headers.get_content_charset() or "utf-8"
        return data.decode(charset, errors="replace")


def safe_fetch(url: str, *, binary: bool = False) -> bytes | str | None:
    try:
        return fetch(url, binary=binary)
    except (HTTPError, URLError, TimeoutError, ssl.SSLError, ValueError) as exc:
        print(f"Fetch skipped for {url}: {exc}")
        return None


def attr(tag: str, name: str) -> str:
    match = re.search(rf"\b{name}\s*=\s*(['\"])(.*?)\1", tag, flags=re.I | re.S)
    return html_module.unescape(match.group(2).strip()) if match else ""


def image_extension(data: bytes, url: str = "") -> str:
    sample = data[:200].lstrip()
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if data.startswith(b"RIFF") and b"WEBP" in data[:16]:
        return ".webp"
    if sample.startswith(b"<svg") or b"<svg" in sample.lower():
        return ".svg"
    suffix = Path(urlparse(url).path).suffix.lower()
    return suffix if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"} else ".bin"


def image_candidates(page: str, base_url: str) -> List[Dict[str, str]]:
    candidates: List[Dict[str, str]] = []
    for match in re.finditer(r"<img\b[^>]*>", page, flags=re.I | re.S):
        tag = match.group(0)
        src = attr(tag, "src") or attr(tag, "data-src") or attr(tag, "data-lazy-src")
        srcset = attr(tag, "srcset") or attr(tag, "data-srcset")
        if srcset:
            options = []
            for item in srcset.split(","):
                bits = item.strip().split()
                if bits:
                    weight = 0
                    if len(bits) > 1:
                        weight_match = re.match(r"(\d+)", bits[1])
                        weight = int(weight_match.group(1)) if weight_match else 0
                    options.append((weight, bits[0]))
            if options:
                src = max(options)[1]
        if not src or src.startswith("data:"):
            continue
        context = page[max(0, match.start() - 350): min(len(page), match.end() + 350)]
        candidates.append({
            "url": urljoin(base_url, src),
            "alt": attr(tag, "alt"),
            "title": attr(tag, "title"),
            "class": attr(tag, "class"),
            "context": re.sub(r"<[^>]+>", " ", context),
            "tag": tag,
        })
    return candidates


def same_site_links(page: str, base_url: str) -> List[str]:
    host = urlparse(PUBLIC_SITE).netloc
    links = []
    for href in re.findall(r"<a\b[^>]*\bhref\s*=\s*(['\"])(.*?)\1", page, flags=re.I | re.S):
        url = urljoin(base_url, html_module.unescape(href[1]))
        parsed = urlparse(url)
        if parsed.netloc == host and parsed.scheme in {"http", "https"}:
            links.append(url.split("#", 1)[0])
    return list(dict.fromkeys(links))


def wordpress_search_links(query: str) -> List[str]:
    endpoint = urljoin(PUBLIC_SITE, f"wp-json/wp/v2/search?search={quote(query)}&per_page=50")
    raw = safe_fetch(endpoint)
    links: List[str] = []
    if isinstance(raw, str):
        try:
            for row in json.loads(raw):
                if isinstance(row, dict) and row.get("url"):
                    links.append(str(row["url"]))
        except json.JSONDecodeError:
            pass
    search_page = safe_fetch(urljoin(PUBLIC_SITE, f"?s={quote(query)}"))
    if isinstance(search_page, str):
        links.extend(same_site_links(search_page, PUBLIC_SITE))
    return list(dict.fromkeys(links))


def collect_reference_pages() -> List[Tuple[str, str]]:
    pages: List[Tuple[str, str]] = []
    home = safe_fetch(PUBLIC_SITE)
    if isinstance(home, str):
        pages.append((PUBLIC_SITE, home))
        likely = []
        for link in same_site_links(home, PUBLIC_SITE):
            low = link.lower()
            if any(word in low for word in ("partner", "about", "service-transformation", "programme")):
                likely.append(link)
        for link in likely[:20]:
            content = safe_fetch(link)
            if isinstance(content, str):
                pages.append((link, content))
    for query in ("partners", "Service Transformation Programme", "Public Service Transformation Academy"):
        for link in wordpress_search_links(query)[:20]:
            if any(existing == link for existing, _ in pages):
                continue
            content = safe_fetch(link)
            if isinstance(content, str):
                pages.append((link, content))
    print(f"Reference pages collected: {len(pages)}")
    return pages


def download_candidate(candidate: Dict[str, str], destination_stem: Path) -> Optional[str]:
    data = safe_fetch(candidate["url"], binary=True)
    if not isinstance(data, bytes) or len(data) < 300:
        return None
    ext = image_extension(data, candidate["url"])
    if ext == ".bin":
        return None
    destination = destination_stem.with_suffix(ext)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return f"{PREFIX}/{destination.relative_to(ROOT).as_posix()}"


def choose_psta_logo(pages: Sequence[Tuple[str, str]]) -> Optional[Dict[str, str]]:
    scored: List[Tuple[int, Dict[str, str]]] = []
    for url, page in pages:
        for candidate in image_candidates(page, url):
            text = " ".join(candidate[key] for key in ("url", "alt", "title", "class", "context")).lower()
            score = 0
            if "logo" in text:
                score += 12
            if "public service transformation academy" in text:
                score += 18
            if "psta" in text:
                score += 14
            if any(word in text for word in ("partner", "redquadrant", "nesta", "e3m", "browne")):
                score -= 8
            if "site-logo" in text or "custom-logo" in text:
                score += 10
            scored.append((score, candidate))
    return max(scored, key=lambda row: row[0])[1] if scored and max(scored, key=lambda row: row[0])[0] > 5 else None


def install_psta_logo(pages: Sequence[Tuple[str, str]]) -> str:
    candidate = choose_psta_logo(pages)
    path = None
    if candidate:
        path = download_candidate(candidate, ROOT / "assets" / "img" / "psta-logo-official")
        if path:
            print(f"Official PSTA logo: {candidate['url']} -> {path}")
    if not path:
        for fallback_name in ("psta-logo-web.jpg", "psta-logo.jpg", "psta-logo-web.png", "psta-logo.png"):
            fallback = ROOT / "assets" / "img" / fallback_name
            if fallback.exists() and fallback.stat().st_size > 1000:
                path = f"{PREFIX}/{fallback.relative_to(ROOT).as_posix()}"
                print(f"Using bundled PSTA logo fallback: {path}")
                break
    if not path:
        raise SystemExit("No usable PSTA logo could be obtained from the current PSTA website or the bundle.")
    marker = ROOT / "assets" / "img" / "psta-logo-path.txt"
    marker.write_text(path, encoding="utf-8")
    return path


def install_partner_logos(pages: Sequence[Tuple[str, str]]) -> Dict[str, str]:
    all_candidates: List[Dict[str, str]] = []
    for url, page in pages:
        all_candidates.extend(image_candidates(page, url))
    installed: Dict[str, str] = {}
    for key, (_, aliases) in PARTNERS.items():
        scored: List[Tuple[int, Dict[str, str]]] = []
        for candidate in all_candidates:
            text = " ".join(candidate[field] for field in ("url", "alt", "title", "class", "context")).lower()
            score = 0
            for alias in aliases:
                if alias in text:
                    score += 20
                    if alias in candidate["alt"].lower() or alias in candidate["title"].lower():
                        score += 12
                    if alias.replace(" ", "") in candidate["url"].lower().replace("-", "").replace("_", ""):
                        score += 8
            if "logo" in text:
                score += 5
            if "psta" in text and key not in {"redquadrant", "basis"}:
                score -= 2
            if score:
                scored.append((score, candidate))
        for _, candidate in sorted(scored, key=lambda row: row[0], reverse=True):
            path = download_candidate(candidate, ROOT / "assets" / "img" / "partners" / key)
            if path:
                installed[key] = path
                print(f"Partner logo {key}: {candidate['url']} -> {path}")
                break
    return installed


def transform_visible_text(segment: str) -> str:
    if not segment or not segment.strip():
        return segment
    result = segment
    for old, new in VISIBLE_REPLACEMENTS:
        result = result.replace(old, new)

    result = re.sub(r"(?<!National )\bCommissioning Academy\b", "National Commissioning Academy", result, flags=re.I)
    result = re.sub(r"(?<!the )\bNational Commissioning Academy\b", "the National Commissioning Academy", result, flags=re.I)
    result = re.sub(r"(?<!the )\bService Transformation Programme\b", "the Service Transformation Programme", result, flags=re.I)
    result = re.sub(r"(?<!the )\bPSTA\b", "the PSTA", result, flags=re.I)

    result = re.sub(r"\bthe the PSTA\b", "the PSTA", result, flags=re.I)
    result = re.sub(r"\bthe the National Commissioning Academy\b", "the National Commissioning Academy", result, flags=re.I)
    result = re.sub(r"\bthe the Service Transformation Programme\b", "the Service Transformation Programme", result, flags=re.I)
    result = re.sub(r"\bThe the PSTA\b", "The PSTA", result)
    result = re.sub(r"\bThe the National Commissioning Academy\b", "The National Commissioning Academy", result)
    result = re.sub(r"\bThe the Service Transformation Programme\b", "The Service Transformation Programme", result)

    if result.lstrip().startswith("the PSTA"):
        prefix_len = len(result) - len(result.lstrip())
        result = result[:prefix_len] + "The PSTA" + result[prefix_len + len("the PSTA"):]
    if result.lstrip().startswith("the National Commissioning Academy"):
        prefix_len = len(result) - len(result.lstrip())
        result = result[:prefix_len] + "The National Commissioning Academy" + result[prefix_len + len("the National Commissioning Academy"):]
    if result.lstrip().startswith("the Service Transformation Programme"):
        prefix_len = len(result) - len(result.lstrip())
        result = result[:prefix_len] + "The Service Transformation Programme" + result[prefix_len + len("the Service Transformation Programme"):]

    result = re.sub(r"[ \t]{2,}", " ", result)
    return result


def patch_text_nodes(document: str) -> str:
    tokens = re.split(r"(<[^>]+>)", document)
    skip_depth = 0
    skip_tags = {"script", "style", "svg", "code", "pre", "textarea"}
    output: List[str] = []
    for token in tokens:
        if token.startswith("<"):
            close = re.match(r"</\s*([a-z0-9:-]+)", token, flags=re.I)
            open_tag = re.match(r"<\s*([a-z0-9:-]+)", token, flags=re.I)
            if close and close.group(1).lower() in skip_tags:
                skip_depth = max(0, skip_depth - 1)
            output.append(token)
            if open_tag and not token.startswith("</") and open_tag.group(1).lower() in skip_tags and not token.rstrip().endswith("/>"):
                skip_depth += 1
        else:
            output.append(token if skip_depth else transform_visible_text(token))
    return "".join(output)


def remove_named_cards(document: str, names: Iterable[str]) -> str:
    result = document
    for name in names:
        escaped = re.escape(name)
        for tag in ("article", "div", "li"):
            pattern = rf"<{tag}\b[^>]*(?:class=['\"][^'\"]*(?:card|partner)[^'\"]*['\"])?[^>]*>.*?{escaped}.*?</{tag}>"
            result = re.sub(pattern, "", result, flags=re.I | re.S)
    return result


def patch_footer(document: str) -> str:
    if re.search(r"<div\b[^>]*class=['\"][^'\"]*footer-legal", document, flags=re.I):
        return re.sub(r"<div\b[^>]*class=['\"][^'\"]*footer-legal[^'\"]*['\"][^>]*>.*?</div>", LEGAL_FOOTER, document, flags=re.I | re.S)
    if "</footer>" in document:
        return document.replace("</footer>", LEGAL_FOOTER + "\n</footer>", 1)
    return document


def patch_feedback(document: str) -> str:
    result = re.sub(r"(?:https://antlerboy\.github\.io)?/PSTA/iteration-notes-[^'\"< ]+/?", FEEDBACK_URL, document)
    result = re.sub(r"iteration-notes-[a-z0-9]+/?", FEEDBACK_URL, result)
    result = result.replace("https://github.com/antlerboy/PSTA/issues/new", FEEDBACK_URL)
    return result


def patch_logo(document: str, logo_path: str) -> str:
    result = re.sub(r"(['\"])(?:/PSTA)?/assets/img/(?:psta-logo(?:-web)?\.(?:png|jpe?g|webp|svg))\1", lambda match: match.group(1) + logo_path + match.group(1), document, flags=re.I)
    result = re.sub(r"(<img\b[^>]*\bclass=['\"][^'\"]*(?:footer-logo|site-logo)[^'\"]*['\"][^>]*\bsrc=['\"])([^'\"]+)", rf"\1{logo_path}", result, flags=re.I)
    result = re.sub(r"alt=['\"](?:PSTA|Public Service Transformation Academy)['\"]", 'alt="The Public Service Transformation Academy"', result, flags=re.I)
    return result


def patch_partner_placeholders(document: str, logos: Dict[str, str]) -> str:
    result = document
    for key, path in logos.items():
        result = result.replace(f'data-partner-logo="{key}" src=""', f'data-partner-logo="{key}" src="{path}"')
        result = result.replace(f'data-partner-logo="{key}"', f'data-partner-logo="{key}"')
    return result


def inject_feedback_shortcut(document: str) -> str:
    if "PSTA_FEEDBACK_SHORTCUT" in document:
        return document
    script = f'''<!-- PSTA_FEEDBACK_SHORTCUT -->
<script>document.addEventListener('keydown',function(e){{if(e.altKey&&e.shiftKey&&e.key.toLowerCase()==='n'){{window.location.href='{FEEDBACK_URL}';}}}});</script>'''
    return document.replace("</body>", script + "\n</body>", 1) if "</body>" in document else document + script


def write_feedback_redirect() -> None:
    target = ROOT / "iteration-notes-7d4f9c2b81e6a5" / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta http-equiv="refresh" content="0; url={FEEDBACK_URL}"><link rel="canonical" href="{FEEDBACK_URL}"><title>PSTA website feedback</title></head><body><p><a href="{FEEDBACK_URL}">Open the running PSTA website feedback thread</a>.</p><script>window.location.replace('{FEEDBACK_URL}');</script></body></html>''', encoding="utf-8")


def visible_text(document: str) -> str:
    clean = re.sub(r"<(script|style|svg|code|pre|textarea)\b[^>]*>.*?</\1>", " ", document, flags=re.I | re.S)
    clean = re.sub(r"<[^>]+>", " ", clean)
    return html_module.unescape(re.sub(r"\s+", " ", clean))


def find_page(terms: Sequence[str], *, excluded_parts: Sequence[str] = ()) -> Optional[Path]:
    scored: List[Tuple[int, int, Path]] = []
    for path in ROOT.rglob("index.html"):
        rel = path.relative_to(ROOT).as_posix().lower()
        if any(part.lower() in rel for part in excluded_parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        plain = visible_text(text).lower()
        score = sum(plain.count(term.lower()) * (3 if index == 0 else 1) for index, term in enumerate(terms))
        if score:
            scored.append((score, -len(rel), path))
    return max(scored)[2] if scored else None


def insert_marked_section(path: Path, marker: str, section: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(rf"<!-- {re.escape(marker)}_START -->.*?<!-- {re.escape(marker)}_END -->", "", text, flags=re.S)
    marked = f"<!-- {marker}_START -->\n{section}\n<!-- {marker}_END -->"
    if "</main>" in text:
        text = text.replace("</main>", marked + "\n</main>", 1)
    else:
        text = text.replace("</body>", marked + "\n</body>", 1)
    path.write_text(text, encoding="utf-8")


def enrich_national_commissioning_academy() -> Optional[Path]:
    page = find_page(("National Commissioning Academy", "100-day plan", "Cabinet Office"), excluded_parts=("news", "partners"))
    if not page:
        print("National Commissioning Academy page not found for enrichment")
        return None
    section = f'''<section class="section section-wash" id="september-2026-cohort">
  <div class="shell">
    <p class="eyebrow">September 2026 to February 2027</p>
    <div class="section-heading"><div><h2>The next National Commissioning Academy</h2><p class="lede">Not just buying services. Shaping systems.</p></div><p><strong>£2,490 per participant.</strong><br>Discounts are available for bookings of three or more people and for organisations willing to host an anchor day.</p></div>
    <div class="feature-panel">
      <div>
        <h3>Bring a live challenge and leave with practical action</h3>
        <p>The National Commissioning Academy combines anchor days, webinars and expert sessions, action learning, peer challenge, a national network, and a practical 100-day plan. It is for commissioners, transformation leads, and colleagues whose work shapes services, partnerships, systems, markets, or outcomes.</p>
        <p>The launch webinar is on <strong>Monday 14 September 2026, 10:00–12:30</strong>. The first full anchor day is on <strong>Wednesday 23 September 2026, 10:00–16:30</strong>. The main programme is expected to run to February 2027.</p>
        <p><a class="button button-gold" href="mailto:david.mason@publicservicetransformation.org?subject=National%20Commissioning%20Academy%20September%202026">Discuss a place with David Mason</a></p>
      </div>
      <div class="feature-meta">
        <h3>How the learning works</h3>
        <p><strong>Action</strong> — applying insight and tools to your own priorities.</p>
        <p><strong>Process</strong> — facilitation, coaching, experience sharing, and collaborative learning.</p>
        <p><strong>Knowledge</strong> — proven practice, challenging ideas, and practical know-how.</p>
      </div>
    </div>
    <h3>Five linked learning cycles</h3>
    <div class="method-grid">
      <div class="method-step"><strong>1. Whole-system design</strong><p>Wellbeing, relationships, and organisations across the system.</p></div>
      <div class="method-step"><strong>2. Capacity and outcomes</strong><p>Capability, confidence, and citizen- and outcome-centred approaches.</p></div>
      <div class="method-step"><strong>3. Insight and innovation</strong><p>Information, insight, innovation, and making room to make a difference.</p></div>
      <div class="method-step"><strong>4. Commissioning practice</strong><p>The commissioning process, service design, models, and tactics.</p></div>
      <div class="method-step"><strong>5. Convening change</strong><p>Putting learning into action and creating the conditions for sustainable change.</p></div>
    </div>
    <h3>What previous participants reported</h3>
    <div class="credibility-grid">
      <div class="credibility-item"><strong>98%</strong><span>made useful connections</span></div>
      <div class="credibility-item"><strong>91%</strong><span>rated it a good or excellent use of their time</span></div>
      <div class="credibility-item"><strong>91%</strong><span>said it was relevant or highly relevant to their learning needs</span></div>
      <div class="credibility-item"><strong>87%</strong><span>would recommend it to colleagues and peers</span></div>
    </div>
  </div>
</section>'''
    insert_marked_section(page, "PSTA_NCA_2026", section)
    print(f"National Commissioning Academy enriched: {page.relative_to(ROOT)}")
    return page


def old_service_transformation_contacts(pages: Sequence[Tuple[str, str]]) -> List[Tuple[str, str]]:
    candidates: List[Tuple[int, List[Tuple[str, str]]]] = []
    for url, page in pages:
        if "service transformation programme" not in visible_text(page).lower():
            continue
        contacts: List[Tuple[str, str]] = []
        for match in re.finditer(r"<a\b[^>]*\bhref\s*=\s*(['\"])(mailto:|tel:)(.*?)\1[^>]*>(.*?)</a>", page, flags=re.I | re.S):
            href = (match.group(2) + match.group(3)).strip()
            label = visible_text(match.group(4)).strip() or href.replace("mailto:", "").replace("tel:", "")
            contacts.append((href, label))
        if contacts:
            score = page.lower().count("service transformation programme") * 10
            if "contact" in page.lower():
                score += 2
            candidates.append((score, contacts))
    if not candidates:
        return []
    selected = max(candidates, key=lambda row: row[0])[1]
    unique: List[Tuple[str, str]] = []
    for item in selected:
        if item not in unique:
            unique.append(item)
    return unique[:3]


def enrich_service_transformation_programme(pages: Sequence[Tuple[str, str]]) -> Optional[Path]:
    page = find_page(("Service Transformation Programme", "service transformation"), excluded_parts=("news", "partners"))
    if not page:
        print("Service Transformation Programme page not found")
        return None
    contacts = old_service_transformation_contacts(pages)
    if not contacts:
        contacts = [("mailto:david.mason@publicservicetransformation.org?subject=Service%20Transformation%20Programme", "Email David Mason")]
    links = []
    for index, (href, label) in enumerate(contacts):
        css = "button button-gold" if index == 0 else "button button-secondary"
        links.append(f'<a class="{css}" href="{html_module.escape(href, quote=True)}">{html_module.escape(label)}</a>')
    section = f'''<section class="section section-blue" id="service-transformation-contact"><div class="shell"><p class="eyebrow">Discuss the programme</p><h2>The Service Transformation Programme</h2><p class="lede">Talk to the PSTA about the programme, an organisational cohort, or how it could be adapted to your context.</p><div class="hero-actions">{''.join(links)}</div></div></section>'''
    insert_marked_section(page, "PSTA_STP_CONTACT", section)
    print(f"Service Transformation Programme contacts enriched: {page.relative_to(ROOT)}; contacts={contacts}")
    return page


def patch_all_pages(logo_path: str, partner_logos: Dict[str, str]) -> None:
    for path in ROOT.rglob("*.html"):
        document = path.read_text(encoding="utf-8", errors="strict")
        document = patch_feedback(document)
        document = remove_named_cards(document, ("APACE", "Fractal Consulting"))
        document = patch_text_nodes(document)
        document = patch_footer(document)
        document = patch_logo(document, logo_path)
        document = patch_partner_placeholders(document, partner_logos)
        document = inject_feedback_shortcut(document)
        path.write_text(document, encoding="utf-8")


def patch_css() -> None:
    css_path = ROOT / "assets" / "css" / "site.css"
    if not css_path.exists():
        raise SystemExit("The site stylesheet is missing")
    css = css_path.read_text(encoding="utf-8")
    css = re.sub(r"\.iteration-secret-link\s*\{.*?\}", "", css, flags=re.S)
    css += '''
/* Feedback iteration 2: visible enough for the site owner, unobtrusive for visitors. */
.brand img,.footer-logo{display:block;width:100%;height:auto;max-height:76px;object-fit:contain;object-position:left center}
.iteration-secret-link{position:fixed;right:0;bottom:0;width:18px;height:18px;z-index:1000;opacity:1;background:#fff;border:1px solid rgba(13,25,255,.24);border-radius:4px 0 0 0;box-shadow:0 0 0 1px rgba(255,255,255,.85)}
.iteration-secret-link:hover,.iteration-secret-link:focus{background:#fff;outline:3px solid #ff8000;outline-offset:0}
.partner-logo-wrap{display:flex;align-items:center;justify-content:center;min-height:104px;margin-bottom:1rem;padding:1rem;background:#fff;border:1px solid var(--line);border-radius:12px}
.partner-logo{max-width:220px;max-height:76px;object-fit:contain}
.partner-logo-fallback{font-size:1.2rem;font-weight:900;color:var(--blue)}
.news-prose{max-width:820px}
'''
    css_path.write_text(css, encoding="utf-8")


def audit(nca_page: Optional[Path], stp_page: Optional[Path], logo_path: str) -> None:
    pages = list(ROOT.rglob("*.html"))
    combined = "\n".join(visible_text(path.read_text(encoding="utf-8", errors="ignore")) for path in pages)
    failures: List[str] = []
    for phrase in FORBIDDEN_PUBLIC_PHRASES:
        if phrase.lower() in combined.lower():
            failures.append(f"forbidden public phrase remains: {phrase}")
    if re.search(r"\bAPACE\b|Fractal Consulting", combined, flags=re.I):
        failures.append("APACE or Fractal Consulting remains in public pages")
    if "2,500+ Academy and Programme graduates across public services" not in combined:
        failures.append("the 2,500+ graduate statistic is missing")
    if "Registered Social Enterprise" not in combined:
        failures.append("Registered Social Enterprise is missing from the footer")
    if nca_page is None or "£2,490" not in visible_text(nca_page.read_text(encoding="utf-8")):
        failures.append("the National Commissioning Academy price and enrichment are missing")
    if stp_page is None or "Service Transformation Programme" not in visible_text(stp_page.read_text(encoding="utf-8")):
        failures.append("the Service Transformation Programme page was not found")
    logo_file = ROOT / logo_path.replace(f"{PREFIX}/", "", 1)
    if not logo_file.exists() or logo_file.stat().st_size < 1000:
        failures.append("the PSTA logo is missing or too small")
    if len(pages) < 30:
        failures.append(f"only {len(pages)} HTML pages were built")

    bare_psta = []
    bare_academy = []
    for path in pages:
        text = visible_text(path.read_text(encoding="utf-8", errors="ignore"))
        if re.search(r"(?<!the )\bPSTA\b", text, flags=re.I):
            bare_psta.append(str(path.relative_to(ROOT)))
        if re.search(r"(?<!National )\bCommissioning Academy\b", text, flags=re.I):
            bare_academy.append(str(path.relative_to(ROOT)))
    if bare_psta:
        failures.append("bare PSTA remains in: " + ", ".join(bare_psta[:8]))
    if bare_academy:
        failures.append("bare Commissioning Academy remains in: " + ", ".join(bare_academy[:8]))

    if failures:
        raise SystemExit("Public copy audit failed:\n- " + "\n- ".join(failures))
    print(f"Public copy audit passed across {len(pages)} HTML pages")


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Build root does not exist: {ROOT}")
    reference_pages = collect_reference_pages()
    logo = install_psta_logo(reference_pages)
    partner_logos = install_partner_logos(reference_pages)
    patch_all_pages(logo, partner_logos)
    nca = enrich_national_commissioning_academy()
    stp = enrich_service_transformation_programme(reference_pages)
    # Enrichment inserts new public copy, so apply the language rules once more.
    patch_all_pages(logo, partner_logos)
    write_feedback_redirect()
    patch_css()
    audit(nca, stp, logo)
    print(f"Installed partner logos: {', '.join(sorted(partner_logos)) or 'none'}")


if __name__ == "__main__":
    main()
