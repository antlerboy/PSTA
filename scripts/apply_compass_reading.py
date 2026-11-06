#!/usr/bin/env python3
"""Build the PSTA Commissioning Compass reading pages."""
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
case_source = json.loads((source_root / 'aspects-cases-equity-2023-06.json').read_text(encoding='utf-8'))
origin_source = json.loads((source_root / 'toolkit-origins-2023-06.json').read_text(encoding='utf-8'))
cases = {lesson['aspect']: lesson for lesson in case_source['lessons']}
slides = {slide['number']: slide for slide in deck['slides']}
approaches = {approach['number']: approach for approach in pre_reading['approaches']}
base = 'tools/commissioning-compass/reading'
domain = 'https://www.publicservicetransformation.org'
template = (root / 'tools/commissioning-compass/index.html').read_text(encoding='utf-8')
published = []
e = html.escape

assert len(course['chapters']) == 49
assert len(cases) == 8
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
    body = '<section class="source-extract" aria-label="Source slide ' + str(number) + '"><h2>' + e(title) + '</h2>'
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
    body = '<section class="source-extract">'
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


def render_sections(sections):
    body = ''
    for section in sections:
        body += '<section class="source-extract"><h3>' + e(section['heading']) + '</h3>'
        in_list = False
        for paragraph in section['paragraphs']:
            listed = paragraph.get('kind') == 'list-item'
            if listed and not in_list:
                body += '<ul>'
                in_list = True
            elif not listed and in_list:
                body += '</ul>'
                in_list = False
            tag = 'li' if listed else 'p'
            body += '<' + tag + '>' + e(paragraph['text']) + '</' + tag + '>'
        if in_list:
            body += '</ul>'
        for link in section.get('links', []):
            body += '<p><a href="' + e(link['url'], quote=True) + '">' + e(link['text']) + '</a></p>'
        body += '</section>'
    return body


def current_lesson(kind):
    if kind == 'using-and-improving':
        return '<p>Use the Compass for a decision or change you can act on. Decide which place, service, or set of relationships you’re assessing, and whose experience you need to understand.</p><h2>Carry out an assessment</h2><p>Record your first view of the eight aspects, then work through the questions and the factors that constrain or enable commissioning. Add the evidence behind your answers. Ask colleagues to record their own views, and discuss why scores or accounts differ.</p><p>Choose what to act on, who can do it, and when you’ll review the result. Keep the original record so you can compare what you expected with what happened.</p><p><a class="button button-gold" href="/tools/commissioning-compass/workspace/">Open the assessment</a></p><h2>Choose an edition</h2><p>The original assessment uses eight aspects, scores, questions, and factors. smartCompass offers sixteen reflective questions. The v2 beta uses an eight-lens matrix. Choose the edition that helps you examine your work.</p><p><a href="/tools/compass/">Compare the editions</a></p><h2>Corrections and examples</h2><p>Tell the PSTA which question or part of the method you used, what you were trying to understand, and what helped or missed something. Include the evidence behind a correction, and suggest wording where you can. Leave out identifying case details unless you have permission to share them.</p><p><a href="/enquire/">Send a question, correction, or example</a></p>'
    if kind == 'contact-and-updates':
        return '<h2>Discuss your work with the PSTA</h2><p>Contact the Public Service Transformation Academy about using the Compass with your team, facilitated assessment, or commissioning development.</p><p>Email <a href="mailto:info@publicservicetransformation.org">info@publicservicetransformation.org</a>, or <a href="/enquire/">prepare an enquiry</a> with the decision you need to make, the people involved, and the help you want.</p><h2>Keep up to date</h2><p><a href="/news/">Read the latest news and resources</a>, <a href="/news/feed.xml">subscribe to the news feed</a>, or <a href="/programmes/">see the PSTA’s programmes</a>.</p><h2>Work through a case with colleagues</h2><p>The case-clinic guide provides a six-session format for a group working on cases from their own organisations. Use the host guide and participant brief, or propose a case for a group with the PSTA.</p><p><a href="/community/case-clinics/">Use the case-clinic resources</a> · <a href="/community/bring-a-case/">Propose a case</a></p>'
    raise ValueError('Unknown current lesson')


shutil.copytree(repo / 'assets/compass/reading', root / 'assets/compass/reading', dirs_exist_ok=True)
public_source = root / 'assets/compass/reading/source'
public_source.mkdir(parents=True, exist_ok=True)
for path in source_root.glob('*.json'):
    shutil.copy2(path, public_source / path.name)

source_notice = '<p><a href="/tools/commissioning-compass/workspace/">Use the assessment</a> · <a href="/' + base + '/sources/">Sources and acknowledgements</a></p>'

# Restore the original internal reference in the pre-reading from a published
# WordPress archive record. It remains a dated article, not a new news item.
assert related_article['originalDate'] == '2017-10-15'
article_body = '<p>Originally published on 15 October 2017.</p><article class="source-extract">' + ''.join('<p class="source-paragraph">' + e(paragraph) + '</p>' for paragraph in related_article['paragraphs']) + '</article><p><a href="/' + base + '/aspect-4/approach/">Return to the citizen-centred commissioning approach</a></p>'
page('2017/10/asset-based-areas-commission', related_article['title'], 'The PSTA’s article of 15 October 2017 on asset-based commissioning.', article_body)

groups = OrderedDict()
for chapter in course['chapters']:
    groups.setdefault(chapter['section'], []).append(chapter)
toc = ''.join('<section><h2>' + e(section) + '</h2><ul>' + ''.join('<li><a href="/' + chapter['route'] + '/">' + e(chapter['title']) + '</a></li>' for chapter in chapters) + '</ul></section>' for section, chapters in groups.items())
page(base, 'Commissioning Compass learning guide', 'Read the definitions, instructions, questions, factors, and eight approaches from the PSTA’s source material.', '<p>The Public Service Transformation Academy’s original teaching sources are available here without an account. Choose a chapter below, or use the assessment workspace to record your own answers, evidence, and actions.</p>' + source_notice + toc + '<p><a href="/' + base + '/sources/">Sources and acknowledgements</a> · <a href="https://public-service-transformation-academy.teachable.com/l/pdp/commissioning-compass">The original Teachable course</a></p>')

for index, chapter in enumerate(course['chapters']):
    if chapter.get('caseStudyAspect'):
        case = cases[chapter['caseStudyAspect']]
        body = '<p>These fictionalised examples draw on real councils and places, and show different stages of development in adult social care commissioning.</p><h2>' + e(case['sourceAspectHeading']) + '</h2>' + render_sections(case['sections'])
    elif chapter.get('currentLesson'):
        body = current_lesson(chapter['currentLesson'])
    elif chapter.get('resourceLesson'):
        body = '<p>The original toolkit was designed for adult social care commissioners. The extracts below explain its purpose, development, and resources.</p>' + render_sections(origin_source['sections'])
    else:
        body = ''.join(render_slide(number) for number in chapter['slides'])
        if chapter.get('preReadingApproach'):
            body += '<h2>Applying this approach</h2>' + render_pre_reading(chapter['preReadingApproach'])

    body += '<nav class="reading-navigation" aria-label="Reading chapters">'
    if index:
        previous = course['chapters'][index - 1]
        body += '<p>Previous chapter: <a href="/' + previous['route'] + '/">' + e(previous['title']) + '</a></p>'
    if index + 1 < len(course['chapters']):
        following = course['chapters'][index + 1]
        body += '<p>Next chapter: <a href="/' + following['route'] + '/">' + e(following['title']) + '</a></p>'
    body += '<p><a href="/' + base + '/">All chapters</a> · <a href="/tools/commissioning-compass/workspace/">Record your assessment</a> · <a href="/' + base + '/sources/">Sources and acknowledgements</a></p></nav>'
    page(chapter['route'], chapter['title'], chapter['section'] + '. Commissioning Compass learning and practice.', body)

download_name = '2026-11-06 the PSTA Commissioning Compass reading sources v0.03 BT.txt'
# The download contains source text and plain version notes, with no HTML markup.
lines = ['The PSTA Commissioning Compass reading sources', '', 'Reading edition from the original teaching documents, prepared 6 November 2026.', 'June 2025 teaching text and June 2023 adult social care approaches pre-reading.', '', deck['title'], deck['scope'], '']
for slide in deck['slides']:
    lines += ['Slide ' + str(slide['number']), *slide['paragraphs'], '']
lines += [pre_reading['title'], pre_reading['scope'], '']
for approach in pre_reading['approaches']:
    lines += [paragraph['text'] for paragraph in approach['paragraphs']] + ['']
lines += [case_source['sourceTitle'], case_source['sourceDate'], '']
for case in case_source['lessons']:
    lines += [case['sourceAspectHeading']]
    for section in case['sections']:
        lines += [section['heading'], *[paragraph['text'] for paragraph in section['paragraphs']], '']
lines += [origin_source['title'], '']
for section in origin_source['sections']:
    lines += [section['heading'], *[paragraph['text'] for paragraph in section['paragraphs']], '']
(public_source / download_name).write_text('\n'.join(lines) + '\n', encoding='utf-8')
previous_download = public_source / '2026-11-06 the PSTA Commissioning Compass reading sources v0.01 BT.txt'
previous_download.unlink(missing_ok=True)
(public_source / '2026-11-06 the PSTA Commissioning Compass reading sources v0.02 BT.txt').unlink(missing_ok=True)
source_body = '<h2>Sources and versions</h2><dl><dt>' + e(deck['title']) + '</dt><dd>Source last modified 25 June 2025. ' + e(deck['scope']) + '</dd><dt>' + e(pre_reading['title']) + '</dt><dd>Dated 5 June 2023. ' + e(pre_reading['scope']) + '</dd></dl><p>The Local Government Association’s <a href="' + pre_reading['publicReferenceUrl'] + '">strengths-based commissioning toolkit</a> contains the earlier pre-reading and supporting material.</p><p><a href="/assets/compass/reading/source/' + quote(download_name) + '" download="' + e(download_name, quote=True) + '">' + e(download_name) + '</a></p><h2>Case studies and equality</h2><p>' + e(case_source['sourceTitle']) + ', June 2023, in <em>' + e(case_source['sourceSeries']) + '</em>. The fictionalised higher/lower examples draw on descriptions of real councils and places, and illustrate different stages of development.</p><h2>Origins and current guidance</h2><p><em>About applying a strengths-based methodology to your strategic commissioning</em>, June 2023, supplies the account of the original toolkit. The introduction and contact guidance reflect current use of the Compass and the PSTA’s public contact routes.</p><h2>Acknowledgements</h2>' + render_slide(99) + '<p><a href="/' + base + '/">Read the chapters</a> · <a href="/tools/commissioning-compass/workspace/">Use the assessment</a></p>'
page(base + '/sources', 'Sources and acknowledgements', 'Source documents and versions for the Commissioning Compass reading material.', source_body)

for relative in ['tools/commissioning-compass/index.html', 'tools/compass/index.html']:
    path = root / relative
    text = path.read_text(encoding='utf-8')
    marker = 'PSTA_COMPASS_READING_20261105'
    addition = '<!-- ' + marker + ' --><section class="section"><div class="shell"><h2>Read the original teaching sources</h2><p>Read the instructions, eight aspects, and eight approaches from the June 2025 teaching template. The approach pages include the full June 2023 pre-reading, with examples. Each chapter identifies its source version.</p><p><a class="button button-gold" href="/' + base + '/">Read the Commissioning Compass material</a> <a href="/' + base + '/sources/">Sources and acknowledgements</a></p></div></section><!-- /' + marker + ' -->'
    text = re.sub(r'<!-- ' + marker + r' -->.*?<!-- /' + marker + r' -->', '', text, flags=re.S)
    text = text.replace('</main>', addition + '</main>', 1)
    path.write_text(text, encoding='utf-8')
sitemap = root / 'sitemap.xml'
text = sitemap.read_text(encoding='utf-8')
for url in published:
    if '<loc>' + url + '</loc>' not in text:
        text = text.replace('</urlset>', '<url><loc>' + url + '</loc></url></urlset>')
sitemap.write_text(text, encoding='utf-8')
print('Built the PSTA Compass reading chapters, index, and sources page.')

# Internal tracking belongs outside the served visitor pages and downloads.
blocked = re.compile(r'Teachable material still to compare|migration status|course status|haven’t been compared with the final|have not been compared|not yet been exported|course comparison is still|current processing and email delivery|remainingCatalogueLessons|teachableBodiesCompared|sourceTopicsAvailable|expectedTeachableLessons|mediaAndDownloadCounts|archiveStatus|migrationStatus', re.I)
for folder in [root / 'tools', root / 'assets/compass']:
    for path in folder.rglob('*'):
        if path.is_file() and path.suffix in ['.html', '.json', '.txt']:
            assert not blocked.search(path.read_text(encoding='utf-8')), 'Internal task text in visitor output: ' + str(path.relative_to(root))
