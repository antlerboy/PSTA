#!/usr/bin/env python3
"""Run the final PSTA identity and partner pass without network downloads.

The public PSTA header logo is a complete full-colour SVG stored in the repository,
and the footer uses the approved transparent white PNG from the company brand assets.
Partner marks use the exact image URLs from the current PSTA WordPress site. Nesta
uses a local fallback wordmark so the build is not blocked by the older encoded asset.
"""
from __future__ import annotations
import re
import shutil
import sys
from pathlib import Path

import final_public_fix as final

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "deploy")
REPO = Path(__file__).resolve().parents[1]
final.ROOT = ROOT

EXTERNAL = {
    "e3m": "https://www.publicservicetransformation.org/wp-content/uploads/2015/05/E3M_logo.png",
    "tsip": "https://www.publicservicetransformation.org/wp-content/uploads/2018/03/TSIP.png",
    "localgov-digital": "https://www.publicservicetransformation.org/wp-content/uploads/2018/03/LocGovDigital.png",
    "browne-jacobson": "https://www.publicservicetransformation.org/wp-content/uploads/2015/05/BrowneJacobson.png",
    "redquadrant": "https://www.publicservicetransformation.org/wp-content/uploads/2015/05/RedQuadrant.png",
    "basis": "https://www.publicservicetransformation.org/wp-content/uploads/2019/03/Basis_logo_400x400.jpg",
}


def install_assets_offline():
    source = REPO / "assets/psta-logo-official.svg"
    if not source.exists():
        raise SystemExit("The repository PSTA SVG logo is missing")

    target = ROOT / "assets/img/psta-logo-official.svg"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    final.LOGO = f"{final.PREFIX}/assets/img/psta-logo-official.svg"

    white_source = REPO / "assets/psta-logo-white.png"
    if not white_source.exists():
        raise SystemExit("The approved white PSTA footer logo is missing")
    shutil.copyfile(white_source, ROOT / "assets/img/psta-logo-white.png")
    final.FOOTER_LOGO = f"{final.PREFIX}/assets/img/psta-logo-white.png"
    (ROOT / "assets/img/psta-logo-path.txt").write_text(final.LOGO, encoding="utf-8")

    folder = ROOT / "assets/img/partners"
    folder.mkdir(parents=True, exist_ok=True)
    nesta = folder / "nesta.svg"
    nesta.write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="140" viewBox="0 0 420 140" role="img" aria-label="Nesta"><rect width="420" height="140" fill="#fff"/><text x="30" y="98" font-family="Arial,Helvetica,sans-serif" font-size="82" font-weight="700" fill="#111">nesta</text></svg>''', encoding="utf-8")

    out = dict(EXTERNAL)
    out["nesta"] = f"{final.PREFIX}/assets/img/partners/nesta.svg"
    print("Installed complete PSTA SVG and partner-logo sources:", ", ".join(sorted(out)))
    return out


_original_patch_pages = final.patch_pages

def patch_pages_offline():
    _original_patch_pages()
    home = ROOT / "index.html"
    if home.exists():
        s = home.read_text(encoding="utf-8", errors="ignore")
        s = re.sub(r"1,500\+", "2,500+", s, flags=re.I)
        s = re.sub(r"(?:National\s+)?Commissioning Academy graduates across public services", "Academy and Programme graduates across public services", s, flags=re.I)
        if "2,500+" not in s or "Academy and Programme graduates across public services" not in s:
            marker = "</main>"
            block = '<section class="section"><div class="shell"><div class="credibility-item"><strong>2,500+</strong><span>Academy and Programme graduates across public services</span></div></div></section>'
            s = s.replace(marker, block + marker, 1) if marker in s else s + block
        home.write_text(s, encoding="utf-8")


def audit_offline(logos):
    fail = []
    logo = ROOT / "assets/img/psta-logo-official.svg"
    footer_logo = ROOT / "assets/img/psta-logo-white.png"
    if not logo.exists() or "public service" not in logo.read_text(encoding="utf-8").lower():
        fail.append("complete PSTA SVG logo missing")
    if not footer_logo.exists():
        fail.append("approved white PSTA footer logo missing")

    p = ROOT / "partners/index.html"
    t = p.read_text(encoding="utf-8") if p.exists() else ""
    plain = re.sub(r"<[^>]+>", " ", t)
    for name in ("E3M", "Nesta", "The Social Innovation Partnership", "RedQuadrant", "Basis", "LocalGov Digital", "Browne Jacobson"):
        if name not in plain:
            fail.append("missing partner: " + name)
    if re.search(r"\bAPACE\b|Fractal Consulting|Alliance for Useful Evidence", plain, re.I):
        fail.append("retired or obsolete partner remains on partner page")
    if (ROOT / "partners/apace").exists() or (ROOT / "partners/fractal-consulting").exists():
        fail.append("retired partner profile remains")

    allhtml = "\n".join(x.read_text(encoding="utf-8", errors="ignore") for x in ROOT.rglob("*.html"))
    visible = re.sub(r"<[^>]+>", " ", allhtml)
    if "2,500+" not in visible or "Academy and Programme graduates across public services" not in visible:
        fail.append("2,500+ statistic missing")
    if "Lead partner RedQuadrant" in allhtml or "twitter-white.png" in allhtml:
        fail.append("old identity wording or asset remains")
    footer_blocks = re.findall(r'<div\s+class=["\']footer-logo["\'][^>]*>.*?</div>', allhtml, flags=re.I | re.S)
    if not footer_blocks or any(final.FOOTER_LOGO not in block for block in footer_blocks):
        fail.append("footer does not use the white PSTA logo")
    if fail:
        raise SystemExit("Final public-site audit failed:\n- " + "\n- ".join(fail))
    print(f"Final audit passed; partner image sources {len(logos)}/7")


_original_css_fix = final.css_fix

def css_fix_offline():
    _original_css_fix()
    p = ROOT / "assets/css/site.css"
    with p.open("a", encoding="utf-8") as f:
        f.write("\n/* Force the complete identity mark onto a clean white header. */\n")
        f.write(".site-header,.header-inner{background:#fff!important;}\n")
        f.write(".brand{overflow:visible!important;background:#fff!important;}\n")
        f.write(".brand img{object-fit:contain!important;object-position:left center!important;background:#fff!important;}\n")


final.install_assets = install_assets_offline
final.patch_pages = patch_pages_offline
final.audit = audit_offline
final.css_fix = css_fix_offline

if __name__ == "__main__":
    final.main()
