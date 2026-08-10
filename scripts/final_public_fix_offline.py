#!/usr/bin/env python3
"""Run the final PSTA identity/partner pass without network downloads.

The PSTA and Nesta marks are pinned in the repository. The other partner marks are the
exact image URLs used by the current PSTA WordPress site. They are embedded as image
sources on the partners page, so the build does not stall while downloading them.
"""
from __future__ import annotations
import sys
from pathlib import Path

import final_public_fix as final

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "deploy")
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
    final.decode_pinned(
        "psta-logo-official.b64",
        final.LOGO_SHA,
        ROOT / "assets/img/psta-logo-official.jpg",
    )
    (ROOT / "assets/img/psta-logo-path.txt").write_text(final.LOGO, encoding="utf-8")
    folder = ROOT / "assets/img/partners"
    folder.mkdir(parents=True, exist_ok=True)
    final.decode_pinned("nesta-logo.b64", final.NESTA_SHA, folder / "nesta.jpg")
    out = dict(EXTERNAL)
    out["nesta"] = f"{final.PREFIX}/assets/img/partners/nesta.jpg"
    print("Partner logo sources fixed:", ", ".join(sorted(out)))
    return out


final.install_assets = install_assets_offline

if __name__ == "__main__":
    final.main()
