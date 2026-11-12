"""Render the retained Compass beta paper as an accessible reading edition."""
from html import escape
from html.parser import HTMLParser
import re


SECTION_TITLES = {
    'Our original Commissioning Compass': 'original-compass',
    'Compass v2.0: the proposition': 'proposition',
    'Systems change as the operating logic': 'systems-change',
    'Principles': 'principles',
    'Compass v2.0: the architecture': 'architecture',
    'The eight aspects as living-system lenses': 'eight-lenses',
    'The five moves': 'five-moves',
    'Discipline on language and framing': 'language-and-framing',
    'Power': 'power',
    'Using the Compass v2.0 beta': 'using-the-beta',
}
SUBHEADINGS = {
    'Whole system conditions', 'Good relations and patterns of organising',
    'Growing capability and confidence', 'People, lived purpose',
    'Shared sensing, insight, and experiments',
    'Agency, shared action, and convening change',
    'Shared choosing, reviewing, and adapting action',
    'Forms of assets, help, infrastructure, and action',
    'Holistic opening up', 'Sensemaking', 'Strategising', 'Making change',
    'Collective learning',
}
LIST_STARTS = {
    'The ‘service provision’ default;',
    'Start with people living well, not services being provided.',
    'holistic opening up',
    'What changed in people’s lived experience?',
    "Provider drift says:",
    "Use 'people living their lives', not 'service users'.",
}
LIST_ENDS = {
    'And, realistically, with the pressures many commissioners face,',
    'Use the eight aspects (set out below)',
    'That gives the whole model',
    'The last question is the one',
    'The integrated model needs a different grammar.',
    'Of course, the real point isn’t to police language.',
}


def inline(text):
    """Link known HTTP(S)/short-link source URLs without changing visible text."""
    pattern = r'https?://[^\s<>]+|(?<![\w/])link\.redquadrant\.com/[^\s<>]+'
    result, end = [], 0
    for match in re.finditer(pattern, text):
        url = match[0].rstrip('.,;!?)')
        result.append(escape(text[end:match.start()]))
        href = url if url.startswith(('http://', 'https://')) else 'https://' + url
        result.append('<a href="' + escape(href, quote=True) + '">' + escape(url) + '</a>')
        result.append(escape(match[0][len(url):]))
        end = match.end()
    result.append(escape(text[end:]))
    return ''.join(result)


def source_element(tag, text, attributes=''):
    return '<' + tag + ' data-paper-source' + attributes + '>' + inline(text) + '</' + tag + '>'


class SourceText(HTMLParser):
    """Extract only the original text, excluding navigation and explanatory UI."""
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if self.depth:
            self.depth += 1
        elif any(key == 'data-paper-source' for key, _ in attrs):
            self.depth = 1

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1
            if not self.depth:
                self.parts.append(' ')

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)


def normalise(text):
    return ' '.join(text.split())


def render_matrix(tool):
    """Keep the full matrix visible on desktop and read it by lens on mobile."""
    sections = tool['sections']
    assert len(sections) == 8 and all(len(s['questions']) == 5 for s in sections)
    moves = [q['label'] for q in sections[0]['questions']]
    assert all([q['label'] for q in s['questions']] == moves for s in sections)
    table = '<div class="paper-matrix-scroll" role="region" aria-labelledby="matrix-heading" tabindex="0"><table class="paper-matrix-table"><caption>Eight lenses and five moves. Read across a lens, or follow a move down the table.</caption><thead><tr><th scope="col" data-paper-source>Aspect</th>'
    table += ''.join(source_element('th', move, ' scope="col"') for move in moves)
    table += '</tr></thead><tbody>'
    cards = '<div class="paper-matrix-cards">'
    for number, section in enumerate(sections, 1):
        table += '<tr>' + source_element('th', section['title'], ' scope="row"')
        table += ''.join(source_element('td', question['prompt']) for question in section['questions']) + '</tr>'
        cards += '<article class="paper-matrix-card"><h3><span class="paper-lens-number" aria-hidden="true">' + str(number).zfill(2) + '</span>' + escape(section['title']) + '</h3><dl>'
        cards += ''.join('<div><dt>' + escape(question['label']) + '</dt><dd>' + inline(question['prompt']) + '</dd></div>' for question in section['questions'])
        cards += '</dl></article>'
    table += '</tbody></table></div>'
    cards += '</div>'
    return '<section class="paper-matrix-section" id="matrix" aria-labelledby="matrix-heading"><div class="paper-matrix-intro">' + source_element('h2', 'The matrix', ' id="matrix-heading"') + '<p>Use any lens or move that helps you work with the situation. Return to the questions as your understanding changes.</p><a class="paper-button" href="/tools/compass-v2-beta/workspace/">Work with the matrix <span aria-hidden="true">→</span></a></div><p class="paper-matrix-hint">Scroll sideways to read all five moves. You can focus the table and use the arrow keys.</p>' + table + cards + '</section>'


def render_paper(source, tool):
    lines = [line.strip() for line in source.splitlines() if line.strip()]
    assert lines[:2] == ['Compass v2.0 beta', 'Commissioning as collective system learning']
    matrix_start = lines.index('The matrix')
    body_lines = lines[4:matrix_start]
    content, section_open, list_open = [], False, False
    for line in body_lines:
        is_section = line in SECTION_TITLES
        is_subheading = line in SUBHEADINGS
        if list_open and (is_section or is_subheading or any(line.startswith(prefix) for prefix in LIST_ENDS)):
            content.append('</ul>')
            list_open = False
        if is_section:
            if section_open:
                content.append('</section>')
            content.append('<section id="' + SECTION_TITLES[line] + '" class="paper-section">')
            content.append(source_element('h2', line))
            section_open = True
        elif is_subheading:
            content.append(source_element('h3', line))
        else:
            if not list_open and any(line.startswith(prefix) for prefix in LIST_STARTS):
                content.append('<ul>')
                list_open = True
            content.append(source_element('li' if list_open else 'p', line))
    if list_open:
        content.append('</ul>')
    if section_open:
        content.append('</section>')
    navigation = '<aside class="paper-sidebar"><nav aria-label="Working paper contents"><p class="paper-sidebar-title">In this paper</p><ol>'
    labels = ['The original Compass', 'The proposition', 'Systems change', 'Principles', 'The architecture', 'Eight lenses', 'Five moves', 'Language and framing', 'Power', 'Using the beta']
    navigation += ''.join('<li><a href="#' + anchor + '">' + label + '</a></li>' for anchor, label in zip(SECTION_TITLES.values(), labels))
    navigation += '<li><a class="paper-matrix-link" href="#matrix">The full matrix <span aria-hidden="true">↘</span></a></li></ol></nav><div class="paper-sidebar-footer"><p>Keep a copy of the original working paper.</p><a href="/assets/compass/sources/compass-v2-beta-2026-06-13.txt" download>Download original text</a></div></aside>'
    hero = '<header class="paper-hero"><div class="paper-shell"><nav class="paper-breadcrumbs" aria-label="Breadcrumb"><a href="/tools/compass/">Compass and practice</a><span aria-hidden="true">/</span><a href="/tools/compass-v2-beta/">The beta</a></nav><div class="paper-kicker"><span>Working paper</span><span>13 June 2026</span></div>'
    hero += source_element('p', lines[0], ' class="paper-edition"')
    hero += source_element('h1', lines[1])
    hero += '<p class="paper-byline">Benjamin P Taylor</p><div class="paper-hero-actions"><a class="paper-button" href="/tools/compass-v2-beta/workspace/">Open the workspace <span aria-hidden="true">→</span></a><a class="paper-jump" href="#matrix">Go to the matrix <span aria-hidden="true">↓</span></a></div></div></header>'
    article = '<article class="paper-prose" aria-label="Working paper">' + source_element('p', lines[2], ' class="paper-share"') + source_element('blockquote', lines[3], ' class="paper-opening"') + ''.join(content) + '</article>'
    result = '<main id="main-content" class="site-main compass-paper-page">' + hero + '<div class="paper-shell paper-reading-layout">' + navigation + article + '</div><div class="paper-shell">' + render_matrix(tool) + '<div class="paper-endnote"><p>Working paper by Benjamin P Taylor · 13 June 2026</p><a href="#main-content">Back to the beginning <span aria-hidden="true">↑</span></a></div></div></main>'
    extracted = SourceText()
    extracted.feed(result)
    assert normalise(''.join(extracted.parts)) == normalise(source), 'The reading edition must preserve the complete original paper and matrix wording'
    return result
