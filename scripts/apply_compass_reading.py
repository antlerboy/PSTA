#!/usr/bin/env python3
"""Build source-labelled Compass reading pages without claiming a Teachable export."""
from collections import OrderedDict
from pathlib import Path
from urllib.parse import quote
import html
import json
import re
import shutil
import sys

repo = Path(__file__).resolve().parents[1]
root = Path(sys.argv[1]).resolve()
source_root = repo / 'content/compass/reading'
course = json.loads((source_root / 'reading-course.json').read_text(encoding='utf-8'))
deck = json.loads((source_root / 'teaching-deck-2025-06.json').read_text(encoding='utf-8'))
pre_reading = json.loads((source_root / 'approaches-pre-reading-2023-06.json').read_text(encoding='utf-8'))
related_article = json.loads((source_root / 'related-article-2017-10.json').read_text(encoding='utf-8'))
slides = {slide['number']: slide for slide in deck['slides']}
approaches = {approach['number']: approach for approach in pre_reading['approaches']}
base = 'tools/commissioning-compass/reading'
domain = 'https://www.publicservicetransformation.org'
template = (root / 'tools/commissioning-compass/index.html').read_text(encoding='utf-8')
published = []
e = html.escape

assert len(course['chapters']) == course['sourceTopicsAvailable'] == 38
assert len(course['remainingCatalogueLessons']) == 11
assert course['expectedTeachableLessons'] == 49 and course['teachableBodiesCompared'] == 0
assert len(approaches) == 8


def page(route, title, lead, body):
    text = re.sub(r'<title>.*?</title>', '<title>' + e(title) + ' | the PSTA</title>', template, count=1)
    url = domain + '/' + route.strip('/') + '/'
    text = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + e(lead, quote=True) + '">', text, count=1)
    text = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="' + url + '">', text, count=1)
    text = re.sub(r'<meta property="og:(title|description|url)" content="[^"]*">', lambda m: '<meta property="og:' + m[1] + '" content="' + e({'title': title, 'description': lead, 'url': url}[m[1]], quote=True) + '">', text)
    text = re.sub(r'<script type="application/ld\+json">.*?</script>', '', text, flags=re.S)
    text = re.sub(r'<script\b[^>]*src="[^"]*easter-eggs\.js[^"]*"[^>]*>\s*</script>', '', text, flags=re.S)
    markup = '<main id="main-content" class="site-main"><section class="page-hero compass-reading-hero"><div class="shell"><p><a href="/">The PSTA</a> / <a href="/tools/compass/">Commissioning Compass</a> / <a href="/' + base + '/">Reading</a></p><h1>' + e(title) + '</h1><p class="lede">' + e(lead) + '</p></div></section><section class="section compass-reading-section"><div class="shell compass-reading">' + body + '</div></section></main>'
    text = re.sub(r'<main\b[^>]*>.*?</main>', lambda _: markup, text, count=1, flags=re.S)
    text = text.replace('</head>', '<link rel="stylesheet" href="/assets/compass/reading/reading.css?v=20261106"></head>')
    destination = root / route / 'index.html'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding='utf-8')
    published.append(url)


def render_slide(number):
    slide = slides[number]
    paragraphs = slide['paragraphs']
    if not paragraphs:
        return ''
    title = paragraphs[0]
    body = '<section class="source-extract" aria-label="Source slide ' + str(number) + '"><p class="source-location">June 2025 teaching template, slide ' + str(number) + '</p><h2>' + e(title) + '</h2>'
    if number == 25:
        assert len(paragraphs) == 18
        body += '<div class="reading-table"><table><thead><tr><th scope="col">' + e(paragraphs[0]) + '</th><th scope="col">' + e(paragraphs[1]) + '</th></tr></thead><tbody>'
        for index in range(2, 18, 2):
            body += '<tr><td>' + e(paragraphs[index]) + '</td><td>' + e(paragraphs[index + 1]) + '</td></tr>'
        body += '</tbody></table></div>'
    else:
        body += ''.join('<p class="source-paragraph">' + e(paragraph) + '</p>' for paragraph in paragraphs[1:])
    if number == 4:
        figure = deck['figures'][0]
        body += '<figure><a href="' + figure['file'] + '"><img src="' + figure['file'] + '" alt="Commissioning connects resources to outcomes through interventions, with learning feeding back into needs, resources, interventions, outcomes, and impact." loading="lazy" width="1920" height="1080"></a><figcaption>' + e(figure['credit']) + ' Open the image to read the original figure at full size.</figcaption></figure>'
    return body + '</section>'


def render_pre_reading(number):
    body = '<section class="source-extract"><p class="source-location">June 2023 adult social care pre-reading, approach ' + str(number) + '</p>'
    in_list = False
    for paragraph in approaches[number]['paragraphs']:
        if paragraph['style'] != 'ListParagraph' and in_list:
            body += '</ul>'
            in_list = False
        content = ''.join('<a href="' + e(run['url'], quote=True) + '">' + e(run['text']) + '</a>' if run.get('url') else e(run['text']) for run in paragraph['runs'])
        if paragraph['style'] == 'ListParagraph':
            if not in_list:
                body += '<ul>'
                in_list = True
            body += '<li>' + content + '</li>'
        elif paragraph['style'].startswith('Heading'):
            tag = 'h2' if paragraph['style'] == 'Heading1' else 'h3'
            body += '<' + tag + '>' + content + '</' + tag + '>'
        else:
            body += '<p>' + content + '</p>'
    return body + ('</ul>' if in_list else '') + '</section>'


shutil.copytree(repo / 'assets/compass/reading', root / 'assets/compass/reading', dirs_exist_ok=True)
public_source = root / 'assets/compass/reading/source'
public_source.mkdir(parents=True, exist_ok=True)
for path in source_root.glob('*.json'):
    shutil.copy2(path, public_source / path.name)

source_notice = '<aside class="reading-status"><p><strong>Teaching material from June 2025.</strong> The approach pages also include June 2023 pre-reading. These documents haven’t been compared with the final Teachable course.</p><p><a href="/' + base + '/sources/">Check the sources and remaining course material</a> · <a href="/tools/commissioning-compass/workspace/">Use the March 2026 assessment</a></p></aside>'

# Restore the original internal reference in the pre-reading from a published
# WordPress archive record. It remains a dated article, not a new news item.
assert related_article['sourceStatus'] == 'publish' and related_article['originalDate'] == '2017-10-15'
article_body = '<p>Originally published on 15 October 2017. The text below was recovered from the published WordPress content export prepared on 19 February 2026. Its wording is retained. The original article image and comments have not been recovered here.</p><article class="source-extract">' + ''.join('<p class="source-paragraph">' + e(paragraph) + '</p>' for paragraph in related_article['paragraphs']) + '</article><p><a href="/' + base + '/aspect-4/approach/">Return to the citizen-centred commissioning approach</a></p>'
page('2017/10/asset-based-areas-commission', related_article['title'], 'The PSTA’s article of 15 October 2017, restored from the published content archive.', article_body)

groups = OrderedDict()
for chapter in course['chapters']:
    groups.setdefault(chapter['section'], []).append(chapter)
toc = ''.join('<section><h2>' + e(section) + '</h2><ul>' + ''.join('<li><a href="/' + chapter['route'] + '/">' + e(chapter['title']) + '</a></li>' for chapter in chapters) + '</ul></section>' for section, chapters in groups.items())
page(base, 'Commissioning Compass reading', 'Read the definitions, instructions, questions, factors, and eight approaches from the PSTA’s source material.', '<p>The Public Service Transformation Academy’s original teaching sources are available here without an account. Choose a chapter below, or use the assessment workspace to record your own answers, evidence, and actions.</p>' + source_notice + toc + '<p><a href="/' + base + '/sources/">Sources, acknowledgements, and migration status</a> · <a href="https://public-service-transformation-academy.teachable.com/l/pdp/commissioning-compass">The original Teachable course</a></p>')

for index, chapter in enumerate(course['chapters']):
    body = source_notice + ''.join(render_slide(number) for number in chapter['slides'])
    if chapter.get('preReadingApproach'):
        body += '<h2>The 2023 adult social care pre-reading</h2><p>The earlier source gives a fuller account of this approach, with examples and references. Its context and wording are retained below.</p>' + render_pre_reading(chapter['preReadingApproach'])
    body += '<nav class="reading-navigation" aria-label="Reading chapters">'
    if index:
        previous = course['chapters'][index - 1]
        body += '<p>Previous chapter: <a href="/' + previous['route'] + '/">' + e(previous['title']) + '</a></p>'
    if index + 1 < len(course['chapters']):
        following = course['chapters'][index + 1]
        body += '<p>Next chapter: <a href="/' + following['route'] + '/">' + e(following['title']) + '</a></p>'
    body += '<p><a href="/' + base + '/">All reading chapters</a> · <a href="/tools/commissioning-compass/workspace/">Record your assessment</a></p></nav>'
    page(chapter['route'], chapter['title'], chapter['section'] + '. Teaching text from June 2025.' + (' Includes the full June 2023 pre-reading.' if chapter.get('preReadingApproach') else ''), body)

download_name = '2026-11-06 the PSTA Commissioning Compass reading sources v0.01 BT.txt'
# The download contains source text and plain version notes, with no HTML markup.
lines = ['The PSTA Commissioning Compass reading sources', '', 'Reading edition from the original teaching documents, prepared 6 November 2026.', 'June 2025 teaching text and June 2023 adult social care approaches pre-reading. Teachable lesson bodies, media, and downloads have not been compared.', '', deck['title'], deck['scope'], '']
for slide in deck['slides']:
    lines += ['Slide ' + str(slide['number']), *slide['paragraphs'], '']
lines += [pre_reading['title'], pre_reading['scope'], '']
for approach in pre_reading['approaches']:
    lines += [paragraph['text'] for paragraph in approach['paragraphs']] + ['']
(public_source / download_name).write_text('\n'.join(lines) + '\n', encoding='utf-8')
remaining = '<ul>' + ''.join('<li>' + e(row['section']) + ': <a href="' + e(row['catalogueLessonUrl'], quote=True) + '">' + e(row['title']) + '</a></li>' for row in course['remainingCatalogueLessons']) + '</ul>'
source_body = '<h2>What is available here</h2><p>These 38 chapters cover 38 of the 49 topics listed in the original Teachable course: six introductory topics, plus definitions, questions, factors, and approaches for all eight aspects. The approach pages also contain the full 2023 pre-reading sections, including examples and references.</p><h2>Sources and versions</h2><dl><dt>' + e(deck['title']) + '</dt><dd>Source last modified 25 June 2025. ' + e(deck['scope']) + '</dd><dt>' + e(pre_reading['title']) + '</dt><dd>Dated 5 June 2023. ' + e(pre_reading['scope']) + '</dd></dl><p>The Local Government Association’s <a href="' + pre_reading['publicReferenceUrl'] + '">original strengths-based commissioning toolkit page</a> links to the earlier pre-reading and supporting material.</p><p><a href="/assets/compass/reading/source/' + quote(download_name) + '" download="' + e(download_name, quote=True) + '">' + e(download_name) + '</a></p><h2>Teachable material still to compare</h2><p>No Teachable lesson body has yet been compared in full against these source pages. The number of embedded videos, images, and downloads in the course has not yet been established. All media and attached downloads need checking, including those in chapters with text available here.</p><p>The following eleven catalogue lessons don’t yet have equivalent local source chapters. The eight case-study and equality lessons may contain later additions. The 2023 examples on approach pages don’t establish what those later lessons contain.</p>' + remaining + '<h2>Acknowledgements</h2>' + render_slide(99) + '<p><a href="/' + base + '/">Read the available chapters</a> · <a href="https://public-service-transformation-academy.teachable.com/l/pdp/commissioning-compass">Open the original Teachable course</a></p>'
page(base + '/sources', 'Commissioning Compass sources and course status', 'Source versions, available teaching text, and the Teachable material still to compare.', source_body)

for relative in ['tools/commissioning-compass/index.html', 'tools/compass/index.html']:
    path = root / relative
    text = path.read_text(encoding='utf-8')
    marker = 'PSTA_COMPASS_READING_20261105'
    addition = '<!-- ' + marker + ' --><section class="section"><div class="shell"><h2>Read the original teaching sources</h2><p>Read the instructions, eight aspects, and eight approaches from the June 2025 teaching template. The approach pages include the full June 2023 pre-reading, with examples. Each page identifies its source version; the Teachable course comparison is still to be completed.</p><p><a class="button button-gold" href="/' + base + '/">Read the Commissioning Compass material</a> <a href="/' + base + '/sources/">Sources and course status</a></p></div></section><!-- /' + marker + ' -->'
    text = re.sub(r'<!-- ' + marker + r' -->.*?<!-- /' + marker + r' -->', '', text, flags=re.S)
    text = text.replace('</main>', addition + '</main>', 1)
    path.write_text(text, encoding='utf-8')
sitemap = root / 'sitemap.xml'
text = sitemap.read_text(encoding='utf-8')
for url in published:
    if '<loc>' + url + '</loc>' not in text:
        text = text.replace('</urlset>', '<url><loc>' + url + '</loc></url></urlset>')
sitemap.write_text(text, encoding='utf-8')
print('Built 38 substantive Compass source chapters, a reading index, and a source/status page for the PSTA. No exact Teachable migration claimed.')
