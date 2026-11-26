#!/usr/bin/env python3
"""Assemble the public course prospectus and shared visitor-page text."""
from pathlib import Path
import csv
import html
import json
import re
import sys

root = Path(sys.argv[1])
content = Path(__file__).resolve().parents[1] / 'content/visitor-pages'
academy_name = 'The Public Service Transformation Academy'

pages = {
    '': ('home', academy_name, 'Capability building for people trying to achieve better outcomes in complex systems – commissioning, leading, and systems change for citizens and communities.'),
    'programmes': ('programmes', 'Programmes from the PSTA', 'Compare commissioning, leadership, and systems change programmes for individuals, teams, and local public service partners.'),
    'programmes/national-commissioning-academy': ('national', 'The National Commissioning Academy', 'Join the National Commissioning Academy in January 2027 as an individual or with colleagues. See the course, fees, group discounts, and how to apply.'),
    'learning-and-capability': ('team', 'A twelve-week programme for your team', 'A programme from the PSTA for eight to twelve people working on one service change with support from a senior sponsor.'),
    'about': ('about', 'About the PSTA', 'The Public Service Transformation Academy builds capability for better outcomes in complex systems. Meet the team and read about the organisation.'),
    'contact': ('contact', 'Contact the PSTA', 'Contact David Mason for programmes from the PSTA, Sarah Johnston for contract management, or Benjamin P Taylor for strategic partnerships.'),
    'community': ('community', 'Events and peer learning', 'Public events, facilitated case clinics, and contributions from participants and practitioners working with the PSTA.'),
    'in-house': ('in-house', 'Bespoke and local partnership programmes', 'Commission a programme from the PSTA for staff in your organisation or people working together across local public services.'),
    'tools': ('tools', 'Commissioning tools', 'Choose a free commissioning self-assessment, compare colleagues’ perspectives, or find the original adult social care question sheet.'),
}
with (content / 'copy.tsv').open(encoding='utf-8') as stream:
    copy_edits = list(csv.reader(stream, delimiter='\t'))
if any(len(row) != 2 for row in copy_edits):
    raise ValueError('Each copy edit needs the source and replacement text')


def update_metadata(source, title, description):
    title = html.escape(title, quote=True)
    desc = html.escape(description, quote=True)
    page_title = title if title == academy_name else f'{title} | {academy_name}'
    source = re.sub(r'<title>[^<]+</title>', lambda _: f'<title>{page_title}</title>', source, count=1)
    for key, value in [('name="description"', desc), ('property="og:description"', desc), ('property="og:title"', title)]:
        source = re.sub(r'(<meta ' + key + r' content=")[^"]*', lambda m: m[1] + value, source)
    return source


def assemble(source, route):
    filename, title, description = pages[route]
    body = (content / (filename + '.html')).read_text(encoding='utf-8')
    if route == '':
        latest = re.search(r'<section class="section psta-latest-panel".*?</section>', source, re.S)
        secret = re.search(r'<a class="iteration-secret-link".*?</a>', source, re.S)
        if not latest or not secret:
            raise ValueError('The generated home news or feedback feature is missing')
        body += latest[0] + secret[0]
    if route == 'programmes/national-commissioning-academy':
        # Keep the searchable course description consistent with the prospectus.
        def course_metadata(match):
            data = json.loads(match[1])
            for entry in data:
                if entry.get('@type') == 'Course':
                    entry['description'] = description
            return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'
        source = re.sub(r'<script type="application/ld\+json">(.*?)</script>', course_metadata, source, flags=re.S)
    source = re.sub(r'(<main\b[^>]*>).*?(</main>)', lambda m: m[1] + '\n' + body + '\n' + m[2], source, count=1, flags=re.S)
    return update_metadata(source, title, description)


def publication(route):
    return route.startswith(('news/', 'insights/', '2017/'))


for path in root.rglob('index.html'):
    route = path.parent.relative_to(root).as_posix().strip('.')
    source = path.read_text(encoding='utf-8')
    if '<main' not in source:
        continue
    # Shared navigation also appears around independently authored articles.
    source = source.replace('National Commissioning Academy applications are open: Starting January 2027', 'National Commissioning Academy · January 2027 intake')
    source = source.replace('Practical development for people changing public services from inside the work.', 'Capability building for better outcomes in complex systems.')
    source = source.replace('href="/in-house/">In-house</a>', 'href="/in-house/">Bespoke</a>').replace('href="/contact/">Talk to us</a>', 'href="/contact/">Contact</a>')
    if not publication(route) and not route.startswith(('wp-', 'wordpress')):
        if route in pages:
            source = assemble(source, route)
        source = source.replace('</head>', '<link rel="stylesheet" href="/assets/css/visitor-edition.css"></head>', 1)
        source = re.sub(r'<body class="', '<body class="academy-visitor ', source, count=1)
        if 'commissioning-compass/reading' not in route and '/workspace' not in route:
            for before, after in copy_edits:
                source = source.replace(before, after)
            source = re.sub(r'<section class="cta-panel">(?:(?!</section>).)*?Tell us what is happening, who needs to act, and what cannot wait\.(?:(?!</section>).)*?</section>', '', source, flags=re.S)
            if route.startswith('partners/'):
                source = re.sub(r'<p class="eyebrow">(Formal partner|Informal partner|Lead partner|Accredited delivery partner)</p>', r'<p class="partner-role">\1</p>', source)
            source = re.sub(r'<p class="eyebrow">[^<]*</p>', '', source)
            source = source.replace('<p class="offer-lead strategy-lead">A substantial, practice-based programme for people who need to understand, lead, and sustain transformation.</p>', '')
            source = source.replace('<p>To enquire, email the address above with your organisation, question, the people involved, and intended timing.</p>', '')
        if route == 'programmes/contract-management-development':
            source = source.replace('Open to applications', 'Enquire about availability').replace('Apply or ask about a place', 'Ask Sarah about places')
            source = source.replace('Applications are open. The programme launches on', 'The published start date for this group was')
            source = source.replace('To secure your place or find out more, contact', 'For current availability or future dates, contact')
            source = source.replace('>Launch</dt>', '>Published start date</dt>')
    if route in pages:
        # Keep the latest visitor edition consistent with the owner's standing
        # terminology, after all page-specific copy substitutions have run.
        source = source.replace('In-house', 'Bespoke').replace('in-house', 'bespoke')
        source = source.replace('/bespoke/', '/in-house/')
        source = re.sub(r'\bThe Academy\b', 'The PSTA', source)
        source = re.sub(r'\bthe Academy\b', 'the PSTA', source)
    path.write_text(source, encoding='utf-8')
