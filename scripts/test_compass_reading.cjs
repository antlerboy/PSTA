/* Source, course teaching, and original asset checks. */
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
const caseSource = read('aspects-cases-equity-2023-06.json');
const origins = read('toolkit-origins-2023-06.json');
const catalogue = JSON.parse(fs.readFileSync(path.join(root, 'content/compass/archive/teachable-course-inventory-2026-11-05.json'), 'utf8'));

test('reading chapters identify genuine catalogue sources without publishing task tracking fields', () => {
  const all = catalogue.sections.flatMap(section => section.lessons.map(lesson => lesson.url));
  const mapped = course.chapters.map(chapter => chapter.catalogueLessonUrl);
  assert.equal(mapped.length, 49);
  assert.equal(new Set(mapped).size, 49);
  assert.deepEqual(mapped.slice().sort(), all.slice().sort());
  assert.equal(all.length, 49);
  for (const field of ['remainingCatalogueLessons', 'teachableBodiesCompared', 'expectedTeachableLessons', 'sourceTopicsAvailable', 'mediaAndDownloadCounts', 'status']) assert.equal(course[field], undefined);
});

test('every local chapter has substantive source material and an identified version', () => {
  const slides = new Map(deck.slides.map(slide => [slide.number, slide]));
  assert.equal(new Set(course.chapters.map(chapter => chapter.route)).size, 49);
  for (const chapter of course.chapters) {
    if (chapter.caseStudyAspect) {
      const lesson = caseSource.lessons.find(row => row.aspect === chapter.caseStudyAspect);
      assert.ok(lesson && lesson.sections.length === 3);
      assert.ok(lesson.sections.every(section => section.paragraphs.length));
    } else if (chapter.currentLesson) {
      assert.ok(['using-and-improving', 'contact-and-updates'].includes(chapter.currentLesson));
    } else if (chapter.resourceLesson) {
      assert.equal(chapter.resourceLesson, 'original-toolkit');
      assert.ok(origins.sections.flatMap(section => section.paragraphs).length > 10);
    } else {
      assert.ok(chapter.slides.length);
      assert.ok(chapter.slides.every(number => slides.has(number)));
      const words = chapter.slides.flatMap(number => slides.get(number).paragraphs).join(' ');
      assert.ok(words.length > 80, chapter.title);
    }
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
  const text = JSON.stringify([deck, preReading, caseSource, origins]);
  assert.doesNotMatch(text, /sharepoint\.com|guestaccesstoken|graph\.microsoft\.com|C:\\\\Users|BEGIN PRIVATE|BENJAMIN\\n25/i);
  assert.equal(preReading.approaches.length, 8);
  for (const approach of preReading.approaches) {
    for (const paragraph of approach.paragraphs) {
      assert.equal(paragraph.runs.map(run => run.text).join(''), paragraph.text);
      for (const run of paragraph.runs) if (run.url) assert.match(run.url, /^(https:\/\/|mailto:)/);
    }
  }
});

test('the original article reference retains its publication date and source text', () => {
  const article = read('related-article-2017-10.json');
  assert.equal(article.originalDate, '2017-10-15');
  assert.equal(article.paragraphs.length, 15);
  assert.equal(article.originalUrl, 'https://www.publicservicetransformation.org/2017/10/asset-based-areas-commission/');
  assert.ok(preReading.approaches.some(approach => approach.paragraphs.some(paragraph => paragraph.runs.some(run => run.url === article.originalUrl))));
});

test('public source metadata contains source facts and no internal migration progress', () => {
  const text = JSON.stringify([course, deck, preReading, caseSource, origins, read('related-article-2017-10.json')]);
  assert.doesNotMatch(text, /Teachable material still to compare|migration status|course status|haven’t been compared|have not been compared|not yet been exported|course comparison is still|media recovery pending/i);
});

test('all eight aspects retain the higher/lower cases and equality text from the original source', () => {
  assert.equal(caseSource.lessons.length, 8);
  assert.equal(new Set(caseSource.lessons.map(lesson => lesson.aspect)).size, 8);
  const paragraphs = caseSource.lessons.flatMap(lesson => lesson.sections.flatMap(section => section.paragraphs));
  assert.equal(paragraphs.length, 47);
  assert.ok(paragraphs.every(paragraph => paragraph.text.length && Number.isInteger(paragraph.sourceParagraph)));
  assert.ok(caseSource.lessons.every(lesson => lesson.sections[2].heading.includes('Equality and equity')));
  assert.equal(caseSource.sourceDate, 'June 2023');
  assert.equal(caseSource.sourceFileSha256, '3f578f6b96c4784e70dcdd200173d463ea0e69d1dc2bc9b9b525107b4ce5dd76');
});

const teaching = read('course-teaching-2026-11.json');
test('the course includes all original teaching chapters and current operational guidance', () => {
  assert.equal(teaching.lessons.length, 47);
  assert.equal(new Set(teaching.lessons.map(lesson => lesson.id)).size, 47);
  assert.equal(course.chapters.filter(chapter => chapter.courseLesson).length, 47);
  assert.equal(course.chapters.filter(chapter => chapter.currentLesson).length, 2);
  for (const chapter of course.chapters) if (chapter.courseLesson) {
    const lesson = teaching.lessons.find(row => row.id === chapter.courseLesson);
    assert.ok(lesson && (lesson.text.trim() || lesson.assetPaths.length));
    assert.equal(chapter.catalogueLessonUrl.split('/').pop(), lesson.id);
  }
  for (const id of ['61938002', '61967619']) assert.match(teaching.lessons.find(lesson => lesson.id === id).html, /<table>/);
});

test('the twenty-nine original files and blank workbook preserve their recorded bytes and names', () => {
  assert.equal(teaching.assets.length, 30);
  const types = teaching.assets.reduce((counts, asset) => { counts[asset.type] = (counts[asset.type] || 0) + 1; return counts; }, {});
  assert.deepEqual(types, {docx: 9, jpg: 16, png: 1, pdf: 3, xlsx: 1});
  for (const asset of teaching.assets) {
    assert.equal(path.posix.basename(asset.path), asset.name);
    const bytes = fs.readFileSync(path.join(root, asset.path));
    assert.equal(bytes.length, asset.bytes);
    assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), asset.sha256);
  }
});

test('published course learning contains no platform state, signed URLs, active embeds, or old automated-email promises', () => {
  const text = JSON.stringify(teaching);
  assert.doesNotMatch(text, /sharepoint\.com|Signature=|Expires=|Key-Pair-Id|data-lecture|data-is-completed|lecture-completion-data|Complete and Continue|<script|<iframe|<object|<form|\son[a-z]+=|uploads\.teachable|student-viewer|docs\.google\.com/i);
  assert.doesNotMatch(text, /Receive .?a personalised, AI-supported response/);
  for (const lesson of teaching.lessons) for (const asset of lesson.assetPaths) assert.ok(teaching.assets.some(file => file.path === asset));
});
