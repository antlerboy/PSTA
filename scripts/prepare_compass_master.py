#!/usr/bin/env python3
"""Transcribe the dated, unfilled March 2026 master, with explicit score fields."""
from pathlib import Path
import hashlib
import json
import re

repo = Path(__file__).resolve().parents[1]
source_path = repo / 'content/compass/sources/commissioning-compass-2026-03-24-master.txt'
text = source_path.read_text(encoding='utf-8')
lines = [line.strip() for line in text.splitlines() if line.strip()]
question_starts = [i for i, line in enumerate(lines) if line == 'Question']
factor_starts = [i for i, line in enumerate(lines) if line == 'Factor']
assert len(question_starts) == len(factor_starts) == 8
descriptors = [line for line in lines if re.match(r'^Aspect [1-8], ', line)]
assert len(descriptors) == 8
bands = list(dict.fromkeys(line for line in lines if re.match(r'^\d+\s*–\s*\d+', line)))
assert len(bands) == 4
instructions = lines[:lines.index('Aspect 1: Whole system design')]
source_aspects, sections = [], []
for index in range(8):
    number = index + 1
    title, description = descriptors[index].split(', ', 1)[1].split(': ', 1)
    q_start, f_start = question_starts[index], factor_starts[index]
    next_start = question_starts[index + 1] if index < 7 else len(lines)
    assert '100' in lines[q_start + 1] and '100' in lines[q_start + 3]
    assert lines[f_start + 1:f_start + 4] == ['Most constraining', 'Most enabling', 'Observations']
    questions = lines[q_start + 4:f_start]
    factors = lines[f_start + 4:next_start]
    source_aspects.append({'number': number, 'title': title, 'description': description, 'questions': questions, 'factors': factors})
    score_range = {'min': 0, 'max': 100, 'step': 1}
    prompts = [{'id': f'a{number}-initial', 'label': 'Initial aspect score', 'prompt': description, 'range': score_range}]
    prompts += [{'id': f'a{number}-q{i}', 'label': f'Question {i}', 'prompt': q, 'range': score_range, 'finalScore': True} for i, q in enumerate(questions, 1)]
    prompts += [{'id': f'a{number}-revised', 'label': 'Revised aspect score', 'prompt': description, 'range': score_range}]
    prompts += [{'id': f'a{number}-f{i}', 'label': f'Factor {i}', 'prompt': factor, 'kind': 'factor', 'factorGroup': f'aspect-{number}'} for i, factor in enumerate(factors, 1)]
    sections.append({'id': f'aspect-{number}', 'title': title, 'description': description, 'questions': prompts})
assert sum(len(a['questions']) for a in source_aspects) == 79
assert sum(len(a['factors']) for a in source_aspects) == 89
source = {'title': 'Scoring sheet for your Commissioning Compass: system assessment for change', 'publicationDate': None, 'sourceDocumentDate': '2026-03-24', 'transcribed': '2026-11-05', 'transcription': 'Transcribed from the unfilled 24 March 2026 master. Layout whitespace is normalised. Initial and final question scores are both /100; factors have constraint/enabler choices and observations rather than numerical scores.', 'scoreBands': bands, 'instructions': instructions, 'aspects': source_aspects}
structured_path = repo / 'content/compass/sources/commissioning-compass-scoring-sheet.json'
structured_path.write_text(json.dumps(source, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
tool_path = repo / 'content/compass/commissioning-compass.json'
tool = json.loads(tool_path.read_text(encoding='utf-8'))
tool.update({'version': '2026-03-24', 'status': 'Original Compass · March 2026 sheets', 'sections': sections, 'scoreBands': bands, 'instructions': instructions, 'factorLimit': 3})
tool['source'].update({'title': source['title'], 'date': '2026-03-24', 'localText': '/assets/compass/sources/commissioning-compass-2026-03-24-master.txt', 'sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(), 'note': 'The original assessment is transcribed from the unfilled 24 March 2026 scoring-sheet master: eight aspect descriptors, 79 assessment questions, 89 constraints and enablers, initial and revised aspect scores, and initial and final question scores /100. The source score bands and wording are preserved; layout whitespace is normalised. The online edition adds perspective comparison, saving, decisions, and reviews. The Teachable course has further teaching, approaches, cases, and resources beyond the scoring sheet.'})
tool_path.write_text(json.dumps(tool, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Transcribed the clean March 2026 master: 79 questions with initial/final /100 fields, and 89 unscored factors')
