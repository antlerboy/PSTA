"""Apply the 30 September public-content review after the historical generators."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])

def amend(route, transform):
    path = root / route / 'index.html'
    original = path.read_text(encoding='utf-8')
    revised = transform(original)
    if revised == original:
        raise SystemExit(f'September review found no matching content in {route}')
    path.write_text(revised, encoding='utf-8')

def insights(text):
    text = text.replace(
        'The archive should do more than announce programmes. It should give alumni, partners and prospective participants material they can use in a meeting, workshop or live piece of work.',
        'Use these notes, cases, and tools in a meeting, workshop, or live piece of work. They offer questions and approaches to test against your own experience.')
    return re.sub(
        r'<h2 id="what-moved-from-the-former-site">.*?</p><p>.*?</p>',
        '<h2 id="more-practice-and-reading">More practice and reading</h2>'
        '<p>Find recent articles, reports, and contributions from the PSTA community in '
        '<a href="/news/">News</a>, or read '
        '<a href="/commissioning-academy/testimonials/">participants’ experiences of the National Commissioning Academy</a>.</p>',
        text, flags=re.S)

amend('insights', insights)
amend('about', lambda t: t.replace(
    'Since then, national and place-based cohorts have brought together more than 1,500 senior decision-makers and practitioners across local and central government, health, policing, housing, civil society and other public services.',
    'More than 2,500 people have graduated from the Academy and its programmes, across local and central government, health, policing, housing, civil society, and other public services.'))

amend('partners/basis', lambda t: re.sub(
    r'<h2 id="developing-the-partnership">.*?</p>',
    '<h2 id="accredited-programmes">Accredited programmes</h2><p>Explore '
    '<a href="/programmes/service-transformation-programme/">the Service Transformation Programme</a> and '
    '<a href="/programmes/agile-master-in-public-services/">Agile Master in Public Services</a>. '
    'Both are delivered by Basis and accredited by the PSTA. Contact Basis for dates, fees, and organisational delivery.</p>',
    t, flags=re.S).replace(
        '<div class="partner-hero-logo" aria-hidden="true"><span class="partner-logo-fallback">Basis - Changing the Change</span></div>', ''))

amend('community', lambda t: t.replace('Applications open by emailing ', 'To express interest, email ').replace(
    '</a> and say which live questions you would bring.',
    '</a> with the live questions you would bring. We will discuss the format and availability with you.'))

amend('privacy', lambda t: t.replace(
    'This website does not currently use advertising cookies, user accounts or an embedded contact form. It does not collect personal information merely because you visit it. Standard server logs may be retained by the hosting provider for security and operation.',
    'This website does not use advertising cookies, user accounts, or an embedded contact form. '
    'We use a page-visit counter served from transduction.systems to understand which pages are used. '
    'The counter sends the page path to events.transduction.systems. It does not set cookies or send the '
    'page’s query string, and it respects the browser’s Do Not Track setting. '
    'As with other web requests, the hosting and analytics services receive connection information, '
    'including an IP address and standard request headers. Standard server logs may be retained for security and operation.'))

def academy(text):
    # Combine adjacent team invitations, keeping both useful routes.
    text = re.sub(r'<!-- PSTA_SERVICE_CHANGE_20260919 --><section class="section">.*?</section>', '', text, count=1, flags=re.S)
    text = text.replace('<h2>Bring a team and a live challenge</h2>', '<h2>Bring a team and a live commissioning challenge</h2>')
    text = text.replace(
        '<h3>Team pricing</h3>',
        '<p>For a separately commissioned twelve-week programme combining workplace practice and sponsor review, '
        'see our <a href="/learning-and-capability/">learning and capability partnership</a>.</p><h3>Team pricing</h3>')
    return text.replace('Action ,  ', 'Action: ').replace('Process ,  ', 'Process: ').replace('Knowledge ,  ', 'Knowledge: ')

amend('programmes/national-commissioning-academy', academy)

# Known lists in existing public copy, including descriptions and share metadata.
replacements = {
    'outcomes, systems, relationships, evidence, power and practical action': 'outcomes, systems, relationships, evidence, power, and practical action',
    'Practical, cross-sector and built around real work': 'Practical, cross-sector, and built around real work',
    'outcomes, communities, providers, evidence and the whole system': 'outcomes, communities, providers, evidence, and the whole system',
    'authority, influence, relationships and complexity': 'authority, influence, relationships, and complexity',
    'Short pieces, tools and cases': 'Short pieces, tools, and cases',
    'programmes, events, resources and case material': 'programmes, events, resources, and case material',
    'commissioners, transformation leads and public service colleagues': 'commissioners, transformation leads, and public service colleagues',
    'Commissioners, transformation leads and public service colleagues': 'Commissioners, transformation leads, and public service colleagues',
    'peer learning and work on live challenges': 'peer learning, and work on live challenges',
    'collaborate, innovate and lead': 'collaborate, innovate, and lead',
    'systems thinking, cybernetics and complexity': 'systems thinking, cybernetics, and complexity',
    'organisations, participants and partners': 'organisations, participants, and partners',
    'public, private and voluntary sectors': 'public, private, and voluntary sectors',
    'facilitators, coaches and specialist partners': 'facilitators, coaches, and specialist partners',
    'Practical notes, cases and tools': 'Practical notes, cases, and tools',
    'events, resources, cases and programme updates': 'events, resources, cases, and programme updates',
    'partners, alumni and practitioners': 'partners, alumni, and practitioners',
    'dates, audience, format and a named contact': 'dates, audience, format, and a named contact',
    'Generic promotion, ungrounded claims and content': 'Generic promotion, ungrounded claims, and content',
    'Alumni, peers, events and developing communities': 'Alumni, peers, events, and developing communities',
    'programmes, tools, webinars and selected partner resources': 'programmes, tools, webinars, and selected partner resources',
    'tools, practice and outside perspectives': 'tools, practice, and outside perspectives',
    'case, resource, event or short practice note': 'case, resource, event, or short practice note',
    'relationships, capability, insight, policy, process and delivery models': 'relationships, capability, insight, policy, process, and delivery models',
    'commissioners, leaders and partners': 'commissioners, leaders, and partners',
    'relationship, power, information or capability problem': 'relationship, power, information, or capability problem',
    'benchmark, maturity score, inspection or performance judgement': 'benchmark, maturity score, inspection, or performance judgement',
    'relationships, resources and uncertainty': 'relationships, resources, and uncertainty',
    'tested next moves and greater confidence': 'tested next moves, and greater confidence',
    'community outcomes or major change': 'community outcomes, or major change',
    'action learning and live challenge work': 'action learning, and live challenge work',
    'simulations, exercises and live examples': 'simulations, exercises, and live examples',
    'notice, review and adapt': 'notice, review, and adapt',
}
for page in root.rglob('*.html'):
    text = page.read_text(encoding='utf-8')
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace('>Service Transformation Programme</a>', '>The Service Transformation Programme</a>')
    page.write_text(text, encoding='utf-8')

print('Applied September public-content review: facts, reader copy, programme routes, and privacy transparency')
