#!/usr/bin/env python3
"""Check curriculum consistency and, optionally, compare the owning record."""
from pathlib import Path
import argparse
import json
from urllib.request import urlopen

repo = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--upstream', help='Owning record URL or a verified local copy')
args = parser.parse_args()
record = json.loads((repo / 'content/programmes/leading-transformation.json').read_text(encoding='utf-8'))
modules = json.loads((repo / 'content/curriculum-2026.json').read_text(encoding='utf-8'))
assert record['canonicalUrl'] == 'https://redquadrant.com/records/leading-transformation.json'
assert record['recordOwner'] == 'RedQuadrant'
assert record['modules'] == modules, 'The programme record and curriculum differ'
assert len(record['modules']) == 24
if args.upstream:
    if args.upstream.startswith('https://'):
        with urlopen(args.upstream, timeout=30) as response:
            upstream = json.load(response)
    else:
        upstream = json.loads(Path(args.upstream).read_text(encoding='utf-8'))
    assert upstream == record, 'The owning programme record has changed; review and refresh the checked copy'
print(f"Leading Transformation record {record['version']}: 24 modules and current routes agree")
