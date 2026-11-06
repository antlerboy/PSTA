/* Source fidelity and record portability tests. Run with Node's built-in test runner. */
const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const { newRecord, validateRecord, markdown, reflectionMarkdown, selectedPerspectiveIndex } = require('../assets/compass/compass.js');
const read = name => JSON.parse(fs.readFileSync(path.join(__dirname, '../content/compass', name), 'utf8'));
const original = read('commissioning-compass.json');
const beta = read('compass-v2-beta.json');
const smart = read('smart-compass-local.json');
const adult = read('archive/adult-social-care-options-appraisal.json');

test('every edition identifies the exact preserved source used for its transcription', () => {
  const crypto = require('node:crypto');
  for (const tool of [original, beta, smart, adult]) {
    const name = path.basename(tool.source.localText);
    const bytes = fs.readFileSync(path.join(__dirname, '../content/compass/sources', name));
    assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), tool.source.sha256);
  }
});

test('all original questions, factors, and score bands preserve the sanitised source', () => {
  const source = read('sources/commissioning-compass-scoring-sheet.json');
  assert.equal(original.sections.length, 8);
  assert.equal(source.aspects.reduce((n, s) => n + s.questions.length, 0), 79);
  assert.equal(source.aspects.reduce((n, s) => n + s.factors.length, 0), 89);
  assert.deepEqual(original.scoreBands, source.scoreBands);
  original.sections.forEach((section, i) => {
    assert.equal(section.title, source.aspects[i].title);
    assert.deepEqual(section.questions.filter(q => q.id.includes('-q')).map(q => q.prompt), source.aspects[i].questions);
    assert.deepEqual(section.questions.filter(q => q.kind === 'factor').map(q => q.prompt), source.aspects[i].factors);
  });
  source.aspects.forEach(a => assert.deepEqual(Object.keys(a).sort(), ['description', 'factors', 'number', 'questions', 'title']));
  source.aspects.forEach(a => {
    assert.ok(a.questions.every(q => typeof q === 'string'));
    assert.ok(a.factors.every(f => typeof f === 'string'));
    assert.equal(Object.prototype.hasOwnProperty.call(a, 'observations'), false);
    assert.equal(Object.prototype.hasOwnProperty.call(a, 'scores'), false);
  });
});

test('smartCompass keeps the published context and sixteen questions in order', () => {
  const source = read('sources/smart-compass-2026-07-16.json');
  const prompts = smart.sections.flatMap(s => s.questions.map(q => q.prompt));
  assert.deepEqual(prompts, [...source.context, ...source.questions].map(q => q.prompt));
  assert.equal(source.questions.length, 16);
  assert.equal(beta.sections.length, 8);
  assert.equal(beta.sections.flatMap(s => s.questions).length, 40);
});

test('editable records preserve zero scores, perspectives, review drafts, and snapshots', () => {
  const record = newRecord(original);
  record.participants[0].answers['a1-q1'] = { notes: 'First account', evidence: 'A dated observation', score: '0', finalScore: '67' };
  record.reviewDraft[0] = 'An unfinished review';
  const snapshot = JSON.parse(JSON.stringify({ title: record.title, boundary: record.boundary, missing: record.missing, participants: record.participants, decisions: record.decisions }));
  record.reviews.push({ date: '2026-11-05', learning: ['First review'], snapshot });
  record.participants[0].answers['a1-q1'].notes = 'A changed account';
  const reopened = validateRecord(JSON.parse(JSON.stringify(record)), original);
  assert.equal(reopened.participants[0].answers['a1-q1'].score, '0');
  assert.equal(reopened.participants[0].answers['a1-q1'].finalScore, '67');
  assert.equal(reopened.reviewDraft[0], 'An unfinished review');
  assert.equal(reopened.reviews[0].snapshot.participants[0].answers['a1-q1'].notes, 'First account');
  const notes = markdown(reopened, original);
  assert.ok(notes.includes('A changed account') && notes.includes('First account') && notes.includes('Indicative score: 0'));
});

test('imports reject wrong editions and invalid scores, and discard unknown fields', () => {
  const record = newRecord(original);
  assert.throws(() => validateRecord(record, beta), /different Compass edition/);
  record.participants[0].answers['a1-q1'] = { score: '101' };
  assert.throws(() => validateRecord(record, original), /outside/);
  record.participants[0].answers = { 'not-a-question': { notes: 'Unknown' } };
  record.unrecognised = 'not retained';
  const clean = validateRecord(record, original);
  assert.equal(clean.unrecognised, undefined);
  assert.deepEqual(clean.participants[0].answers, {});
});

test('three constraints and three enablers remain separate for each perspective', () => {
  const record = newRecord(original);
  for (let i = 1; i <= 3; i++) record.participants[0].answers['a1-f' + i] = { constraining: true, enabling: false };
  record.participants[0].answers['a1-f4'] = { enabling: true };
  const clean = validateRecord(record, original);
  assert.equal(clean.participants[0].answers['a1-f4'].enabling, true);
  record.participants[0].answers['a1-f5'] = { constraining: true };
  assert.throws(() => validateRecord(record, original), /at most three/);
});

test('the SCOA archive preserves its own scoring fields without importing later limits', () => {
  assert.equal(adult.sections.length, 8);
  assert.equal(adult.sections.flatMap(s => s.questions).filter(q => q.kind === 'factor').length, 88);
  assert.equal(adult.sections.flatMap(s => s.questions).filter(q => /-q\d+$/.test(q.id)).length, 71);
  assert.equal(adult.scoreBands, undefined);
  const record = newRecord(adult);
  for (let i = 1; i <= 4; i++) record.participants[0].answers['a1-f' + i] = { enabling: true, score: '50' };
  assert.doesNotThrow(() => validateRecord(record, adult));
});

test('the public reflection pack starts with the current task and contains only the selected current perspective', () => {
  const prompt = fs.readFileSync(path.join(__dirname, '../content/compass/sources/smartcompass-public-reflection-2026-11-06.md'), 'utf8');
  const record = newRecord(smart);
  record.title = 'Synthetic assessment';
  record.participants[0].answers['context-1'] = { notes: 'OTHER PERSPECTIVE MARKER' };
  record.participants.push({ id: 'second', label: 'Selected view', answers: { 'context-1': { notes: 'CURRENT CASE MARKER', evidence: 'A dated observation' } } });
  record.decisions.push({ title: 'EXCLUDED ACTION MARKER' });
  record.reviewDraft = ['EXCLUDED DRAFT MARKER'];
  record.reviews.push({ date: '2025-01-01', learning: ['EXCLUDED HISTORY MARKER'], snapshot: { title: '', boundary: '', missing: '', participants: [record.participants[0]], decisions: [] } });
  const pack = reflectionMarkdown(record, smart, prompt, '# Versioned source excerpts\n\nSYNTHETIC REFERENCE', 1);
  assert.ok(pack.startsWith(prompt.trim()));
  assert.ok(pack.indexOf('SYNTHETIC REFERENCE') < pack.indexOf('CURRENT CASE MARKER'));
  assert.ok(pack.includes('Selected perspective:\n\n> Selected view'));
  assert.ok(pack.includes('> CURRENT CASE MARKER') && pack.includes('> A dated observation'));
  for (const marker of ['OTHER PERSPECTIVE MARKER', 'EXCLUDED ACTION MARKER', 'EXCLUDED DRAFT MARKER', 'EXCLUDED HISTORY MARKER', 'BEGIN ORIGINAL PROMPT']) assert.equal(pack.includes(marker), false);
  let position = pack.indexOf('## Current assessment answers');
  for (const q of smart.sections.flatMap(s => s.questions)) { const next = pack.indexOf(q.prompt, position); assert.ok(next > position); position = next; }
  assert.ok(pack.includes('> (Not recorded)'));
  assert.ok(markdown(record, smart).includes('EXCLUDED HISTORY MARKER'));
});

test('reflection packs require an explicit valid perspective and both supplied source files', () => {
  const record = newRecord(smart);
  assert.throws(() => reflectionMarkdown(record, smart, 'Task', 'Reference', 2), /Choose one perspective/);
  assert.throws(() => reflectionMarkdown(record, smart, '', 'Reference', 0), /both be available/);
  assert.throws(() => reflectionMarkdown(record, smart, 'Task', '', 0), /both be available/);
});

test('reflection selection follows a participant identity across removal and requires a choice after selected removal', () => {
  const record = newRecord(smart);
  record.participants = ['A', 'B', 'C'].map(id => ({ id, label: id, answers: {} }));
  assert.equal(selectedPerspectiveIndex(record, 'B'), 1);
  record.participants.splice(0, 1);
  assert.equal(selectedPerspectiveIndex(record, 'B'), 0);
  assert.equal(record.participants[selectedPerspectiveIndex(record, 'B')].label, 'B');
  record.participants.splice(0, 1);
  assert.throws(() => selectedPerspectiveIndex(record, 'B'), /Choose one perspective/);
  assert.throws(() => selectedPerspectiveIndex(record, ''), /Choose one perspective/);
});
