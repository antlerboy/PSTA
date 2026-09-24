#!/usr/bin/env python3
"""Set the PSTA public telephone number across the assembled website."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "deploy")
old = ("+447701049836", "07701 049836", "07701049836")
new = ("+447931317230", "07931 317230", "07931317230")

changed = 0
for path in root.rglob("*.html"):
    html = path.read_text(encoding="utf-8")
    updated = html
    for before, after in zip(old, new):
        updated = updated.replace(before, after)
    if updated != html:
        path.write_text(updated, encoding="utf-8")
        changed += 1
    if "07701 049836" in updated or "07701049836" in updated or "+447701049836" in updated:
        raise SystemExit(f"Old PSTA telephone number remains in {path}")

for page in (root / "index.html", root / "contact/index.html"):
    html = page.read_text(encoding="utf-8")
    if 'href="tel:+447931317230">07931 317230</a>' not in html:
        raise SystemExit(f"New PSTA telephone number missing from {page}")

print(f"Updated the telephone number on {changed} PSTA pages")
