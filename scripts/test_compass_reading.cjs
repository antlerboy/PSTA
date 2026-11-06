/* Source coverage checks. These do not claim comparison with gated lesson bodies. */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const read = name => JSON.parse(fs.readFileSync(path.join(root, 'content/compass/reading', name), 'utf8'));
const course = read('reading-course.json');
const deck = read('teaching-deck-2025-06.json');
const preReading = read('approaches-pre-reading-2023-06.json');
const catalogue = JSON.parse(fs.readFileSync(path.join(root, 'content/compass/archive/teachable-course-inventory-2026-11-05.json'), 'utf8'));

test('38 source topics and 11 remaining lessons reconcile to the actual 49-lesson catalogue', () => {
  const all = catalogue.sections.flatMap(section => section.lessons.map(lesson => lesson.url));
  const mapped = course.chapters.map(chapter => chapter.catalogueLessonUrl);
  const remaining = course.remainingCatalogueLessons.map(chapter => chapter.catalogueLessonUrl);
  assert.equal(mapped.length, 38);
  assert.equal(remaining.length, 11);
  assert.deepEqual([...mapped, ...remaining].sort(), all.sort());
  assert.equal(new Set([...mapped, ...remaining]).size, 49);
  assert.equal(course.teachableBodiesCompared, 0);
  assert.equal(course.remainingCatalogueLessons.filter(lesson => /Case studies and Equality/.test(lesson.title)).length, 8);
});

test('every local chapter has substantive source material and an identified version', () => {
  const slides = new Map(deck.slides.map(slide => [slide.number, slide]));
  assert.equal(new Set(course.chapters.map(chapter => chapter.route)).size, 38);
  for (const chapter of course.chapters) {
    assert.ok(chapter.slides.length);
    assert.ok(chapter.slides.every(number => slides.has(number)));
    const words = chapter.slides.flatMap(number => slides.get(number).paragraphs).join(' ');
    assert.ok(words.length > 80, chapter.title);
    if (chapter.preReadingApproach) assert.ok(preReading.approaches.find(approach => approach.number === chapter.preReadingApproach).paragraphs.length > 10);
  }
  assert.equal(deck.lastModified, '2025-06-25');
  assert.equal(preReading.date, '2023-06-05');
});

test('approved source extracts and the credited diagram retain their recorded hashes', () => {
  for (const source of course.sourceFiles) {
    const bytes = fs.readFileSync(path.join(root, 'content/compass/reading', source.file));
    assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), source.sha256);
  }
  const figure = deck.figures[0];
  const bytes = fs.readFileSync(path.join(root, figure.file));
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), figure.sha256);
  assert.ok(figure.credit.includes('R. Selwyn'));
});

test('source publication excludes template instructions, speaker notes, private URLs, and draft appendices', () => {
  assert.ok(deck.slides.every(slide => (slide.number >= 4 && slide.number <= 87) || slide.number === 99));
  const text = JSON.stringify([deck, preReading]);
  assert.doesNotMatch(text, /sharepoint\.com|guestaccesstoken|graph\.microsoft\.com|C:\\\\Users|BEGIN PRIVATE|BENJAMIN\\n25/i);
  assert.equal(preReading.approaches.length, 8);
  for (const approach of preReading.approaches) {
    for (const paragraph of approach.paragraphs) {
      assert.equal(paragraph.runs.map(run => run.text).join(''), paragraph.text);
      for (const run of paragraph.runs) if (run.url) assert.match(run.url, /^(https:\/\/|mailto:)/);
    }
  }
});

test('the original internal article reference is restored from a published record, with its date retained', () => {
  const article = read('related-article-2017-10.json');
  assert.equal(article.sourceStatus, 'publish');
  assert.equal(article.originalDate, '2017-10-15');
  assert.equal(article.paragraphs.length, 15);
  assert.equal(article.originalUrl, 'https://www.publicservicetransformation.org/2017/10/asset-based-areas-commission/');
  assert.ok(preReading.approaches.some(approach => approach.paragraphs.some(paragraph => paragraph.runs.some(run => run.url === article.originalUrl))));
});
