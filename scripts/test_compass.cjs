/* Source fidelity and record portability tests. Run with Node's built-in test runner. */
const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const { newRecord, validateRecord, markdown, reportBlocks, reportHtml, wordDocument, hasRecordContent, editableSize, MAX_IMPORT, reflectionMarkdown, selectedPerspectiveIndex } = require('../assets/compass/compass.js');
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

function exportFixture() {
  const record = newRecord(beta);
  record.title = 'Novi Sad — shared purpose & learning';
  record.boundary = 'A fictional place\nTwo lines, with <boundaries> & different views.';
  record.missing = 'Residents who could not attend.';
  record.participants[0].label = 'Practitioner — Željka';
  record.participants[0].answers['lens-1-move-1'] = { notes: 'Earlier interpretation 🧭', evidence: 'A dated observation' };
  record.decisions.push({ title: 'Try a change', owner: 'Team & residents', due: '2026-12-01', expected: 'Less avoidable work', evidence: 'Look for counterexamples', nextMove: 'Listen again' });
  const snapshot = JSON.parse(JSON.stringify({ title: record.title, boundary: record.boundary, missing: record.missing, participants: record.participants, decisions: record.decisions }));
  record.reviews.push({ date: '2026-11-12T10:00:00Z', learning: ['Earlier learning'], snapshot });
  record.participants[0].answers['lens-1-move-1'].notes = '<img src=x onerror=alert(1)> New interpretation';
  record.reviewDraft[0] = 'Unfinished learning';
  return record;
}

test('print notes use semantic headings, escaped answers, and complete dated snapshots', () => {
  const record = exportFixture();
  const html = reportHtml(record, beta);
  assert.ok(html.startsWith('<h1>Novi Sad — shared purpose &amp; learning</h1>'));
  assert.ok(html.includes('<h2>Current answers</h2>'));
  assert.ok(html.includes('<h3>Whole system conditions</h3>'));
  assert.ok(html.includes('&lt;img src=x onerror=alert(1)&gt; New interpretation'));
  assert.equal(html.includes('<img'), false);
  assert.ok(html.includes('Earlier interpretation 🧭') && html.includes('A dated observation'));
  assert.ok(html.includes('Earlier learning') && html.includes('Unfinished learning'));
  assert.ok(html.includes('People and views not included') && html.includes('Residents who could not attend.'));
  assert.ok(html.includes('Record retained at this review') && html.includes('Team &amp; residents'));
  assert.equal(html.includes(beta.source.url), false);
  assert.equal(html.includes('## '), false);
  assert.equal(reportBlocks(record, beta).filter(b => b.kind === 'prompt').length, 80);
});

test('Word notes are a valid OOXML ZIP with Unicode, styles, safe text, and no external relationships', () => {
  const { spawnSync } = require('node:child_process');
  const bytes = wordDocument(exportFixture(), beta);
  assert.ok(bytes instanceof Uint8Array);
  assert.equal(Buffer.from(bytes).subarray(0, 4).toString('hex'), '504b0304');
  const check = spawnSync('python3', ['-c', `
import io, json, sys, zipfile, xml.etree.ElementTree as ET
with zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read())) as archive:
    assert archive.testzip() is None
    names = archive.namelist()
    assert '[Content_Types].xml' in names and 'word/document.xml' in names
    for name in names:
        ET.fromstring(archive.read(name))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    doc = ET.fromstring(archive.read('word/document.xml'))
    text = '\\n'.join(e.text or '' for e in doc.findall('.//w:t', ns))
    assert 'Practitioner — Željka' in text and 'Earlier interpretation 🧭' in text
    assert '<img src=x onerror=alert(1)> New interpretation' in text
    assert 'A dated observation' in text and 'Team & residents' in text
    assert 'Unfinished learning' in text and 'Earlier learning' in text
    assert 'Residents who could not attend.' in text
    assert 'docs.google.com' not in text
    styles = {e.attrib.get('{'+ns['w']+'}val') for e in doc.findall('.//w:pStyle', ns)}
    assert {'Title', 'Heading1', 'Heading2', 'Heading3', 'Heading4', 'Normal'} <= styles
    for name in names:
        if name.endswith('.rels'):
            for relationship in ET.fromstring(archive.read(name)):
                assert relationship.attrib.get('TargetMode') != 'External'
    print(json.dumps({'entries': len(names), 'paragraphs': len(doc.findall('.//w:p', ns))}))
`], { input: Buffer.from(bytes), encoding: 'utf8' });
  assert.equal(check.status, 0, check.stderr);
  assert.ok(JSON.parse(check.stdout).paragraphs > 100);
});

test('Word output removes XML control characters and repairs unpaired surrogates', () => {
  const { spawnSync } = require('node:child_process');
  const record = newRecord(beta);
  record.title = 'A\u0001B\ud800C';
  const check = spawnSync('python3', ['-c', `import io, sys, zipfile, xml.etree.ElementTree as E
with zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read())) as z:
    data = z.read('word/document.xml')
    E.fromstring(data)
    assert 'AB�C' in data.decode('utf8')`], { input: Buffer.from(wordDocument(record, beta)), encoding: 'utf8' });
  assert.equal(check.status, 0, check.stderr);
});

test('unsaved-work detection includes evidence, zero scores, review drafts, and role labels', () => {
  const empty = newRecord(beta);
  assert.equal(hasRecordContent(empty), false);
  empty.participants[0].answers['lens-1-move-1'] = { notes: '', evidence: 'Evidence only' };
  assert.equal(hasRecordContent(empty), true);
  empty.participants[0].answers = {};
  empty.reviewDraft[0] = 'Unfinished thought';
  assert.equal(hasRecordContent(empty), true);
  empty.reviewDraft[0] = '';
  empty.participants[0].label = 'Resident';
  assert.equal(hasRecordContent(empty), true);
  const scored = newRecord(original);
  scored.participants[0].answers['a1-q1'] = { score: '0' };
  assert.equal(hasRecordContent(scored), true);
});

test('substantial review history remains within the reopening limit and round-trips intact', () => {
  const record = newRecord(beta);
  for (const q of beta.sections.flatMap(s => s.questions)) record.participants[0].answers[q.id] = { notes: 'A'.repeat(19000), evidence: 'Observed' };
  const snapshot = JSON.parse(JSON.stringify({ title: record.title, boundary: record.boundary, missing: record.missing, participants: record.participants, decisions: record.decisions }));
  record.reviews = [0, 1, 2].map(i => ({ date: '2026-11-' + (10 + i), learning: ['Review ' + i], snapshot }));
  assert.ok(editableSize(record) > 1500000);
  assert.ok(editableSize(record) < MAX_IMPORT);
  const reopened = validateRecord(JSON.parse(JSON.stringify(record)), beta);
  assert.equal(reopened.reviews.length, 3);
  assert.equal(reopened.reviews[2].snapshot.participants[0].answers['lens-8-move-5'].notes.length, 19000);
});
