#!/usr/bin/env python3
"""Run the final PSTA identity/partner pass without network downloads.

The complete stored site bundle already contains the approved full PSTA wordmark. This
pass verifies that exact asset by SHA-256, copies it to the stable public identity path,
and builds the agreed partner directory. Nesta is pinned locally; the other partner
marks use the exact image URLs from the current PSTA WordPress site.
"""
from __future__ import annotations
import hashlib
import shutil
import sys
from pathlib import Path

import final_public_fix as final

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "deploy")
final.ROOT = ROOT

EXPECTED_PSTA_SHA = "bd6bcb8ba0f83684095826bb77e2b49a7ad2b710e65053305bf4f1e6df1b0db7"
EXTERNAL = {
    "e3m": "https://www.publicservicetransformation.org/wp-content/uploads/2015/05/E3M_logo.png",
    "tsip": "https://www.publicservicetransformation.org/wp-content/uploads/2018/03/TSIP.png",
    "localgov-digital": "https://www.publicservicetransformation.org/wp-content/uploads/2018/03/LocGovDigital.png",
    "browne-jacobson": "https://www.publicservicetransformation.org/wp-content/uploads/2015/05/BrowneJacobson.png",
    "redquadrant": "https://www.publicservicetransformation.org/wp-content/uploads/2015/05/RedQuadrant.png",
    "basis": "https://www.publicservicetransformation.org/wp-content/uploads/2019/03/Basis_logo_400x400.jpg",
}


def install_assets_offline():
    source = ROOT / "assets/img/psta-logo-web.jpg"
    if not source.exists():
        raise SystemExit("The full PSTA wordmark is missing from the complete site bundle")
    raw = source.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_PSTA_SHA:
        raise SystemExit(f"The stored PSTA wordmark failed its identity checksum: {actual}")

    target = ROOT / "assets/img/psta-logo-official.jpg"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    final.LOGO = f"{final.PREFIX}/assets/img/psta-logo-official.jpg"
    final.LOGO_SHA = EXPECTED_PSTA_SHA
    (ROOT / "assets/img/psta-logo-path.txt").write_text(final.LOGO, encoding="utf-8")

    folder = ROOT / "assets/img/partners"
    folder.mkdir(parents=True, exist_ok=True)
    final.decode_pinned("nesta-logo.b64", final.NESTA_SHA, folder / "nesta.jpg")
    out = dict(EXTERNAL)
    out["nesta"] = f"{final.PREFIX}/assets/img/partners/nesta.jpg"
    print("Verified full PSTA wordmark and fixed partner-logo sources:", ", ".join(sorted(out)))
    return out


final.install_assets = install_assets_offline

if __name__ == "__main__":
    final.main()
