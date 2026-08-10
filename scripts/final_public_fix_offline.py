#!/usr/bin/env python3
"""Run the final PSTA identity and partner pass without network downloads.

The public PSTA logo is a complete white-backed SVG stored in the repository so the
Pages build never depends on the damaged JPEG in the historic site bundle. Partner
marks use the exact image URLs from the current PSTA WordPress site, with Nesta pinned
locally as before.
"""
from __future__ import annotations
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
    (ROOT / "assets/img/psta-logo-path.txt").write_text(final.LOGO, encoding="utf-8")

    folder = ROOT / "assets/img/partners"
    folder.mkdir(parents=True, exist_ok=True)
    final.decode_pinned("nesta-logo.b64", final.NESTA_SHA, folder / "nesta.jpg")
    out = dict(EXTERNAL)
    out["nesta"] = f"{final.PREFIX}/assets/img/partners/nesta.jpg"
    print("Installed complete PSTA SVG and partner-logo sources:", ", ".join(sorted(out)))
    return out


final.install_assets = install_assets_offline

if __name__ == "__main__":
    final.main()
