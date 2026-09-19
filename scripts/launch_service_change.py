"""Publish the approved service-change offer without changing the site design."""
from __future__ import annotations
from html import escape
from pathlib import Path
import re


def insert_once(text: str, marker: str, block: str, before: str = '</main>') -> str:
    if marker in text:
        return text
    if before not in text:
        raise ValueError(f'Missing insertion point: {before}')
    return text.replace(before, block + before, 1)


def apply_launch_service_change(root: Path) -> None:
    domain = 'https://www.publicservicetransformation.org'
    slug = 'learning-and-capability'
    title = 'Learning and capability partner'
    lead = 'Help a sponsored team change its work, and show what happened.'
    template = (root / 'transformation-academies/index.html').read_text(encoding='utf-8')
    sections = [
        ('Who it is for', 'For programme sponsors who need more than a course: a team able to apply learning, change decisions, and sustain a live improvement.'),
        ('First step', 'A twelve-week commissioned programme around one real change, normally for a team of eight to twelve. The design is agreed with the sponsor and can complement an existing Academy or delivery programme.'),
        ('How we work', 'We establish a baseline and the sponsoring decision. Participants practise with feedback, test changes in their workplace, and review the consequences with peers and their sponsor. We work on the authority, measures, relationships, and resources that help or prevent application.'),
        ('What you get', 'A practical inquiry and test plan; agreed evidence; a record of decisions and changes; sponsor reviews; reusable tools; and a 100-day continuation plan. Findings include what did not improve and what cannot yet be concluded.'),
        ('Working together', 'The Public Service Transformation Academy leads the learning design, drawing on commissioning, systems practice, and public-service experience. RedQuadrant or other agreed partners can provide separately scoped implementation support. The sponsor protects application time and access to decisions.'),
        ('Limits', 'Attendance is not proof of impact. We distinguish contribution from causation and learning support from independent evaluation. We do not promise accreditation or a funded apprenticeship place unless separately confirmed.'),
        ('What follows', 'The programme can lead to an in-house Academy, a further shared problem, or a client-led continuation. The aim is useful capability, not dependence on external facilitation.')
    ]
    body = ''.join('<section><h2>' + escape(heading) + '</h2><p>' + escape(text) + '</p></section>' for heading, text in sections)
    body += '''<section><h2>Discuss a sponsored team</h2><p>Bring one real change, a team who will work on it, and a sponsor who can help remove obstacles. We agree the design, access, timing, responsibilities, and fee before starting.</p><p><a class="button" href="mailto:david.mason@publicservicetransformation.org?subject=Learning%20and%20capability%20partner">Email David Mason</a></p></section><section><h2>Related ways to work with us</h2><p><a href="/programmes/national-commissioning-academy/">National Commissioning Academy</a>: explore the programme and discuss individual places, a sponsored team, or an in-house Academy.</p><p><a href="/systems-leadership-academy/">Systems Leadership Academy</a>: develop practice across organisational boundaries.</p><p><a href="/programmes/leading-transformation/">Leading Transformation</a>: develop a broader repertoire for public-service change.</p><p>When a programme needs hands-on diagnosis or implementation, <a href="https://redquadrant.com/service-change/">explore RedQuadrant's service pressure diagnostic, joined-up service redesign, and AI-enabled service change</a>. Learning and implementation responsibilities are agreed explicitly.</p></section>'''
    main = '<main id="main-content"><article class="strategy-academy"><p><a href="/programmes/">Programmes</a></p><h1>' + title + '</h1><p class="strategy-lead">' + lead + '</p>' + body + '</article></main>'
    page, replacements = re.subn(r'<main\b[^>]*>.*?</main>', lambda _: main, template, count=1, flags=re.S)
    if replacements != 1:
        raise ValueError('Expected one main element in the existing Academy shell')
    page = re.sub(r'<title>.*?</title>', '<title>' + title + ' | The Public Service Transformation Academy</title>', page, count=1, flags=re.S)
    page = re.sub(r'<meta[^>]+(?:name|property)="(?:description|og:title|og:description|og:url|twitter:title|twitter:description)"[^>]*>', '', page)
    page = re.sub(r'<link[^>]+rel="canonical"[^>]*>', '', page)
    page = re.sub(r'<script type="application/ld\+json">.*?</script>', '', page, flags=re.S)
    canonical = domain + '/' + slug + '/'
    metadata = '<meta name="description" content="' + escape(lead, quote=True) + '"><meta property="og:title" content="' + title + '"><meta property="og:description" content="' + escape(lead, quote=True) + '"><meta property="og:url" content="' + canonical + '"><link rel="canonical" href="' + canonical + '">'
    page = page.replace('</head>', metadata + '</head>', 1)
    destination = root / slug / 'index.html'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page, encoding='utf-8')

    marker = 'PSTA_SERVICE_CHANGE_20260919'
    chooser = '''<!-- PSTA_SERVICE_CHANGE_20260919 --><section class="section"><div class="shell"><h2>Develop a team through live service change</h2><p>A twelve-week commissioned programme around one real change, with workplace practice, peer challenge, sponsor reviews, and evidence of what changed. Normally for a team of eight to twelve; design and fee are agreed with the sponsor.</p><p><a class="button" href="/learning-and-capability/">Explore the learning and capability partnership</a></p></div></section>'''
    programmes = root / 'programmes/index.html'
    programmes.write_text(insert_once(programmes.read_text(encoding='utf-8'), marker, chooser), encoding='utf-8')
    academy = root / 'programmes/national-commissioning-academy/index.html'
    text = academy.read_text(encoding='utf-8')
    # Correct current recruitment copy only; historical articles and URLs stay intact.
    text = text.replace('September 2026 cohort', 'November 2026 cohort').replace('returns in September 2026', 'returns in November 2026')
    text = text.replace('September 2026 to February 2027', 'November 2026 to May 2027').replace('November 2026 to February 2027', 'November 2026 to May 2027')
    note = '''<!-- PSTA_SERVICE_CHANGE_20260919 --><section class="section"><div class="shell"><h2>Bring a team and a live commissioning challenge</h2><p>Discuss sponsored-team places on the National Commissioning Academy, or an in-house programme, with David Mason. Confirm the timetable, places, fees, and sponsor commitment before booking.</p><p>For a separately commissioned twelve-week programme combining workplace practice and sponsor review, see our <a href="/learning-and-capability/">learning and capability partnership</a>.</p></div></section>'''
    academy.write_text(insert_once(text, marker, note), encoding='utf-8')
    sitemap = root / 'sitemap.xml'
    text = sitemap.read_text(encoding='utf-8')
    if '<loc>' + canonical + '</loc>' not in text:
        text = text.replace('</urlset>', '<url><loc>' + canonical + '</loc></url>\n</urlset>')
        sitemap.write_text(text, encoding='utf-8')

    # Block publication if the offer or its two entry points are missing.
    assert destination.is_file()
    assert 'mailto:david.mason@publicservicetransformation.org' in page
    assert '/learning-and-capability/' in programmes.read_text(encoding='utf-8')
    assert '/learning-and-capability/' in academy.read_text(encoding='utf-8')
    assert 'November 2026 to May 2027' in academy.read_text(encoding='utf-8')
    assert len(re.findall(r'<h1(?:\s|>)', page)) == 1
    assert '<link rel="canonical" href="' + canonical + '">' in page
    print('Published service-change offer: page, programme entry, Academy team invitation, and sitemap')
