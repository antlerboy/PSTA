#!/usr/bin/env python3
"""Transcribe the published beta matrix without rewriting its questions."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'content/compass/sources/compass-v2-beta-2026-06-13.txt'
text = source.read_text(encoding='utf-8')
matrix = text.rsplit('\nThe matrix\n', 1)[1]
lines = [line.strip() for line in matrix.splitlines() if line.strip()]
assert lines[:6] == ['Aspect', 'Opening up', 'Sensemaking', 'Strategising', 'Making change', 'Collective learning']
lines = lines[6:]
# The source's final heading wraps across two paragraphs in text extraction.
wrap = lines.index('Forms of assets help, infrastructure,')
assert lines[wrap + 1] == 'and action'
lines[wrap:wrap + 2] = ['Forms of assets help, infrastructure, and action']
assert len(lines) == 48, f'Expected 8 matrix rows of 6 cells; found {len(lines)}'
moves = ['Opening up', 'Sensemaking', 'Strategising', 'Making change', 'Collective learning']
sections = []
for index in range(8):
    row = lines[index * 6:(index + 1) * 6]
    sections.append({'id': f'lens-{index + 1}', 'title': row[0], 'questions': [
        {'id': f'lens-{index + 1}-move-{move + 1}', 'label': label, 'prompt': row[move + 1]}
        for move, label in enumerate(moves)
    ]})
data = {
    'id': 'compass-v2-beta',
    'title': 'Compass v2.0 beta',
    'version': '2026-06-13',
    'status': 'Working beta',
    'description': 'Work with the eight lenses and five moves in the published beta. Keep different accounts visible, choose a practical intervention, and return to what it teaches you.',
    'introduction': 'Commissioning is the public craft of helping a place form and reform the relationships, capabilities, arrangements and conditions through which people can live well, with the system learning from what happens.',
    'source': {
        'title': 'Compass v2.0 beta: commissioning as collective system learning',
        'author': 'Benjamin P Taylor',
        'date': '2026-06-13',
        'url': 'https://docs.google.com/document/d/1bOoSQhIyOi1FQRXPSnKuwZ-RrJBnLe-M/edit',
        'localText': '/assets/compass/sources/compass-v2-beta-2026-06-13.txt',
        'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'note': 'The matrix wording is transcribed from the published beta. The final lens heading has been joined across a line break. Saving, perspective comparison, decisions, and review records are additional features of this online edition. No maturity score is calculated.',
    },
    'sections': sections,
    'reviewQuestions': [
        'What changed in people’s lived experience?',
        'What did we learn about how the system behaves?',
        'What did we learn about our arrangements, rules, measures, relationships and forms of help?',
        'What did this reveal about who we think we are, what we think we are here for, and whose purposes count?',
    ],
}
destination = ROOT / 'content/compass/compass-v2-beta.json'
destination.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Transcribed {len(sections)} lenses and 40 original matrix prompts to {destination.name}')
