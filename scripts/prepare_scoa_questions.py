#!/usr/bin/env python3
"""Preserve the undated SCOA predecessor question sheet as an archive edition."""
from pathlib import Path
import hashlib
import json

repo = Path(__file__).resolve().parents[1]
source = repo / 'content/compass/sources/scoa-self-assessment-questions.txt'
lines = [line.strip() for line in source.read_text(encoding='utf-8').splitlines() if line.strip()]
qs = [i for i, line in enumerate(lines) if line == 'Question']
fs = [i for i, line in enumerate(lines) if line == 'Factor']
assert len(qs) == len(fs) == 8
titles = [lines[6 + i * 2] for i in range(8)]
sections = []
for i in range(8):
    n = i + 1
    questions = lines[qs[i] + 3:fs[i]]
    factors = lines[fs[i] + 5:(qs[i + 1] if i < 7 else len(lines))]
    assert lines[fs[i] + 1:fs[i] + 5] == ['Most constraining', 'Most enabling', 'Observations', 'Score /100']
    score = {'min': 0, 'max': 100, 'step': 1}
    prompts = [{'id': f'a{n}-initial', 'label': 'Initial aspect score', 'prompt': titles[i], 'range': score}]
    prompts += [{'id': f'a{n}-q{j}', 'label': f'Question {j}', 'prompt': q, 'range': score} for j, q in enumerate(questions, 1)]
    prompts += [{'id': f'a{n}-revised', 'label': 'Revised aspect score', 'prompt': titles[i], 'range': score}]
    prompts += [{'id': f'a{n}-f{j}', 'label': f'Factor {j}', 'prompt': f, 'kind': 'factor', 'factorGroup': f'aspect-{n}', 'range': score} for j, f in enumerate(factors, 1)]
    sections.append({'id': f'aspect-{n}', 'title': titles[i], 'questions': prompts})
assert sum(len(s['questions']) for s in sections) == 71 + 88 + 16
beta = json.loads((repo / 'content/compass/compass-v2-beta.json').read_text(encoding='utf-8'))
data = {
    'id': 'adult-social-care-options-appraisal', 'title': 'SCOA: archived adult social care question sheet',
    'version': 'undated-source-transcription-2026-11-05', 'status': 'Archived predecessor · undated sheet',
    'description': 'Use the predecessor’s eight aspects, 71 assessment questions, and 88 constraints and enablers, with local notes and /100 self-assessment scores.',
    'introduction': 'The strategic commissioning options appraisal was the adult social care predecessor to the broader Commissioning Compass. This archive preserves its question sheet for comparison and use with judgement.',
    'instructions': lines[:6],
    'source': {
        'title': 'Self-Assessment Questions for 8 Aspects', 'date': None,
        'url': 'https://www.publicservicetransformation.org/tools/adult-social-care-options-appraisal/',
        'localText': '/assets/compass/sources/scoa-self-assessment-questions.txt',
        'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'note': 'The generic wording is transcribed from the undated predecessor document Self-Assessment Questions for 8 Aspects. This is an archive source edition, not a claim that it is the latest sector-specific tool or a complete migration of the teaching material. It preserves 71 questions, 88 factors, and /100 score fields. No numerical score-band labels or three-factor limit are added, because neither appears in this sheet. Some policy references belong to the historical source. Saving, perspectives, decisions, and reviews are additions to the online edition.',
    },
    'sections': sections, 'reviewQuestions': beta['reviewQuestions'],
    'reviewSourceNote': 'The four review questions are from Compass v2.0 beta, 13 June 2026; they are an additional follow-through feature in this archive edition.',
}
(repo / 'content/compass/archive').mkdir(exist_ok=True)
(repo / 'content/compass/archive/adult-social-care-options-appraisal.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Preserved the undated SCOA sheet: 71 questions, 88 factors, and its own /100 fields without invented score anchors')
