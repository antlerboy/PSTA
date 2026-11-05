#!/usr/bin/env python3
"""Reproduce the Pages assembly locally, including every checked-in content pass."""
from pathlib import Path
import base64
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile

repo = Path(__file__).resolve().parents[1]
target = repo / 'deploy'
assert target.resolve().parent == repo.resolve() and target.name == 'deploy'
if target.exists():
    # File indexing and sync clients can briefly hold a directory on Windows.
    for attempt in range(4):
        try:
            shutil.rmtree(target)
            break
        except PermissionError:
            if attempt == 3:
                raise
            time.sleep(0.3 * (attempt + 1))
target.mkdir()
parts = sorted((repo / 'site-full-text').glob('part-*'))
if not parts:
    raise SystemExit('The complete site bundle is missing')
text = ''.join(p.read_text(encoding='utf-8').strip() for p in parts)
clean = re.sub(r'[^A-Za-z0-9+/=]', '', text)
data = base64.b64decode(clean + '=' * (-len(clean) % 4))
try:
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:*') as archive:
        for member in archive.getmembers():
            resolved = (target / member.name).resolve()
            if target != resolved and target not in resolved.parents:
                raise SystemExit('Unsafe archive member')
        archive.extractall(target, filter='data')
except tarfile.ReadError:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in archive.namelist():
            resolved = (target / name).resolve()
            if target != resolved and target not in resolved.parents:
                raise SystemExit('Unsafe archive member')
        archive.extractall(target)
if (repo / 'overrides').is_dir():
    shutil.copytree(repo / 'overrides', target, dirs_exist_ok=True)
# Read the authoritative pass order from the release workflow.
workflow = (repo / '.github/workflows/pages.yml').read_text(encoding='utf-8')
scripts = re.findall(r'^\s*python3 (scripts/[a-zA-Z0-9_-]+\.py) deploy\s*$', workflow, re.M)
assert scripts and scripts[-1] == 'scripts/audit_site.py'
env = {**os.environ, 'PYTHONUTF8': '1'}
for script in scripts:
    subprocess.run([sys.executable, script, str(target)], cwd=repo, env=env, check=True)
print(f'Built and audited {target}')
