/* PSTA Compass: local inquiry records, with no account or submission endpoint. */
(function (root) {
  'use strict';
  const SCHEMA = 'psta-compass-session';
  const MAX_IMPORT = 1500000;
  const uid = () => 'r' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
  const str = (value, limit = 20000) => typeof value === 'string' ? value.slice(0, limit) : '';
  const fields = ['title', 'owner', 'due', 'expected', 'evidence', 'nextMove'];
  const questionIds = tool => new Set(tool.sections.flatMap(s => s.questions.map(q => q.id)));
  const has = (obj, key) => Object.prototype.hasOwnProperty.call(obj, key);

  function newRecord(tool) {
    return {
      schema: SCHEMA, schemaVersion: 1, toolId: tool.id, toolVersion: tool.version,
      title: '', boundary: '', missing: '', participants: [{ id: uid(), label: 'My view', answers: {} }],
      decisions: [], reviews: [], reviewDraft: (tool.reviewQuestions || []).map(() => ''), updated: new Date().toISOString(),
    };
  }

  function cleanParticipants(input, tool) {
    if (!Array.isArray(input) || !input.length || input.length > 20) throw Error('A record needs between one and twenty perspectives.');
    const allowed = questionIds(tool);
    const questions = Object.fromEntries(tool.sections.flatMap(s => s.questions.map(q => [q.id, q])));
    return input.map((p, i) => {
      if (!p || typeof p !== 'object') throw Error('A perspective could not be read.');
      const answers = {};
      for (const id of allowed) {
        if (p.answers && has(p.answers, id)) {
          const a = p.answers[id];
          if (!a || typeof a !== 'object') throw Error('An answer could not be read.');
          const score = str(a.score, 30);
          const finalScore = str(a.finalScore, 30);
          const q = questions[id];
          if (score && q.range && (!/^\d+$/.test(score) || Number(score) < q.range.min || Number(score) > q.range.max)) throw Error('A score is outside this edition’s range.');
          if (finalScore && q.finalScore && (!/^\d+$/.test(finalScore) || Number(finalScore) < q.range.min || Number(finalScore) > q.range.max)) throw Error('A final score is outside this edition’s range.');
          if (score && q.scale && !q.scale.some(s => String(s.value) === score)) throw Error('A score does not match this edition’s scale.');
          answers[id] = { notes: str(a.notes), evidence: str(a.evidence), score, finalScore: q.finalScore ? finalScore : '', constraining: a.constraining === true, enabling: a.enabling === true };
        }
      }
      for (const section of tool.sections) {
        for (const choice of ['constraining', 'enabling']) {
          if (tool.factorLimit && section.questions.filter(q => q.kind === 'factor' && answers[q.id]?.[choice]).length > tool.factorLimit) throw Error('Choose at most three constraints and three enablers per aspect.');
        }
      }
      return { id: 'perspective-' + i, label: str(p.label, 100) || 'Perspective ' + (i + 1), answers };
    });
  }

  function cleanDecisions(input) {
    if (!Array.isArray(input) || input.length > 50) throw Error('The decision list could not be read.');
    return input.map((d, i) => {
      if (!d || typeof d !== 'object') throw Error('A decision could not be read.');
      return Object.fromEntries([['id', 'decision-' + i], ...fields.map(f => [f, str(d[f], f === 'due' ? 10 : 20000)])]);
    });
  }

  function validateRecord(input, tool) {
    if (!input || input.schema !== SCHEMA || input.schemaVersion !== 1) throw Error('Choose a PSTA Compass JSON record, exported by this tool.');
    if (input.toolId !== tool.id || input.toolVersion !== tool.version) throw Error('This record belongs to a different Compass edition. Open that edition to import it.');
    if (!Array.isArray(input.reviews) || input.reviews.length > 100) throw Error('The review history could not be read.');
    return {
      schema: SCHEMA, schemaVersion: 1, toolId: tool.id, toolVersion: tool.version,
      title: str(input.title, 200), boundary: str(input.boundary), missing: str(input.missing),
      participants: cleanParticipants(input.participants, tool), decisions: cleanDecisions(input.decisions),
      reviewDraft: (tool.reviewQuestions || []).map((_, i) => str(Array.isArray(input.reviewDraft) ? input.reviewDraft[i] : '')),
      reviews: input.reviews.map((r, i) => {
        if (!r || typeof r !== 'object' || !r.snapshot) throw Error('A review could not be read.');
        return {
          id: 'review-' + i, date: str(r.date, 30),
          learning: (tool.reviewQuestions || []).map((_, n) => str(Array.isArray(r.learning) ? r.learning[n] : '')),
          snapshot: {
            title: str(r.snapshot.title, 200), boundary: str(r.snapshot.boundary), missing: str(r.snapshot.missing),
            participants: cleanParticipants(r.snapshot.participants, tool), decisions: cleanDecisions(r.snapshot.decisions),
          },
        };
      }),
      updated: str(input.updated, 30),
    };
  }

  function markdown(record, tool) {
    const lines = ['# ' + (record.title || tool.title), '', tool.title + ' · ' + tool.version, '', '## System of interest', '', record.boundary || '(Not recorded)', '', '## Missing perspectives', '', record.missing || '(Not recorded)', ''];
    function answers(participants, sections, level = '##') {
      for (const section of sections) {
        lines.push(level + ' ' + section.title, '');
        for (const q of section.questions) {
          lines.push((q.label ? '**' + q.label + '**: ' : '') + q.prompt, '');
          for (const p of participants) {
            const a = p.answers[q.id] || {};
            lines.push('**' + p.label + '**', '', a.notes || '(No notes)', '');
            if (a.score) lines.push('Indicative score: ' + a.score, '');
            if (a.finalScore) lines.push('Finalised score after evidence: ' + a.finalScore, '');
            if (a.constraining) lines.push('Selected as one of the most constraining factors.', '');
            if (a.enabling) lines.push('Selected as one of the most enabling factors.', '');
            if (a.evidence) lines.push('Evidence / uncertainty: ' + a.evidence, '');
          }
        }
      }
    }
    function decisions(items, level = '##') {
      lines.push(level + ' Decisions and experiments', '');
      if (!items.length) lines.push('(None recorded)', '');
      items.forEach((d, i) => {
        lines.push('### ' + (i + 1) + '. ' + (d.title || 'Untitled decision'), '', 'Owner: ' + d.owner, '', 'Review date: ' + d.due, '', 'What we expect to change: ' + d.expected, '', 'Evidence that could support or challenge this: ' + d.evidence, '', 'Next move: ' + d.nextMove, '');
      });
    }
    answers(record.participants, tool.sections);
    decisions(record.decisions);
    if ((record.reviewDraft || []).some(Boolean)) {
      lines.push('## Review in progress', '');
      (tool.reviewQuestions || []).forEach((q, i) => lines.push('**' + q + '**', '', record.reviewDraft[i] || '(Not recorded)', ''));
    }
    lines.push('## Review history', '');
    record.reviews.forEach((r, i) => {
      lines.push('### Review ' + (i + 1) + ' · ' + r.date, '', 'System of interest at this review: ' + r.snapshot.boundary, '');
      (tool.reviewQuestions || []).forEach((q, n) => lines.push('**' + q + '**', '', r.learning[n] || '(Not recorded)', ''));
      answers(r.snapshot.participants, tool.sections, '####');
      decisions(r.snapshot.decisions, '####');
    });
    lines.push('## Source and edition', '', tool.source.title, '', tool.source.url, '', tool.source.note || '', '', 'This record contains participants’ judgements and notes. It is not a benchmark or an automated diagnosis.', '');
    return lines.join('\n');
  }

  const api = { newRecord, validateRecord, markdown, MAX_IMPORT };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (!root.document) return;

  const node = document.getElementById('compass-app');
  const payload = document.getElementById('compass-tool-data');
  if (!node || !payload) return;
  const tool = JSON.parse(payload.textContent);
  const key = 'psta-compass:' + tool.id + ':' + tool.version;
  let record = newRecord(tool);
  let saved = false;
  let message = '';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const label = (text, control, hint = '') => '<label>' + esc(text) + control + '</label>' + (hint ? '<p class="compass-hint">' + esc(hint) + '</p>' : '');
  const textarea = (attrs, value) => '<textarea rows="3" ' + attrs + '>' + esc(value) + '</textarea>';
  const input = (attrs, value) => '<input ' + attrs + ' value="' + esc(value) + '">';
  const button = (action, text, extra = '') => '<button type="button" data-action="' + action + '" ' + extra + '>' + esc(text) + '</button>';
  const fileName = () => (record.title || tool.id).toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-|-$/g, '').slice(0, 70) || tool.id;
  try {
    const stored = localStorage.getItem(key);
    if (stored) { record = validateRecord(JSON.parse(stored), tool); saved = true; message = 'Your saved record has been restored from this device.'; }
  } catch (_) { message = 'A saved record could not be restored. You can still work here and download a copy.'; }

  function status(text) {
    message = text;
    const live = document.getElementById('compass-status');
    if (live) live.textContent = text;
  }
  function changed() {
    record.updated = new Date().toISOString();
    if (saved) {
      try { localStorage.setItem(key, JSON.stringify(record)); status('Saved on this device at ' + new Date().toLocaleTimeString('en-GB') + '. Download a copy to keep or share it.'); }
      catch (_) { saved = false; status('This device could not save the latest changes. Download a JSON copy now.'); }
    } else status('Changes are in this open page. Save on this device or download a copy before leaving.');
  }
  function download(name, content, mime) {
    const url = URL.createObjectURL(new Blob([content], { type: mime }));
    const a = document.createElement('a'); a.href = url; a.download = name; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  function render() {
    node.innerHTML = '<div class="compass-controls">' + button('save', 'Save on this device') + button('json', 'Download editable record') + button('markdown', 'Download readable notes') + button('print', 'Print / save PDF') + '<label class="compass-file">Open a saved record<input type="file" id="compass-import" accept="application/json,.json"></label>' + button('remove', 'Remove device copy') + button('new', 'Start a new record') + '</div><p id="compass-status" class="compass-status" role="status" aria-live="polite">' + esc(message || 'Your answers stay in this open page until you choose to save or download them.') + '</p>' +
      (tool.agentPrompt ? '<section><h2>Prepare an AI reflection</h2><p>Download the preserved original PSTA draft prompt with the answers in this record. Check the file, remove anything you should not share, and run it in your authorised AI account. This page does not generate a response, email a result, or send your answers to an AI service.</p>' + button('ai-pack', 'Download the AI handoff pack') + '<p class="compass-hint">' + esc(tool.agentPrompt.note) + '</p></section>' : '') +
      '<section class="compass-context"><h2>Your inquiry</h2>' +
      label('Name this inquiry', input('data-record="title" maxlength="200"', record.title)) +
      label('System of interest: what are you paying attention to, and why?', textarea('data-record="boundary"', record.boundary)) +
      label('Who is affected but absent? What might your boundary leave out?', textarea('data-record="missing"', record.missing)) +
      '<h3>Keep different views visible</h3><p>Use a role or short label for each perspective. Compare the reasons behind different accounts before seeking agreement. Add only material that you have permission to record.</p>' +
      record.participants.map((p, i) => '<div class="compass-perspective-label">' + label('Perspective ' + (i + 1), input('data-person="' + i + '" maxlength="100"', p.label)) + (record.participants.length > 1 ? button('remove-person', 'Remove perspective', 'data-index="' + i + '"') : '') + '</div>').join('') +
      button('add-person', 'Add another perspective') + '</section>' +
      '<section><h2>Explore the Compass</h2><p>Open the lens you need. There is no required order or overall grade. Empty answers remain empty.</p>' + (tool.instructions?.length || tool.scoreBands ? '<details><summary>Original instructions' + (tool.scoreBands ? ' and scoring bands' : '') + '</summary><p>Scores remain the people’s self-assessments.</p>' + (tool.scoreBands ? '<ul>' + tool.scoreBands.map(s => '<li>' + esc(s) + '</li>').join('') + '</ul>' : '') + (tool.instructions || []).filter(p => !(tool.scoreBands || []).includes(p)).map(p => '<p>' + esc(p) + '</p>').join('') + '</details>' : '') + '<div class="compass-lenses">' +
      tool.sections.map((section, si) => '<details class="compass-lens" data-section="' + si + '"><summary>' + esc(section.title) + '</summary>' + (section.description ? '<p>' + esc(section.description) + '</p>' : '') + section.questions.map(q => '<div class="compass-question"><h3>' + esc(q.label || 'Question') + '</h3><p>' + esc(q.prompt) + '</p><div class="compass-views">' + record.participants.map((p, pi) => {
        const a = p.answers[q.id] || {};
        const attrs = 'data-question="' + esc(q.id) + '" data-perspective="' + pi + '"';
        return '<fieldset><legend data-perspective-label="' + pi + '">' + esc(p.label) + '</legend>' + (q.range ? label((q.finalScore ? 'Initial score' : 'Self-assessment score') + ' /' + q.range.max + ' (optional)', input(attrs + ' data-answer="score" type="number" min="' + q.range.min + '" max="' + q.range.max + '" step="' + q.range.step + '"', a.score || '')) : '') + (q.scale ? label('Indicative score', '<select ' + attrs + ' data-answer="score"><option value="">Not scored</option>' + q.scale.map(s => '<option value="' + esc(s.value) + '"' + (String(s.value) === a.score ? ' selected' : '') + '>' + esc(s.label) + '</option>').join('') + '</select>') : '') + (q.kind === 'factor' ? '<label class="compass-factor-choice"><input type="checkbox" ' + attrs + ' data-answer="constraining"' + (a.constraining ? ' checked' : '') + '> ' + (tool.factorLimit === 3 ? 'One of the three most constraining' : 'Most constraining') + '</label><label class="compass-factor-choice"><input type="checkbox" ' + attrs + ' data-answer="enabling"' + (a.enabling ? ' checked' : '') + '> ' + (tool.factorLimit === 3 ? 'One of the three most enabling' : 'Most enabling') + '</label>' : '') + label('What do you see?', textarea(attrs + ' data-answer="notes"', a.notes || '')) + label('Evidence, uncertainty, or a different interpretation', textarea(attrs + ' data-answer="evidence"', a.evidence || '')) + (q.finalScore ? label('Finalised score after evidence /100 (optional)', input(attrs + ' data-answer="finalScore" type="number" min="0" max="100" step="1"', a.finalScore || '')) : '') + '</fieldset>';
      }).join('') + '</div></div>').join('') + '</details>').join('') + '</div></section>' +
      '<section><h2>Decisions and experiments</h2><p>Choose a move that could change a real condition. Make the expectation, responsibility, evidence, and review date explicit.</p>' +
      record.decisions.map((d, i) => '<fieldset class="compass-decision"><legend>Decision ' + (i + 1) + '</legend>' + [
        ['title', 'What will you change?', false], ['owner', 'Who can act, and who needs to agree?', false], ['due', 'When will you review it?', false],
        ['expected', 'What do you expect to change, for whom?', true], ['evidence', 'What would support or challenge that expectation?', true], ['nextMove', 'What is the next practical move?', true],
      ].map(([f, text, area]) => label(text, area ? textarea('data-decision="' + i + '" data-field="' + f + '"', d[f]) : input('data-decision="' + i + '" data-field="' + f + '"' + (f === 'due' ? ' type="date"' : ''), d[f]))).join('') + button('remove-decision', 'Remove decision', 'data-index="' + i + '"') + '</fieldset>').join('') + button('add-decision', 'Add a decision or experiment') + '</section>' +
      '<section><h2>Return to what happened</h2><p>A review keeps a dated snapshot of the current answers and decisions. It preserves disagreement and uncertainty; it does not turn the record into a score.</p>' + (tool.reviewSourceNote ? '<p class="compass-hint">' + esc(tool.reviewSourceNote) + '</p>' : '') +
      (tool.reviewQuestions || []).map((q, i) => label(q, textarea('data-learning="' + i + '"', record.reviewDraft[i] || ''))).join('') + button('review', 'Record this review') +
      '<div class="compass-history">' + record.reviews.map((r, i) => '<details><summary>Review ' + (i + 1) + ' · ' + esc(r.date) + '</summary><p><strong>Boundary at this review:</strong> ' + esc(r.snapshot.boundary) + '</p>' + (tool.reviewQuestions || []).map((q, n) => '<h3>' + esc(q) + '</h3><p class="compass-pre">' + esc(r.learning[n] || 'No answer recorded') + '</p>').join('') + '<p>' + r.snapshot.participants.length + ' perspective(s), ' + r.snapshot.decisions.length + ' decision(s). The full snapshot is included in both downloads.</p></details>').join('') + '</div></section><section><h2>Source and edition</h2><p>' + esc(tool.source.note || '') + '</p><p><a href="' + esc(tool.source.localText || tool.source.url) + '">Read the source</a> · Edition ' + esc(tool.version) + '</p></section>';
    node.querySelectorAll('input,textarea').forEach(control => control.setAttribute('autocomplete', 'off'));
  }

  node.addEventListener('input', event => {
    const t = event.target;
    if (t.hasAttribute('data-record')) record[t.dataset.record] = t.value;
    else if (t.hasAttribute('data-person')) {
      record.participants[Number(t.dataset.person)].label = t.value;
      node.querySelectorAll('[data-perspective-label="' + t.dataset.person + '"]').forEach(legend => { legend.textContent = t.value; });
    }
    else if (t.hasAttribute('data-answer')) {
      const p = record.participants[Number(t.dataset.perspective)];
      p.answers[t.dataset.question] ||= { notes: '', evidence: '', score: '' };
      if (t.type === 'checkbox') {
        const section = tool.sections.find(s => s.questions.some(q => q.id === t.dataset.question));
        const count = section.questions.filter(q => q.kind === 'factor' && p.answers[q.id]?.[t.dataset.answer]).length;
        if (t.checked && tool.factorLimit && count >= tool.factorLimit) { t.checked = false; return status('Choose at most three of the most constraining and three of the most enabling factors for each aspect and perspective.'); }
        p.answers[t.dataset.question][t.dataset.answer] = t.checked;
      } else {
        if (t.type === 'number' && t.value !== '') t.value = String(Math.max(Number(t.min), Math.min(Number(t.max), Math.round(Number(t.value)))));
        p.answers[t.dataset.question][t.dataset.answer] = t.value;
      }
    } else if (t.hasAttribute('data-decision')) record.decisions[Number(t.dataset.decision)][t.dataset.field] = t.value;
    else if (t.hasAttribute('data-learning')) record.reviewDraft[Number(t.dataset.learning)] = t.value;
    else return;
    changed();
  });

  node.addEventListener('change', async event => {
    if (event.target.id !== 'compass-import') return;
    const file = event.target.files[0];
    if (!file) return;
    try {
      if (file.size > MAX_IMPORT) throw Error('This file is too large for a Compass record.');
      const imported = validateRecord(JSON.parse(await file.text()), tool);
      if (!confirm('Replace the record in this open page? Download the current record first if you need to keep it.')) return;
      record = imported; changed(); render(); status('The record has been opened. ' + (saved ? 'It is also saved on this device.' : 'Choose Save on this device if you want it restored next time.'));
    } catch (error) { status(error.message || 'The file could not be read.'); }
  });

  node.addEventListener('click', async event => {
    const b = event.target.closest('[data-action]');
    if (!b) return;
    const action = b.dataset.action;
    if (action === 'save') { saved = true; changed(); }
    if (action === 'json') download(fileName() + '.json', JSON.stringify(record, null, 2), 'application/json');
    if (action === 'markdown') download(fileName() + '.md', markdown(record, tool), 'text/markdown;charset=utf-8');
    if (action === 'ai-pack' && tool.agentPrompt) {
      try {
        const response = await fetch(tool.agentPrompt.path, { credentials: 'omit', cache: 'no-store' });
        if (!response.ok) throw Error('The preserved prompt could not be loaded. Your record is unchanged.');
        const original = await response.text();
        const pack = 'PSTA smartCompass AI handoff pack\n\nOriginal prompt: ' + tool.agentPrompt.version + '\n' + tool.agentPrompt.note + '\n\nCheck this file before sharing it with an authorised AI service. No AI response has been generated by this page.\n\nBEGIN ORIGINAL PROMPT (VERBATIM)\n\n' + original + '\n\nEND ORIGINAL PROMPT\n\nBEGIN RESPONSES FOR THIS RUN\n\nName and email: not supplied in this local reflection edition. Do not invent a name or contact detail.\n\n' + markdown(record, tool) + '\nEND RESPONSES\n';
        download(fileName() + '-ai-handoff.txt', pack, 'text/plain;charset=utf-8');
        status('The original prompt and your answers have been downloaded. No AI service has been called.');
      } catch (error) { status(error.message || 'The handoff pack could not be prepared.'); }
    }
    if (action === 'print') {
      let report = document.getElementById('compass-print');
      if (!report) { report = document.createElement('pre'); report.id = 'compass-print'; document.body.appendChild(report); }
      report.textContent = markdown(record, tool); window.print();
    }
    if (action === 'remove') {
      try { localStorage.removeItem(key); saved = false; status('The device copy has been removed. Your open record and downloaded files are unchanged.'); }
      catch (_) { status('This browser could not remove the device copy. Use its site-data settings to clear it.'); }
    }
    if (action === 'new' && confirm('Start a new record? Download this one first if you need to keep it.')) {
      try { localStorage.removeItem(key); } catch (_) { /* New page state remains usable. */ }
      record = newRecord(tool); saved = false; message = 'A new record is open.'; render();
    }
    if (action === 'add-person') {
      if (record.participants.length >= 20) return status('This record already has twenty perspectives.');
      record.participants.push({ id: uid(), label: 'Perspective ' + (record.participants.length + 1), answers: {} }); changed(); render();
    }
    if (action === 'remove-person' && confirm('Remove this perspective and its answers from the current record? Earlier review snapshots remain.')) { record.participants.splice(Number(b.dataset.index), 1); changed(); render(); }
    if (action === 'add-decision') {
      if (record.decisions.length >= 50) return status('This record already has fifty decisions.');
      record.decisions.push(Object.fromEntries([['id', uid()], ...fields.map(f => [f, ''])])); changed(); render();
    }
    if (action === 'remove-decision' && confirm('Remove this decision from the current record? Earlier review snapshots remain.')) { record.decisions.splice(Number(b.dataset.index), 1); changed(); render(); }
    if (action === 'review') {
      if (record.reviews.length >= 100) return status('This record already has one hundred reviews. Download it and begin a new record.');
      const learning = (tool.reviewQuestions || []).map((_, i) => node.querySelector('[data-learning="' + i + '"]').value);
      record.reviews.push({ id: uid(), date: new Date().toISOString(), learning, snapshot: JSON.parse(JSON.stringify({ title: record.title, boundary: record.boundary, missing: record.missing, participants: record.participants, decisions: record.decisions })) });
      record.reviewDraft = (tool.reviewQuestions || []).map(() => '');
      changed(); render(); status('Review recorded with a snapshot of the current perspectives and decisions.');
    }
  });
  render();
})(typeof window === 'undefined' ? globalThis : window);
