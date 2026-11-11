/* The PSTA smartCompass: optional, explicit report requests. No automatic submission. */
(function (root) {
  'use strict';
  const EDITION = { id: 'smart-compass-local', version: '2026-07-16' };
  const IDS = ['context-1', 'context-2', ...Array.from({ length: 16 }, (_, i) => 'question-' + (i + 1))];
  const STATES = new Set(['queued', 'generating', 'generation_failed', 'generated', 'preparing_draft', 'draft_failed', 'draft_ready', 'send_intent', 'send_uncertain', 'sent_confirmed', 'archiving', 'archive_failed', 'quarantined', 'complete']);
  const STORE = 'psta-smartcompass-request:' + EDITION.version;
  const object = value => !!value && typeof value === 'object' && !Array.isArray(value);
  const clone = value => JSON.parse(JSON.stringify(value));
  const fail = message => { throw Error(message); };
  function text(value, limit, required) {
    if (typeof value !== 'string' || value.length > limit || /\u0000/.test(value) || (required && !value.trim())) fail('Check the required fields and the length of your answers.');
    return value.trim();
  }
  function settings(value) {
    if (value?.enabled !== true) return null;
    if (value.backendLiveChecksPassed !== true || value.publicIngressVerified !== true || value.processingTriggerVerified !== true) fail('Report requests are unavailable.');
    const url = new URL(value.endpoint);
    if (url.protocol !== 'https:' || url.username || url.password || url.pathname !== '/' || url.search || url.hash || url.origin !== value.endpoint.replace(/\/$/, '')) fail('Report requests are unavailable.');
    if (typeof value.consentVersion !== 'string' || !value.consentVersion.trim() || value.consentVersion.length > 100) fail('Report requests are unavailable.');
    if (value.privacyPath !== '/privacy/#smartcompass-report-requests' || value.contact !== 'info@publicservicetransformation.org') fail('Report requests are unavailable.');
    return Object.freeze({ ...value, endpoint: url.origin });
  }
  function perspectiveIndex(record, id) {
    if (typeof id !== 'string' || !id || !Array.isArray(record?.participants)) fail('Choose one perspective.');
    const index = record.participants.findIndex(person => person.id === id);
    if (index < 0) fail('Choose one perspective.');
    return index;
  }
  function buildSubmission(record, index, respondent, consent, idempotencyKey, config) {
    if (!object(record) || record.schema !== 'psta-compass-session' || record.schemaVersion !== 1 || record.toolId !== EDITION.id || record.toolVersion !== EDITION.version || !Array.isArray(record.participants)) fail('Open the supported smartCompass edition.');
    if (!Number.isInteger(index) || !object(record.participants[index]?.answers)) fail('Choose one perspective.');
    if (!/^[A-Za-z0-9_-]{20,100}$/.test(idempotencyKey)) fail('A secure request key could not be created.');
    const person = record.participants[index];
    const answers = Object.fromEntries(IDS.map(id => [id, text(person.answers[id]?.notes ?? '', 8000)]));
    const evidence = Object.fromEntries(IDS.map(id => [id, text(person.answers[id]?.evidence ?? '', 4000)]));
    if (!Object.values(answers).some(Boolean)) fail('Record an answer before requesting a report.');
    const name = text(respondent.name, 100, true), email = text(respondent.email, 254, true).toLowerCase();
    if (/[\r\n]/.test(name) || !/^[^\s<>@,;]+@[^\s<>@,;]+\.[^\s<>@,;]+$/.test(email) || /[\r\n]/.test(email)) fail('Check your name and email address.');
    if (consent.processWithAI !== true || consent.emailResult !== true || typeof consent.contactAboutSupport !== 'boolean') fail('Choose both required permissions to request a report.');
    const result = { schema: 'psta-smartcompass-submission', schemaVersion: 1, idempotencyKey, edition: { ...EDITION }, respondent: { name, email, roleAndOrganisation: text(respondent.roleAndOrganisation ?? '', 300) }, answers, evidence, perspective: text(person.label ?? '', 100), consent: { version: config.consentVersion, processWithAI: true, emailResult: true, contactAboutSupport: consent.contactAboutSupport } };
    if (new TextEncoder().encode(JSON.stringify(result)).length > 131072) fail('The request is too large. Shorten your answers or evidence notes.');
    return result;
  }
  function validateAccepted(value) {
    if (!object(value) || !/^[A-Za-z0-9-]{1,100}$/.test(value.id) || !STATES.has(value.state) || !/^[a-f0-9]{64}$/.test(value.statusToken) || value.statusPath !== '/v1/submissions/' + value.id) fail('The request result could not be confirmed.');
    return { id: value.id, state: value.state, statusToken: value.statusToken, statusPath: value.statusPath };
  }
  function statusText(value) {
    if (value.state === 'send_uncertain') return 'Your report may already have been sent. Check this request again after the next processing run. Don\'t create another request. If the status is unchanged, contact the PSTA with the reference below.';
    if (value.reviewRequired || ['quarantined', 'send_uncertain'].includes(value.state)) return 'The request needs checking by the PSTA and may already have been sent. Don\'t create another request. Contact us with the reference below.';
    if (value.archiveComplete && value.emailConfirmed) return 'The service has confirmed the email was sent and its record was archived. Check your inbox and junk folder. This does not confirm receipt or reading.';
    if (value.emailConfirmed) return 'The service has confirmed the email was sent. Its archive is still pending. Don\'t request another copy; check your inbox and junk folder.';
    if (value.state === 'send_intent') return 'Sending is being checked. Don\'t create another request; the email may already have been sent.';
    if (['generation_failed', 'draft_failed', 'archive_failed'].includes(value.state)) return 'Processing is delayed. Check this request again or contact the PSTA with its reference. Don\'t create another request.';
    return 'The request is recorded and processing is pending. Check its status here later. No email has been confirmed yet.';
  }
  function createClient({ config: value, storage, fetcher = root.fetch.bind(root), cryptography = root.crypto, clock = () => new Date().toISOString() }) {
    const config = settings(value);
    if (!config) return null;
    let pending = null, busy = false, invalidStored = false;
    try {
      const raw = storage.getItem(STORE);
      if (raw) {
        const stored = JSON.parse(raw), body = JSON.parse(stored.body);
        if (stored.version !== 1 || stored.endpoint !== config.endpoint || body.schema !== 'psta-smartcompass-submission' || !/^[A-Za-z0-9_-]{20,100}$/.test(body.idempotencyKey) || body.edition?.id !== EDITION.id || body.edition?.version !== EDITION.version || stored.body.length > 131072 || !['waiting', 'unknown', 'accepted'].includes(stored.phase)) fail('stored');
        if (stored.receipt) validateAccepted(stored.receipt);
        else if (body.consent?.version !== config.consentVersion) fail('stored');
        pending = stored;
      }
    } catch (_) { invalidStored = true; }
    function save(next) {
      const serialized = JSON.stringify(next);
      storage.setItem(STORE, serialized);
      if (storage.getItem(STORE) !== serialized) fail('The browser could not keep the request safely. No request has been sent.');
      pending = next;
    }
    function key() {
      if (!cryptography?.getRandomValues) fail('This browser cannot create a secure request key.');
      return [...cryptography.getRandomValues(new Uint8Array(32))].map(v => v.toString(16).padStart(2, '0')).join('');
    }
    async function json(path, init) {
      const controller = new AbortController(); let reader, timer;
      const cancel = () => { try { void reader?.cancel().catch(() => {}); } catch (_) {} };
      const deadline = new Promise((_resolve, reject) => {
        timer = setTimeout(() => { reject(Error('The service response could not be confirmed.')); controller.abort(); cancel(); }, 20000);
      });
      try {
        const response = await Promise.race([fetcher(config.endpoint + path, { ...init, signal: controller.signal, credentials: 'omit', redirect: 'error', cache: 'no-store', referrerPolicy: 'no-referrer' }), deadline]);
        if (!/^application\/json(?:\s*;|$)/i.test(response.headers.get('Content-Type') || '')) fail('Unexpected service response.');
        const length = response.headers.get('Content-Length');
        if (length && (!/^\d+$/.test(length) || Number(length) > 16384)) fail('Unexpected service response.');
        reader = response.body?.getReader(); if (!reader) fail('Unexpected service response.');
        const chunks = []; let total = 0;
        for (;;) {
          const { done, value } = await Promise.race([reader.read(), deadline]);
          if (done) break;
          total += value.byteLength; if (total > 16384) fail('Unexpected service response.'); chunks.push(value);
        }
        const bytes = new Uint8Array(total); let offset = 0;
        for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
        let result;
        try { result = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)); }
        catch (_) { fail('Unexpected service response.'); }
        if (!response.ok) {
          const error = Error('The service could not confirm the request.');
          error.code = typeof result.error === 'string' ? result.error : 'service_unavailable';
          throw error;
        }
        return result;
      } finally { clearTimeout(timer); controller.abort(); cancel(); }
    }
    async function post() {
      if (busy || invalidStored || !pending || pending.receipt) fail('Use the existing request status.');
      busy = true;
      try {
        const receipt = validateAccepted(await json('/v1/submissions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: pending.body }));
        const next = { ...pending, phase: 'accepted', receipt };
        try { save(next); } catch (_) { pending = next; }
        return clone(pending);
      } catch (error) {
        const next = { ...pending, phase: 'unknown' };
        try { save(next); } catch (_) { pending = next; }
        const conflict = error.code === 'idempotency_conflict';
        throw Error(conflict ? 'The existing request needs checking. Don\'t create another request; contact the PSTA.' : 'Acceptance could not be confirmed. Keep this tab open. Retry the same stored request below; don\'t make a new request.');
      } finally { busy = false; }
    }
    return {
      prepare(record, index, respondent, consent) {
        if (pending || invalidStored) fail('A request is already retained in this tab.');
        return buildSubmission(record, index, respondent, consent, key(), config);
      },
      async submit(payload) {
        if (pending || invalidStored || busy) fail('Use the existing request.');
        save({ version: 1, endpoint: config.endpoint, body: JSON.stringify(clone(payload)), phase: 'waiting', preparedAt: clock() });
        return post();
      },
      retry: post,
      async check() {
        if (busy || invalidStored || !pending?.receipt) fail('There is no confirmed request reference to check.');
        busy = true;
        try {
          const result = await json(pending.receipt.statusPath, { method: 'GET', headers: { Authorization: 'Bearer ' + pending.receipt.statusToken } });
          if (result.id !== pending.receipt.id || !STATES.has(result.state) || ['emailConfirmed', 'archiveComplete', 'reviewRequired'].some(k => typeof result[k] !== 'boolean')) fail('The service status could not be confirmed.');
          const status = { id:result.id, state:result.state, emailConfirmed:result.emailConfirmed, archiveComplete:result.archiveComplete, reviewRequired:result.reviewRequired };
          const next = { ...pending, receipt: { ...pending.receipt, state: status.state }, status };
          try { save(next); } catch (_) { pending = next; }
          return clone(status);
        } finally { busy = false; }
      },
      state: () => ({ pending: pending ? clone(pending) : null, invalidStored, busy }),
      clearComplete() {
        if (!pending?.status?.archiveComplete || !pending?.status?.emailConfirmed) fail('Keep the existing request until its send and archive are confirmed.');
        storage.removeItem(STORE); pending = null;
      },
    };
  }
  const api = { EDITION, IDS, STORE, settings, perspectiveIndex, buildSubmission, statusText, createClient };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (!root.document) return;
  const mount = root.document.getElementById('compass-report-app'), configNode = root.document.getElementById('compass-report-config');
  if (!mount || !configNode) return;
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
  let client, config, preview = null, formDraft = null;
  try { config = settings(JSON.parse(configNode.textContent)); if (!config) return; client = createClient({ config, storage: root.sessionStorage }); }
  catch (_) { mount.textContent = 'Report requests are unavailable. Your workspace answers are unchanged.'; return; }
  const workspace = () => root.PSTACompassWorkspace.read();
  function notice(value) { mount.querySelector('[data-report-status]').textContent = value; }
  function render() {
    const previousForm = mount.querySelector('[data-report-form]');
    if (previousForm) formDraft = { perspective: previousForm.elements.perspective.value, name: previousForm.elements.name.value, email: previousForm.elements.email.value, roleAndOrganisation: previousForm.elements.roleAndOrganisation.value, processWithAI: previousForm.elements.processWithAI.checked, emailResult: previousForm.elements.emailResult.checked, contactAboutSupport: previousForm.elements.contactAboutSupport.checked };
    const state = client.state();
    if (state.invalidStored) { mount.innerHTML = '<h2>Request needs checking</h2><p>This tab\'s request record could not be read, or the service address changed. A previous request may have been accepted. Don\'t submit it again. Contact <a href="mailto:' + esc(config.contact) + '">' + esc(config.contact) + '</a>.</p>'; return; }
    if (state.pending) {
      const p = state.pending, body = JSON.parse(p.body);
      mount.innerHTML = '<h2>Your report request</h2><p class="compass-hint">Report requests are processed at 10am, 1pm, 4pm, 7pm, and 11pm UK time. Some reports may need a later run.</p><p>The request uses a saved snapshot for ' + esc(body.respondent.email) + '. Later edits in the workspace don\'t change it.</p><p data-report-status role="status" aria-live="polite">' + esc(p.status ? statusText(p.status) : p.receipt ? statusText(p.receipt) : 'Acceptance is not confirmed. Retry this same stored request; don\'t create a new one.') + '</p>' + (p.receipt ? '<p>Request reference: <code>' + esc(p.receipt.id) + '</code></p><button type="button" data-report-action="check">Check request status</button>' : '<button type="button" data-report-action="retry">Retry the same request</button>') + (p.status?.archiveComplete && p.status?.emailConfirmed ? '<button type="button" data-report-action="clear">Remove this tab\'s request copy</button>' : '') + '<p>For help, contact <a href="mailto:' + esc(config.contact) + '">' + esc(config.contact) + '</a> with the request reference if one is shown. Don\'t email the status token or confidential case details.</p>';
      return;
    }
    const record = workspace();
    mount.innerHTML = '<h2>Request a smartCompass reflection by email</h2><p class="compass-hint">Report requests are processed at 10am, 1pm, 4pm, 7pm, and 11pm UK time. Some reports may need a later run.</p><p>Choose one perspective. The service receives its two context answers, sixteen reflections, and evidence notes, plus the details you enter below. It doesn\'t receive your other perspectives, actions, or review history.</p><p>OpenAI uses the chosen answers, evidence, perspective label, name, and role/organisation to generate an automated reflection. The PSTA stores your submitted answers and the emailed report in Microsoft 365. Its service database also keeps the request and result to track processing. Authorised staff can review these records. The report is emailed only to the address you enter. Remove confidential client information and identifying details about other people before submitting.</p><form data-report-form><label>Perspective<select name="perspective" required><option value="">Choose a perspective</option>' + record.participants.map((p, i) => '<option value="' + esc(p.id) + '">' + esc(p.label || 'Perspective ' + (i + 1)) + '</option>').join('') + '</select></label><label>Your name<input name="name" maxlength="100" required autocomplete="name"></label><label>Email for the report<input name="email" type="email" maxlength="254" required autocomplete="email"></label><label>Role and organisation (optional)<input name="roleAndOrganisation" maxlength="300" autocomplete="organization"></label><p><a href="' + esc(config.privacyPath) + '">Read how report requests are processed</a>. This tab keeps the request snapshot and a private status token in browser session storage so a retry can recover the same request. A browser may restore a tab with its session data. After processing is confirmed, remove this tab’s request copy or clear this site’s browser data. Server records and emails are separate.</p><label><input name="processWithAI" type="checkbox" required> I ask the PSTA to use OpenAI to prepare an automated reflection from this selected perspective.</label><label><input name="emailResult" type="checkbox" required> I ask the PSTA to email the report to the address above.</label><label><input name="contactAboutSupport" type="checkbox"> The PSTA may contact me separately about support with this work. (Optional.)</label><button type="submit">Check what will be sent</button></form><p data-report-status role="status" aria-live="polite"></p><div data-report-preview></div>';
    mount.querySelector('[data-report-form]').addEventListener('submit', event => {
      event.preventDefault();
      const form = event.currentTarget;
      try {
        const current = workspace();
        preview = client.prepare(current, perspectiveIndex(current, form.elements.perspective.value), { name: form.elements.name.value, email: form.elements.email.value, roleAndOrganisation: form.elements.roleAndOrganisation.value }, { processWithAI: form.elements.processWithAI.checked, emailResult: form.elements.emailResult.checked, contactAboutSupport: form.elements.contactAboutSupport.checked });
        const questions = JSON.parse(root.document.getElementById('compass-tool-data').textContent).sections.flatMap(s => s.questions);
        mount.querySelector('[data-report-preview]').innerHTML = '<h3>Check the request</h3><p>Name: ' + esc(preview.respondent.name) + '. Email: ' + esc(preview.respondent.email) + '. Role and organisation: ' + esc(preview.respondent.roleAndOrganisation || '(Blank)') + '.</p><p>Perspective: ' + esc(preview.perspective) + '. Blank answers stay blank.</p><p>Separate support contact: ' + (preview.consent.contactAboutSupport ? 'yes' : 'no') + '.</p><details open><summary>Answers and evidence to send</summary>' + questions.map(q => '<h4>' + esc(q.prompt) + '</h4><p class="compass-pre">' + esc(preview.answers[q.id] || '(Blank)') + '</p><p class="compass-pre">Evidence: ' + esc(preview.evidence[q.id] || '(Blank)') + '</p>').join('') + '</details><p><button type="button" data-report-action="send">Request this report by email</button> <button type="button" data-report-action="cancel">Cancel this preview</button></p>';
        notice('Check this snapshot, then choose whether to send it. Nothing has been submitted.');
      } catch (error) { notice(error.message); }
    });
    mount.querySelector('[data-report-form]').addEventListener('input', () => { preview = null; mount.querySelector('[data-report-preview]').replaceChildren(); });
    if (formDraft) {
      const form = mount.querySelector('[data-report-form]');
      for (const name of ['name', 'email', 'roleAndOrganisation']) form.elements[name].value = formDraft[name];
      if ([...form.elements.perspective.options].some(option => option.value === formDraft.perspective)) form.elements.perspective.value = formDraft.perspective;
      for (const name of ['processWithAI', 'emailResult', 'contactAboutSupport']) form.elements[name].checked = formDraft[name];
    }
  }
  root.document.addEventListener('psta-compass-record-changed', event => {
    if (client.state().pending) return;
    preview = null;
    mount.querySelector('[data-report-preview]')?.replaceChildren();
    const select = mount.querySelector('[name="perspective"]');
    if (!select) return;
    const previous = event.detail?.resetSelection ? '' : select.value;
    select.innerHTML = '<option value="">Choose a perspective</option>' + workspace().participants.map((p, i) => '<option value="' + esc(p.id) + '">' + esc(p.label || 'Perspective ' + (i + 1)) + '</option>').join('');
    select.value = [...select.options].some(option => option.value === previous) ? previous : '';
  });
  mount.addEventListener('click', async event => {
    const button = event.target.closest('[data-report-action]'); if (!button) return;
    const action = button.dataset.reportAction;
    if (action === 'cancel') { preview = null; mount.querySelector('[data-report-preview]').replaceChildren(); return; }
    if (action === 'clear') { if (root.confirm('Remove this tab\'s request snapshot and status token? This does not delete server records or emails.')) { client.clearComplete(); render(); } return; }
    if (action === 'send' && !preview) return;
    button.disabled = true;
    try {
      if (action === 'send') await client.submit(preview);
      if (action === 'retry') await client.retry();
      if (action === 'check') await client.check();
      render();
    } catch (error) { render(); notice(action === 'check' ? 'The status could not be checked. Keep the existing request and try checking it later; don\'t submit another report.' : error.message); }
  });
  render();
})(typeof window === 'undefined' ? globalThis : window);
