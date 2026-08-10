#!/usr/bin/env python3
"""Deterministic public-copy enrichment without scraping the old WordPress site.

The final public identity/partner pass owns the real logo and partner assets. This pass
keeps the useful copy rules and programme enrichment from the earlier iteration while
removing its slow, brittle network scraping and obsolete global audit.
"""
from __future__ import annotations
import sys
from pathlib import Path

import apply_feedback_iteration as legacy

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "deploy")
legacy.ROOT = ROOT


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Build root does not exist: {ROOT}")

    # Point all public copy at the final pinned wordmark now. The authoritative final pass
    # writes the checksum-verified binary to this path later in the same build.
    logo = f"{legacy.PREFIX}/assets/img/psta-logo-official.jpg"
    partner_logos = {}

    legacy.patch_all_pages(logo, partner_logos)
    nca = legacy.enrich_national_commissioning_academy()
    stp = legacy.enrich_service_transformation_programme([])
    legacy.patch_all_pages(logo, partner_logos)
    legacy.write_feedback_redirect()
    legacy.patch_css()

    if nca is None:
        raise SystemExit("The National Commissioning Academy page could not be enriched")
    if stp is None:
        raise SystemExit("The Service Transformation Programme page could not be enriched")
    print("Deterministic public-copy enrichment completed")


if __name__ == "__main__":
    main()
