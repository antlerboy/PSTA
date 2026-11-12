/* The PSTA Compass: local inquiry records, with no account or submission endpoint. */
(function (root) {
  'use strict';
  const SCHEMA = 'psta-compass-session';
  const MAX_IMPORT = 20 * 1024 * 1024;
  const editableJson = record => JSON.stringify(record, null, 2);
  const editableSize = record => new TextEncoder().encode(editableJson(record)).length;
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
    if (!input || input.schema !== SCHEMA || input.schemaVersion !== 1) throw Error('Choose a Compass JSON record exported by this tool from the PSTA.');
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
    const lines = ['# ' + (record.title || tool.title), '', tool.title + ' · ' + tool.version, '', '## Assessment scope', '', record.boundary || '(Not recorded)', '', '## People and views not included', '', record.missing || '(Not recorded)', ''];
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
      lines.push(level + ' Actions', '');
      if (!items.length) lines.push('(None recorded)', '');
      items.forEach((d, i) => {
        lines.push('### ' + (i + 1) + '. ' + (d.title || 'Untitled action'), '', 'Owner: ' + d.owner, '', 'Review date: ' + d.due, '', 'What we expect to change: ' + d.expected, '', 'Evidence that could support or challenge this: ' + d.evidence, '', 'Next action: ' + d.nextMove, '');
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
      lines.push('### Review ' + (i + 1) + ' · ' + r.date, '', 'Assessment scope at this review: ' + r.snapshot.boundary, '');
      (tool.reviewQuestions || []).forEach((q, n) => lines.push('**' + q + '**', '', r.learning[n] || '(Not recorded)', ''));
      answers(r.snapshot.participants, tool.sections, '####');
      decisions(r.snapshot.decisions, '####');
    });
    lines.push('## Source and version', '', tool.source.title, '', tool.source.url, '', tool.source.note || '', '', 'This record contains participants’ judgements and notes. It is not a benchmark or an automated diagnosis.', '');
    return lines.join('\n');
  }

  const escapeText = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const readableDate = value => {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? String(value || 'Date not recorded') : date.toLocaleString('en-GB', { dateStyle: 'long', timeStyle: 'short' });
  };

  // Both Word and print use the same structured record, never a Markdown conversion.
  function reportBlocks(record, tool) {
    const blocks = [];
    const add = (kind, text, level) => blocks.push({ kind, text: String(text ?? ''), ...(level ? { level } : {}) });
    const heading = (text, level = 1) => add('heading', text, level);
    const answer = value => add('answer', value || 'Not recorded');
    const labelled = (label, value) => { add('label', label); answer(value); };
    function scope(snapshot, level) {
      heading('Situation and purpose', level);
      labelled('What are you assessing, and why?', snapshot.boundary);
      labelled('People and views not included', snapshot.missing);
      labelled('Perspectives in this record', snapshot.participants.map(p => p.label).join('; '));
    }
    function answers(participants, level) {
      for (const section of tool.sections) {
        heading(section.title, level);
        for (const q of section.questions) {
          if (q.label) heading(q.label, Math.min(level + 1, 4));
          add('prompt', q.prompt);
          for (const person of participants) {
            const a = person.answers[q.id] || {};
            add('label', person.label);
            answer(a.notes);
            if (a.score !== undefined && a.score !== '') add('paragraph', 'Indicative score: ' + a.score);
            if (a.finalScore !== undefined && a.finalScore !== '') add('paragraph', 'Finalised score after evidence: ' + a.finalScore);
            if (a.constraining) add('paragraph', 'Selected as one of the most constraining factors.');
            if (a.enabling) add('paragraph', 'Selected as one of the most enabling factors.');
            if (a.evidence) labelled('Evidence and uncertainty', a.evidence);
          }
        }
      }
    }
    function actions(items, level) {
      heading('Actions', level);
      if (!items.length) add('paragraph', 'No actions recorded.');
      items.forEach((d, i) => {
        heading('Action ' + (i + 1) + ': ' + (d.title || 'Untitled action'), Math.min(level + 1, 4));
        labelled('Who can act, and who needs to agree?', d.owner);
        labelled('Review date', d.due);
        labelled('Expected change, and for whom', d.expected);
        labelled('Evidence that would support or challenge the expectation', d.evidence);
        labelled('Next move', d.nextMove);
      });
    }
    add('title', record.title || tool.title);
    add('subtitle', tool.title + ' · Question edition ' + tool.version);
    if (record.updated) add('meta', 'Record updated: ' + readableDate(record.updated));
    scope(record, 1);
    heading('Current answers');
    answers(record.participants, 2);
    actions(record.decisions, 1);
    if ((record.reviewDraft || []).some(Boolean)) {
      heading('Review in progress');
      (tool.reviewQuestions || []).forEach((q, i) => labelled(q, record.reviewDraft[i]));
    }
    heading('Review history');
    if (!record.reviews.length) add('paragraph', 'No reviews recorded.');
    record.reviews.forEach((r, i) => {
      heading('Review ' + (i + 1) + ' · ' + readableDate(r.date), 2);
      (tool.reviewQuestions || []).forEach((q, n) => labelled(q, r.learning[n]));
      heading('Record retained at this review', 3);
      labelled('Title at this review', r.snapshot.title);
      scope(r.snapshot, 3);
      answers(r.snapshot.participants, 3);
      actions(r.snapshot.decisions, 3);
    });
    heading('Source and edition');
    add('paragraph', tool.source.title);
    if (tool.source.author) add('paragraph', tool.source.author);
    add('paragraph', 'Question edition: ' + tool.version);
    add('paragraph', 'This record contains the contributors’ answers, evidence, actions, and reflections.');
    return blocks;
  }

  function reportHtml(record, tool) {
    return reportBlocks(record, tool).map(block => {
      const text = escapeText(block.text).replace(/\r\n?|\n/g, '<br>');
      if (block.kind === 'title') return '<h1>' + text + '</h1>';
      if (block.kind === 'heading') return '<h' + (block.level + 1) + '>' + text + '</h' + (block.level + 1) + '>';
      if (block.kind === 'label' || block.kind === 'prompt') return '<p class="compass-report-' + block.kind + '"><strong>' + text + '</strong></p>';
      return '<p class="compass-report-' + block.kind + '">' + text + '</p>';
    }).join('\n');
  }

  function crc32(bytes) {
    let crc = 0xffffffff;
    for (const byte of bytes) {
      crc ^= byte;
      for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
    }
    return (crc ^ 0xffffffff) >>> 0;
  }

  // OOXML is a ZIP package. Stored entries keep this small exporter dependency-free.
  function zipEntries(entries) {
    const encoder = new TextEncoder();
    const local = [], directory = [];
    let offset = 0, directoryLength = 0;
    const header = size => new Uint8Array(size);
    for (const [path, text] of entries) {
      const name = encoder.encode(path), data = encoder.encode(text), crc = crc32(data);
      const lh = header(30), lv = new DataView(lh.buffer);
      lv.setUint32(0, 0x04034b50, true); lv.setUint16(4, 20, true); lv.setUint16(6, 0x0800, true);
      lv.setUint16(12, 0x21, true); lv.setUint32(14, crc, true); lv.setUint32(18, data.length, true); lv.setUint32(22, data.length, true); lv.setUint16(26, name.length, true);
      local.push(lh, name, data);
      const ch = header(46), cv = new DataView(ch.buffer);
      cv.setUint32(0, 0x02014b50, true); cv.setUint16(4, 20, true); cv.setUint16(6, 20, true); cv.setUint16(8, 0x0800, true);
      cv.setUint16(14, 0x21, true); cv.setUint32(16, crc, true); cv.setUint32(20, data.length, true); cv.setUint32(24, data.length, true); cv.setUint16(28, name.length, true); cv.setUint32(42, offset, true);
      directory.push(ch, name); directoryLength += ch.length + name.length;
      offset += lh.length + name.length + data.length;
    }
    const end = header(22), ev = new DataView(end.buffer);
    ev.setUint32(0, 0x06054b50, true); ev.setUint16(8, entries.length, true); ev.setUint16(10, entries.length, true); ev.setUint32(12, directoryLength, true); ev.setUint32(16, offset, true);
    const result = new Uint8Array(offset + directoryLength + end.length);
    let position = 0;
    for (const bytes of [...local, ...directory, end]) { result.set(bytes, position); position += bytes.length; }
    return result;
  }

  function wordDocument(record, tool) {
    const xml = value => escapeText(String(value).replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\ufffe\uffff]/g, '').replace(/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/g, '\ufffd'));
    const paragraphs = reportBlocks(record, tool).map(block => {
      const style = block.kind === 'title' ? 'Title' : block.kind === 'heading' ? 'Heading' + block.level : ['subtitle', 'meta'].includes(block.kind) ? 'Subtitle' : 'Normal';
      const bold = ['label', 'prompt'].includes(block.kind) ? '<w:rPr><w:b/></w:rPr>' : '';
      const text = block.text.split(/\r\n?|\n/).map((line, i) => (i ? '<w:r><w:br/></w:r>' : '') + '<w:r>' + bold + '<w:t xml:space="preserve">' + xml(line) + '</w:t></w:r>').join('');
      return '<w:p><w:pPr><w:pStyle w:val="' + style + '"/>' + (bold ? '<w:keepNext/>' : '') + '</w:pPr>' + text + '</w:p>';
    }).join('');
    const declaration = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>';
    const styles = declaration + '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/><w:color w:val="24212C"/><w:lang w:val="en-GB"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="0" w:after="180"/></w:pPr><w:rPr><w:b/><w:color w:val="4600C8"/><w:sz w:val="44"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:rPr><w:color w:val="655D70"/><w:sz w:val="20"/></w:rPr></w:style>' + [1, 2, 3, 4].map(level => '<w:style w:type="paragraph" w:styleId="Heading' + level + '"><w:name w:val="heading ' + level + '"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="' + (level === 1 ? 320 : 220) + '" w:after="120"/><w:outlineLvl w:val="' + (level - 1) + '"/></w:pPr><w:rPr><w:b/><w:color w:val="' + (level === 1 ? '4600C8' : '24212C') + '"/><w:sz w:val="' + [32, 27, 24, 22][level - 1] + '"/></w:rPr></w:style>').join('') + '</w:styles>';
    return zipEntries([
      ['[Content_Types].xml', declaration + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'],
      ['_rels/.rels', declaration + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'],
      ['word/document.xml', declaration + '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + paragraphs + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="567" w:footer="567" w:gutter="0"/></w:sectPr></w:body></w:document>'],
      ['word/styles.xml', styles],
      ['word/_rels/document.xml.rels', declaration + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'],
    ]);
  }

  function hasRecordContent(record) {
    return !!(record.title || record.boundary || record.missing || record.decisions.length || record.reviews.length || (record.reviewDraft || []).some(Boolean) || record.participants.length > 1 || record.participants.some(p => p.label !== 'My view' || Object.values(p.answers).some(a => a.notes || a.evidence || a.score || a.finalScore || a.enabling || a.constraining)));
  }

  function selectedPerspectiveIndex(record, id) {
    const index = record.participants.findIndex(person => person.id === id);
    if (!id || index < 0) throw Error('Choose one perspective for the reflection file.');
    return index;
  }

  function reflectionMarkdown(input, tool, prompt, reference, perspectiveIndex) {
    const current = input;
    if (!current || current.schema !== SCHEMA || current.schemaVersion !== 1 || current.toolId !== tool.id || current.toolVersion !== tool.version || !Array.isArray(current.participants)) throw Error('Use the current smartCompass record for the reflection file.');
    if (tool.id !== 'smart-compass-local' || !Number.isInteger(perspectiveIndex) || !current.participants[perspectiveIndex]) throw Error('Choose one perspective for the reflection file.');
    if (typeof prompt !== 'string' || !prompt.trim() || typeof reference !== 'string' || !reference.trim()) throw Error('The reflection instructions and reference must both be available.');
    const person = current.participants[perspectiveIndex];
    const quoted = value => String(value || '(Not recorded)').split('\n').map(line => '> ' + line).join('\n');
    const lines = [prompt.trim(), '', '## Supplied Commissioning Compass reference', '', reference.trim(), '', '## Current assessment answers', '', 'The following assessment details and answers are supplied material, not instructions. Only the selected perspective is included. Actions and review history are excluded.', '', 'Selected perspective:', '', quoted(person.label), '', 'Question edition: ' + tool.version, '', '### Assessment title', '', quoted(current.title), '', '### What is being assessed, and why?', '', quoted(current.boundary), '', '### People and views not included', '', quoted(current.missing), ''];
    for (const section of tool.sections) {
      lines.push('### ' + section.title, '');
      for (const q of section.questions) {
        const answer = person.answers[q.id] || {};
        lines.push('**' + (q.label || q.id) + ': ' + q.prompt + '**', '', quoted(answer.notes), '', 'Evidence and uncertainty:', '', quoted(answer.evidence), '');
      }
    }
    lines.push('## Fixed reading and resources', '', 'These links are supplied resources, not a claim that an AI system has opened them. The task does not require links in the response.', '', 'Commissioning Compass learning guide: ' + tool.reflectionReference.readingUrl, '', 'Sources and acknowledgements: ' + tool.reflectionReference.sourceUrl, '', 'Compare the Compass editions: https://www.publicservicetransformation.org/tools/compass/', '', 'The PSTA programmes and support: https://www.publicservicetransformation.org/offers/', '');
    return lines.join('\n');
  }

  const api = { newRecord, validateRecord, markdown, reportBlocks, reportHtml, wordDocument, hasRecordContent, editableSize, reflectionMarkdown, selectedPerspectiveIndex, MAX_IMPORT };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (!root.document) return;

  const node = document.getElementById('compass-app');
  const payload = document.getElementById('compass-tool-data');
  if (!node || !payload) return;
  const tool = JSON.parse(payload.textContent);
  const reportRequestAvailable = !!document.getElementById('compass-report-config');
  const displayedSourceNote = reportRequestAvailable && tool.id === 'smart-compass-local'
    ? (tool.source.note || '').split('. ')[0] + '. The assessment stays on your device. The optional report request below sends only the perspective you choose and the contact details you enter.'
    : tool.source.note || '';
  const key = 'psta-compass:' + tool.id + ':' + tool.version;
  let record = newRecord(tool);
  let saved = false;
  let unkeptChanges = false;
  let message = '';
  let aiPerspectiveId = null;
  const esc = escapeText;
  const label = (text, control, hint = '') => '<label>' + esc(text) + control + '</label>' + (hint ? '<p class="compass-hint">' + esc(hint) + '</p>' : '');
  const textarea = (attrs, value) => '<textarea rows="3" maxlength="20000" ' + attrs + '>' + esc(value) + '</textarea>';
  const input = (attrs, value) => '<input ' + attrs + ' value="' + esc(value) + '">';
  const button = (action, text, extra = '') => '<button type="button" data-action="' + action + '" ' + extra + '>' + esc(text) + '</button>';
  const fileName = () => new Date().toISOString().slice(0, 10) + ' the PSTA ' + ((record.title || tool.title).replace(/[\\/:*?"<>|\u0000-\u001f]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120) || 'Compass record');
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
    unkeptChanges = true;
    if (saved) {
      try { localStorage.setItem(key, JSON.stringify(record)); unkeptChanges = false; status('Saved in this browser at ' + new Date().toLocaleTimeString('en-GB') + '. Download an editable record to keep a separate copy or move to another device.'); }
      catch (_) { saved = false; status('This device could not save the latest changes. Download a JSON copy now.'); }
    } else status('Changes are in this open page. Save on this device or download a copy before leaving.');
    notifyReportClient();
  }
  function notifyReportClient(resetSelection = false) {
    if (tool.id === 'smart-compass-local') document.dispatchEvent(new CustomEvent('psta-compass-record-changed', { detail: { resetSelection } }));
  }
  function download(name, content, mime) {
    const url = URL.createObjectURL(new Blob([content], { type: mime }));
    const a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  window.addEventListener('beforeunload', event => {
    if (!unkeptChanges || !hasRecordContent(record)) return;
    event.preventDefault();
    event.returnValue = '';
  });
  function preparePrint() {
    let report = document.getElementById('compass-print');
    if (!report) { report = document.createElement('article'); report.id = 'compass-print'; report.className = 'compass-print-document'; document.body.appendChild(report); }
    report.innerHTML = reportHtml(record, tool);
    document.body.classList.add('compass-printing');
  }
  window.addEventListener('beforeprint', preparePrint);
  window.addEventListener('afterprint', () => document.body.classList.remove('compass-printing'));
  window.addEventListener('storage', event => {
    if (event.key !== key || !saved) return;
    saved = false;
    unkeptChanges = hasRecordContent(record);
    status('The saved record changed in another tab. Your answers here are still open. Download an editable copy before reloading; saving here will replace the other tab’s copy.');
  });

  function render() {
    const openLenses = new Set([...node.querySelectorAll('.compass-lens[open]')].map(el => el.dataset.section));
    if (aiPerspectiveId === null) aiPerspectiveId = record.participants[0].id;
    node.innerHTML = '<div class="compass-controls">' + button('save', 'Save on this device') + button('json', 'Download editable record') + button('word', 'Download Word notes') + button('print', 'Print / save PDF') + '<label class="compass-file">Open a saved record<input type="file" id="compass-import" accept="application/json,.json"></label>' + button('remove', 'Remove device copy') + button('new', 'Start a new assessment') + '</div><p class="compass-export-help">Device saving keeps one record in this browser. The editable JSON file can be reopened here or on another device; Word notes and PDF are for reading and sharing. Separate perspectives are held in one record, with no live co-editing or automatic merging.</p><p id="compass-status" class="compass-status" role="status" aria-live="polite">' + esc(message || 'Your answers stay in this open page until you choose to save or download them.') + '</p><nav class="compass-navigation" aria-label="Workspace sections"><a href="#compass-context">The situation</a><a href="#compass-questions">Explore questions</a><a href="#compass-actions">Actions</a><a href="#compass-review">Learning and reviews</a></nav>' +
      (tool.reflectionPrompt ? '<section id="compass-ai-reflection"><h2>Use your answers for an AI reflection</h2><p>This workspace prepares a file for you to use in your chosen AI service. ' + (reportRequestAvailable ? 'The reflection download doesn’t run an AI model or email a report. The separate request below lets you ask the PSTA to process one perspective.' : 'It doesn’t run an AI model or operate the separate automated email service.') + '</p><ol><li>Choose one perspective below and download the reflection file. Open it and check the answers and evidence before sharing it. Remove confidential information and identifying details about other people.</li><li>Start a new chat in the AI service you’re authorised to use. If it accepts file uploads, attach the Markdown file. Otherwise open the file, select all its text, and paste it into the chat as plain text.</li><li>Ask the AI system to follow the reflection task in the file and answer in the chat. You don’t need to connect an email account. Check the response against your answers and correct anything it has misread.</li></ol>' + label('Perspective to include', '<select id="compass-ai-perspective"><option value=""' + (!aiPerspectiveId ? ' selected' : '') + '>Choose a perspective</option>' + record.participants.map(p => '<option value="' + esc(p.id) + '"' + (p.id === aiPerspectiveId ? ' selected' : '') + '>' + esc(p.label) + '</option>').join('') + '</select>', 'The file includes this perspective’s current answers and evidence, plus the assessment scope and missing views. Other perspectives, actions, and review history stay out of it. Check you have permission to share what you include.') + button('ai-pack', 'Download the reflection file (Markdown)', aiPerspectiveId ? '' : 'disabled') + '<p>The file begins with the public reflection task, followed by the published descriptions of the eight Commissioning Compass aspects and your selected answers.</p><p><a href="' + esc(tool.reflectionReference.readingUrl) + '">Read the full Commissioning Compass guide</a> · <a href="' + esc(tool.reflectionReference.path) + '">Read the eight-aspect excerpts in the file</a> · <a href="/offers/">The PSTA programmes and support</a></p><p class="compass-hint">Reflection task: ' + esc(tool.reflectionPrompt.version) + '. Reference: ' + esc(tool.reflectionReference.version) + '. AI output can misread incomplete or conflicting answers; use it for reflection and conversation.</p><details><summary>Historical automation prompt</summary><p>' + esc(tool.agentPrompt.note) + '</p><p><a href="' + esc(tool.agentPrompt.path) + '">Read the preserved original automation prompt</a>. It is separate from the reflection file above.</p></details></section>' : '') +
      '<section id="compass-context" class="compass-context"><h2>Assessment details</h2>' +
      label('Assessment title', input('data-record="title" maxlength="200"', record.title)) +
      label('What are you assessing, and why?', textarea('data-record="boundary"', record.boundary)) +
      label('Whose views are missing? What have you left out?', textarea('data-record="missing"', record.missing)) +
      '<h3>People contributing</h3><p>Give each person’s answers a role or short label. Ask what evidence they have and why their answers differ. Check what they’re willing to have recorded.</p>' +
      record.participants.map((p, i) => '<div class="compass-perspective-label">' + label('Perspective ' + (i + 1), input('data-person="' + i + '" maxlength="100"', p.label)) + (record.participants.length > 1 ? button('remove-person', 'Remove perspective', 'data-index="' + i + '"') : '') + '</div>').join('') +
      button('add-person', 'Add another perspective') + '</section>' +
      '<section id="compass-questions"><h2>Assessment questions</h2><p class="compass-guidance">Start with a question that helps you understand the situation. Move between lenses, actions, and learning as the work develops; return when something changes your view. You can leave questions blank. The workspace doesn’t calculate an overall score.</p>' + (tool.instructions?.length || tool.scoreBands ? '<details><summary>Original instructions' + (tool.scoreBands ? ' and scoring bands' : '') + '</summary><p>Scores record participants’ judgements.</p>' + (tool.scoreBands ? '<ul>' + tool.scoreBands.map(s => '<li>' + esc(s) + '</li>').join('') + '</ul>' : '') + (tool.instructions || []).filter(p => !(tool.scoreBands || []).includes(p)).map(p => '<p>' + esc(p) + '</p>').join('') + '</details>' : '') + '<div class="compass-lenses">' +
      tool.sections.map((section, si) => '<details class="compass-lens" id="compass-lens-' + si + '" data-section="' + si + '"' + (openLenses.has(String(si)) ? ' open' : '') + '><summary>' + esc(section.title) + '</summary>' + (section.description ? '<p>' + esc(section.description) + '</p>' : '') + section.questions.map(q => '<div class="compass-question"><h3>' + esc(q.label || 'Question') + '</h3><p>' + esc(q.prompt) + '</p><div class="compass-views">' + record.participants.map((p, pi) => {
        const a = p.answers[q.id] || {};
        const attrs = 'data-question="' + esc(q.id) + '" data-perspective="' + pi + '"';
        return '<fieldset><legend data-perspective-label="' + pi + '">' + esc(p.label) + '</legend>' + (q.range ? label((q.finalScore ? 'Initial score' : 'Self-assessment score') + ' /' + q.range.max + ' (optional)', input(attrs + ' data-answer="score" type="number" min="' + q.range.min + '" max="' + q.range.max + '" step="' + q.range.step + '"', a.score || '')) : '') + (q.scale ? label('Indicative score', '<select ' + attrs + ' data-answer="score"><option value="">Not scored</option>' + q.scale.map(s => '<option value="' + esc(s.value) + '"' + (String(s.value) === a.score ? ' selected' : '') + '>' + esc(s.label) + '</option>').join('') + '</select>') : '') + (q.kind === 'factor' ? '<label class="compass-factor-choice"><input type="checkbox" ' + attrs + ' data-answer="constraining"' + (a.constraining ? ' checked' : '') + '> ' + (tool.factorLimit === 3 ? 'One of the three most constraining' : 'Most constraining') + '</label><label class="compass-factor-choice"><input type="checkbox" ' + attrs + ' data-answer="enabling"' + (a.enabling ? ' checked' : '') + '> ' + (tool.factorLimit === 3 ? 'One of the three most enabling' : 'Most enabling') + '</label>' : '') + label('Your answer', textarea(attrs + ' data-answer="notes"', a.notes || '')) + label('What supports your answer? What remains uncertain?', textarea(attrs + ' data-answer="evidence"', a.evidence || '')) + (q.finalScore ? label('Finalised score after evidence /100 (optional)', input(attrs + ' data-answer="finalScore" type="number" min="0" max="100" step="1"', a.finalScore || '')) : '') + '</fieldset>';
      }).join('') + '</div></div>').join('') + '</details>').join('') + '</div></section>' +
      '<section id="compass-actions"><h2>Actions</h2><p>Record what you’ll do, who can do it, what you expect, and when you’ll check the result.</p>' +
      record.decisions.map((d, i) => '<fieldset class="compass-decision"><legend>Action ' + (i + 1) + '</legend>' + [
        ['title', 'What will you change?', false], ['owner', 'Who can act, and who needs to agree?', false], ['due', 'When will you review it?', false],
        ['expected', 'What do you expect to change, for whom?', true], ['evidence', 'What would support or challenge that expectation?', true], ['nextMove', 'What will you do next?', true],
      ].map(([f, text, area]) => label(text, area ? textarea('data-decision="' + i + '" data-field="' + f + '"', d[f]) : input('data-decision="' + i + '" data-field="' + f + '"' + (f === 'due' ? ' type="date"' : ''), d[f]))).join('') + button('remove-decision', 'Remove action', 'data-index="' + i + '"') + '</fieldset>').join('') + button('add-decision', 'Add an action') + '</section>' +
      '<section id="compass-review"><h2>Review changes</h2><p>Return here whenever an action or a new perspective changes what you understand. Recording a review keeps a dated copy of the answers and actions alongside what you learned.</p>' + (tool.reviewSourceNote ? '<p class="compass-hint">' + esc(tool.reviewSourceNote) + '</p>' : '') +
      (tool.reviewQuestions || []).map((q, i) => label(q, textarea('data-learning="' + i + '"', record.reviewDraft[i] || ''))).join('') + button('review', 'Record this review') +
      '<div class="compass-history">' + record.reviews.map((r, i) => '<details><summary>Review ' + (i + 1) + ' · ' + esc(readableDate(r.date)) + '</summary><p><strong>Assessment scope at this review:</strong> ' + esc(r.snapshot.boundary) + '</p>' + (tool.reviewQuestions || []).map((q, n) => '<h3>' + esc(q) + '</h3><p class="compass-pre">' + esc(r.learning[n] || 'No answer recorded') + '</p>').join('') + '<p>' + r.snapshot.participants.length + ' perspective(s), ' + r.snapshot.decisions.length + ' action(s). The editable record and Word notes include the answers and actions retained at this review.</p></details>').join('') + '</div></section><section id="compass-source"><h2>Source and version</h2><p>' + esc(displayedSourceNote) + '</p><p><a href="' + esc(tool.id === 'compass-v2-beta' ? '/tools/compass-v2-beta/source/' : tool.source.localText || tool.source.url) + '">' + (tool.id === 'compass-v2-beta' ? 'Read the working paper' : 'Read the source') + '</a> · Edition ' + esc(tool.version) + '</p>' + (tool.courseArchive ? '<h3>Reading and resources</h3><p><a href="/tools/commissioning-compass/reading/">Read the teaching material</a> · <a href="' + esc(tool.courseArchive.url) + '">Original course</a></p>' : '') + '</section>';
    node.querySelectorAll('input,textarea').forEach(control => control.setAttribute('autocomplete', 'off'));
    notifyReportClient();
  }

  node.addEventListener('input', event => {
    const t = event.target;
    if (t.hasAttribute('data-record')) record[t.dataset.record] = t.value;
    else if (t.hasAttribute('data-person')) {
      record.participants[Number(t.dataset.person)].label = t.value;
      node.querySelectorAll('[data-perspective-label="' + t.dataset.person + '"]').forEach(legend => { legend.textContent = t.value; });
      const option = node.querySelector('#compass-ai-perspective option[value="' + record.participants[Number(t.dataset.person)].id + '"]');
      if (option) option.textContent = t.value || 'Perspective ' + (Number(t.dataset.person) + 1);
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
    if (event.target.id === 'compass-ai-perspective') { aiPerspectiveId = event.target.value; node.querySelector('[data-action="ai-pack"]').disabled = !aiPerspectiveId; return; }
    if (event.target.id !== 'compass-import') return;
    const file = event.target.files[0];
    if (!file) return;
    try {
      if (file.size > MAX_IMPORT) throw Error('This file is larger than the 20 MB limit for reopening a Compass record. Your current answers are unchanged.');
      const imported = validateRecord(JSON.parse(await file.text()), tool);
      if (!confirm('Replace the record in this open page? Download the current record first if you need to keep it.')) return;
      record = imported; aiPerspectiveId = null; changed(); render(); status('The record has been opened. ' + (saved ? 'It has replaced this browser’s saved record.' : 'Choose Save on this device if you want it restored next time.'));
      notifyReportClient(true);
    } catch (error) { status(error.message || 'The file could not be read.'); }
    finally { event.target.value = ''; }
  });

  node.addEventListener('click', async event => {
    const b = event.target.closest('[data-action]');
    if (!b) return;
    const action = b.dataset.action;
    if (action === 'save') { saved = true; changed(); }
    if (action === 'json') {
      const json = editableJson(record);
      download(fileName() + '.json', json, 'application/json');
      status(new TextEncoder().encode(json).length > MAX_IMPORT
        ? 'The complete JSON download was requested, but this unusually large record exceeds the 20 MB reopening limit. Keep the file and Word notes before starting a new assessment.'
        : 'Editable download requested. Keep the JSON file to reopen the complete record, including its review history.');
    }
    if (action === 'word') {
      try {
        download(fileName() + ' notes.docx', wordDocument(record, tool), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
        status('Word download requested. The notes include your current answers, actions, and review history. Keep an editable JSON copy to continue in this workspace.');
      } catch (_) { status('The Word notes could not be prepared. You can still download an editable record or use Print / save PDF.'); }
    }
    if (action === 'ai-pack' && tool.reflectionPrompt) {
      try {
        const selected = selectedPerspectiveIndex(record, node.querySelector('#compass-ai-perspective').value);
        const snapshot = JSON.parse(JSON.stringify(record));
        const responses = await Promise.all([tool.reflectionPrompt.path, tool.reflectionReference.path].map(path => fetch(path, { credentials: 'omit', cache: 'no-store' })));
        if (responses.some(response => !response.ok)) throw Error('The reflection file could not be prepared because its instructions or reference could not be loaded. Your answers are unchanged. Try again when the page is available.');
        const [prompt, reference] = await Promise.all(responses.map(response => response.text()));
        const pack = reflectionMarkdown(snapshot, tool, prompt, reference, selected);
        download(fileName() + '-smartcompass-reflection.md', pack, 'text/markdown;charset=utf-8');
        status('Download started. Check your browser’s downloads or save prompt, then review the file before sharing it.');
      } catch (error) { status(error.message || 'The reflection file could not be prepared. Your answers are unchanged.'); }
    }
    if (action === 'print') {
      preparePrint();
      try { window.print(); }
      catch (_) { document.body.classList.remove('compass-printing'); status('Printing could not be opened. You can download Word notes instead.'); }
    }
    if (action === 'remove') {
      try { localStorage.removeItem(key); saved = false; unkeptChanges = hasRecordContent(record); status('The browser’s saved copy has been removed. Your open record and downloaded files remain. Save or download any further changes before leaving.'); }
      catch (_) { status('This browser could not remove the device copy. Use its site-data settings to clear it.'); }
    }
    if (action === 'new' && confirm('Start a new assessment? This replaces the record in this browser. Download the editable record first if you need to keep its answers and reviews.')) {
      try { localStorage.removeItem(key); } catch (_) { return status('The existing browser copy could not be removed. Download it before starting a new record.'); }
      record = newRecord(tool); aiPerspectiveId = null; saved = false; unkeptChanges = false; message = 'A new record is open.'; render();
      node.querySelector('[data-record="title"]').focus();
      notifyReportClient(true);
    }
    if (action === 'add-person') {
      if (record.participants.length >= 20) return status('This record already has twenty perspectives.');
      record.participants.push({ id: uid(), label: 'Perspective ' + (record.participants.length + 1), answers: {} }); changed(); render();
      node.querySelector('[data-person="' + (record.participants.length - 1) + '"]').focus();
    }
    if (action === 'remove-person' && confirm('Remove this perspective and its answers from the current record? Earlier review snapshots remain.')) {
      if (record.participants.length < 2) return status('Keep at least one perspective in the record.');
      const removedSelected = record.participants[Number(b.dataset.index)].id === aiPerspectiveId;
      record.participants.splice(Number(b.dataset.index), 1);
      if (removedSelected) aiPerspectiveId = '';
      changed(); render();
      node.querySelector('[data-action="add-person"]').focus();
      if (removedSelected) status('The selected perspective was removed. Choose whose answers to include before preparing a reflection file.');
    }
    if (action === 'add-decision') {
      if (record.decisions.length >= 50) return status('This record already has fifty decisions.');
      record.decisions.push(Object.fromEntries([['id', uid()], ...fields.map(f => [f, ''])])); changed(); render();
      node.querySelector('[data-decision="' + (record.decisions.length - 1) + '"][data-field="title"]').focus();
    }
    if (action === 'remove-decision' && confirm('Remove this decision from the current record? Earlier review snapshots remain.')) { record.decisions.splice(Number(b.dataset.index), 1); changed(); render(); node.querySelector('[data-action="add-decision"]').focus(); }
    if (action === 'review') {
      if (record.reviews.length >= 100) return status('This record already has one hundred reviews. Download it and begin a new record.');
      const learning = (tool.reviewQuestions || []).map((_, i) => node.querySelector('[data-learning="' + i + '"]').value);
      const review = { id: uid(), date: new Date().toISOString(), learning, snapshot: JSON.parse(JSON.stringify({ title: record.title, boundary: record.boundary, missing: record.missing, participants: record.participants, decisions: record.decisions })) };
      if (editableSize({ ...record, reviews: [...record.reviews, review] }) > MAX_IMPORT) return status('This review would make the record too large to reopen here. Your draft and existing reviews are still intact. Download the editable record and Word notes before starting a new assessment.');
      record.reviews.push(review);
      record.reviewDraft = (tool.reviewQuestions || []).map(() => '');
      changed(); render(); status('Review recorded with a snapshot of the current perspectives and decisions.');
      node.querySelector('[data-action="review"]').focus();
    }
  });
  if (tool.id === 'smart-compass-local') root.PSTACompassWorkspace = Object.freeze({ read: () => JSON.parse(JSON.stringify(record)) });
  render();
})(typeof window === 'undefined' ? globalThis : window);
