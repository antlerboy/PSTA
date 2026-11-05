/* End-to-end local-save, review, import, export, and private-page checks. */
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '../deploy');
const qa = path.resolve(__dirname, '../../psta-qa');
const contentTypes = { '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.txt': 'text/plain', '.html': 'text/html' };
const server = http.createServer(async (req, res) => {
  try {
    let name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (name.endsWith('/')) name += 'index.html';
    const file = path.resolve(root, '.' + name);
    if (!file.startsWith(root + path.sep)) throw Error('Invalid path');
    res.setHeader('Content-Type', (contentTypes[path.extname(file)] || 'application/octet-stream') + '; charset=utf-8');
    res.end(await fs.readFile(file));
  } catch (_) { res.statusCode = 404; res.end('Not found'); }
});

(async () => {
  console.log('Preparing local browser checks');
  await fs.mkdir(qa, { recursive: true });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = 'http://127.0.0.1:' + server.address().port;
  console.log('Local test origin: ' + origin);
  const browser = await chromium.launch({ headless: true, ...(process.env.BROWSER_EXECUTABLE ? { executablePath: process.env.BROWSER_EXECUTABLE } : {}) });
  const context = await browser.newContext({ acceptDownloads: true });
  console.log('Browser launched');
  const page = await context.newPage();
  const errors = [], requests = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', req => requests.push({ url: req.url(), frame: req.frame().url() }));
  page.on('dialog', dialog => dialog.accept());
  async function download(action, name) {
    const event = page.waitForEvent('download');
    await page.locator('[data-action="' + action + '"]').click();
    const d = await event; const destination = path.join(qa, name); await d.saveAs(destination);
    return destination;
  }
  try {
    await page.goto(origin + '/tools/commissioning-compass/workspace/');
    console.log('Original Compass loaded');
    await page.locator('[data-record="title"]').fill('Browser portability check');
    await page.locator('[data-record="boundary"]').fill('A fictional practice exercise');
    await page.locator('details[data-section="0"]>summary').click();
    const notes = page.locator('[data-question="a1-q1"][data-answer="notes"]');
    await notes.fill('First interpretation');
    await page.locator('[data-question="a1-q1"][data-answer="score"]').fill('0');
    await page.locator('[data-question="a1-q1"][data-answer="finalScore"]').fill('67');
    for (let i = 1; i <= 4; i++) await page.locator('[data-question="a1-f' + i + '"][data-answer="constraining"]').click();
    assert.equal(await page.locator('input[data-answer="constraining"]:checked').count(), 3);
    await page.locator('[data-learning="0"]').fill('Review in progress');
    await page.locator('[data-action="save"]').click();
    await page.reload();
    assert.equal(await page.locator('[data-record="title"]').inputValue(), 'Browser portability check');
    assert.equal(await page.locator('[data-learning="0"]').inputValue(), 'Review in progress');
    await page.locator('details[data-section="0"]>summary').click();
    assert.equal(await notes.inputValue(), 'First interpretation');
    assert.equal(await page.locator('[data-question="a1-q1"][data-answer="score"]').inputValue(), '0');
    assert.equal(await page.locator('[data-question="a1-q1"][data-answer="finalScore"]').inputValue(), '67');
    await page.locator('[data-action="add-person"]').click();
    await page.locator('[data-person="1"]').fill('Different view');
    await page.locator('details[data-section="0"]>summary').click();
    await page.locator('[data-question="a1-q1"][data-perspective="1"][data-answer="notes"]').fill('A different account');
    await page.locator('[data-action="add-decision"]').click();
    await page.locator('[data-decision="0"][data-field="title"]').fill('Test one changed condition');
    await page.locator('[data-decision="0"][data-field="due"]').fill('2026-12-05');
    await page.locator('[data-action="review"]').click();
    await page.locator('details[data-section="0"]>summary').click();
    await page.locator('[data-question="a1-q1"][data-perspective="0"][data-answer="notes"]').fill('Changed after review');
    const exported = await download('json', 'original-record.json');
    const record = JSON.parse(await fs.readFile(exported, 'utf8'));
    assert.equal(record.participants.length, 2);
    assert.equal(record.reviews[0].snapshot.participants[0].answers['a1-q1'].notes, 'First interpretation');
    assert.equal(record.participants[0].answers['a1-q1'].notes, 'Changed after review');
    assert.equal(record.decisions[0].due, '2026-12-05');
    await page.locator('[data-action="new"]').click();
    await page.locator('#compass-import').setInputFiles(exported);
    await page.waitForFunction(() => document.querySelector('[data-record="title"]').value === 'Browser portability check');
    const wrong = { ...record, toolId: 'wrong-tool' };
    await page.locator('#compass-import').setInputFiles({ name: 'wrong.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(wrong)) });
    await page.waitForFunction(() => document.querySelector('#compass-status').textContent.includes('different Compass edition'));
    assert.equal(await page.locator('[data-record="title"]').inputValue(), 'Browser portability check');
    await page.evaluate(() => { window.print = () => {}; });
    await page.locator('[data-action="print"]').click();
    assert.ok((await page.locator('#compass-print').textContent()).includes('First interpretation'));
    await page.locator('[data-action="save"]').click();
    await page.locator('[data-action="remove"]').click();
    await page.reload();
    assert.equal(await page.locator('[data-record="title"]').inputValue(), '');

    await page.goto(origin + '/tools/smart-compass/workspace/');
    await page.locator('[data-record="title"]').fill('AI handoff test');
    const pack = await download('ai-pack', 'ai-handoff.txt');
    const originalPrompt = await fs.readFile(path.resolve(__dirname, '../content/compass/sources/smartcompass-agent-prompt-v3.txt'), 'utf8');
    const handoff = await fs.readFile(pack, 'utf8');
    assert.ok(handoff.includes(originalPrompt));
    assert.ok(handoff.includes('No AI response has been generated'));
    assert.ok(handoff.includes('AI handoff test'));

    await page.goto(origin + '/tools/compass-v2-beta/workspace/');
    assert.equal(await page.locator('.compass-lens').count(), 8);
    assert.equal(await page.locator('.compass-question').count(), 40);
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: path.join(qa, 'workspace-mobile.png') });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    assert.equal((await page.request.get(origin + '/assets/compass/sources/scoa-self-assessment-questions.txt')).status(), 200);
    assert.equal((await page.request.get(origin + '/tools/adult-social-care-options-appraisal/workspace/')).status(), 404);
    await page.goto(origin + '/tools/compass/');
    await page.screenshot({ path: path.join(qa, 'compass-hub-mobile.png'), fullPage: true });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await page.goto(origin + '/enquire/');
    await page.locator('[data-prompt="Your role and organisation"]').fill('Fictional service team');
    assert.ok((await page.locator('#intake-preview').textContent()).includes('Fictional service team'));
    await page.goto(origin + '/community/bring-a-case/');
    assert.equal(await page.locator('form[data-practice-intake]').count(), 1);
    assert.deepEqual(errors, []);
    const foreign = requests.filter(r => /\/workspace\/|\/enquire\/|\/bring-a-case\//.test(r.frame) && !r.url.startsWith(origin));
    assert.deepEqual(foreign, [], 'Workspace/enquiry pages must make no third-party requests');
    console.log('Browser checks passed: local persistence/removal, zero scores, factor limits, two perspectives, immutable review snapshot, JSON round-trip, wrong-edition protection, source-exact AI handoff, print, mobile width, and local enquiry preparation.');
    console.log('QA artefacts: ' + qa);
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
