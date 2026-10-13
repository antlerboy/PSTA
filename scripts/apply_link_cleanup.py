"""Publish current offer routes and honest retirement pages; restore useful legacy paths."""
from pathlib import Path
import html,json,re,sys
from urllib.parse import urlsplit,unquote
root=Path(sys.argv[1]);domain='https://www.publicservicetransformation.org'
template=(root/'programmes/place-based-academies/index.html').read_text()
published=[]
def page(slug,title,lead,body):
    s=template
    s=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+' | PSTA</title>',s,count=1)
    s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+html.escape(lead,quote=True)+'">',s,count=1)
    s=re.sub(r'<link rel="canonical" href="[^"]*">','<link rel="canonical" href="'+domain+'/'+slug+'/">',s,count=1)
    s=re.sub(r'<meta property="og:(title|description|url)" content="[^"]*">',lambda m:'<meta property="og:'+m[1]+'" content="'+html.escape({'title':title,'description':lead,'url':domain+'/'+slug+'/'}[m[1]],quote=True)+'">',s)
    s=re.sub(r'<script type="application/ld\+json">.*?</script>','',s,flags=re.S)
    main='<main id="main-content" class="site-main"><section class="page-hero"><div class="shell"><p><a href="/">PSTA</a> / <a href="/offers/">Programmes and tools</a></p><h1>'+html.escape(title)+'</h1><p class="lede">'+html.escape(lead)+'</p></div></section><section class="section"><div class="shell">'+body+'</div></section></main>'
    s=re.sub(r'<main\b[^>]*>.*?</main>',lambda _:main,s,count=1,flags=re.S)
    s=s.replace('</head>','<style>.offer-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,270px),1fr));gap:20px;margin:24px 0}.offer-card{border:1px solid #dedbd6;border-top:4px solid #99141b;border-radius:6px;padding:24px;background:white}.offer-card h3{margin-top:0;font-size:23px}.offer-card p{line-height:1.6}.route-note{border-left:4px solid #b98736;padding:16px 22px;background:#f7f5f2;margin:24px 0}</style></head>')
    p=root/slug/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s);published.append(slug)
def cards(items):
    return '<div class="offer-grid">'+''.join('<article class="offer-card"><h3><a href="'+u+'">'+t+'</a></h3><p>'+d+'</p><a href="'+u+'">Explore '+label+' →</a></article>' for t,u,d,label in items)+'</div>'

programmes=[
('National Commissioning Academy','/programmes/national-commissioning-academy/','Bring a live commissioning challenge and develop your practice with people from across public services. See the programme page for the current cohort, commitment, and fees.','the Academy'),
('Commissioning: a ten-step introduction','/programmes/commissioning-ten-step-introduction/','Understand the commissioning task, work through its practical steps, and apply them to your own context.','the introduction'),
('Contract management development','/programmes/contract-management-development/','Develop the judgement, relationships, and practical disciplines needed to manage public-service contracts.','contract management'),
('Commissioning and innovation','/programmes/commissioning-and-innovation/','An experiential programme for working across complex systems and developing different ways forward.','the programme'),
('Leading Transformation','/programmes/leading-transformation/','A broad programme of recorded modules and additional material, with options for supported application to live work.','Leading Transformation'),
('Commissioning simulation','/programmes/commissioning-simulation/','Practise decisions and explore their consequences in a facilitated simulation.','the simulation'),
('Learning and capability partnership','/learning-and-capability/','Develop a team through a live change challenge, connecting learning, workplace practice, and sponsor review.','the partnership'),
('LGR and devolution','/lgr-academy/','Tailored development for the people making reorganisation and cross-place working happen. See also the <a href="/devolution-academy/">Devolution Academy</a>.','LGR development'),
]
toolitems=[
('smartCompass','/tools/smart-compass/','A prototype tool to help you explore your system and community-powered outcomes.','smartCompass'),
('Commissioning Compass','/tools/commissioning-compass/','Systems assessment for change, with a route to the original tool.','the Compass'),
('Compass v2.0 beta','/tools/compass-v2-beta/','Read and contribute to the emerging version of the systems-change tool.','the beta'),
('Commissioning health check','/programmes/commissioning-health-check/','Review your organisation’s commissioning practice and discuss useful next steps. Confirm scope, availability, and any fee with us.','the health check'),
]
page('offers','PSTA programmes, tools, and practical support',
     'Choose a development programme, try a practical tool, or talk with us about the change you need to make.',
     '<p>These are current routes into the PSTA’s work. Follow each programme for its format, fees, and booking arrangements, or tell us about your team and live challenge.</p><h2>Develop your practice and your team</h2>'+cards(programmes)+'<h2>Tools and a place to start</h2>'+cards(toolitems)+
     '<h2>Talk about what you need</h2><p><a class="button" href="mailto:david.mason@publicservicetransformation.org?subject=PSTA%20programme%20enquiry">Discuss a programme with David Mason</a> · <a href="/contact/">Other enquiries</a></p><p><a href="https://eepurl.com/hSKY5n">Get PSTA news, events, and offers by email</a>.</p>')
page('programmes/systems-thinking-apprenticeship','The apprenticeship has ended',
     'The PSTA apprenticeship offer is no longer available.',
     '<p>The apprenticeship and its recruitment webinars have ended. This page is retained for people arriving through an old invitation or prospectus.</p><h2>Other ways to develop your practice</h2>'+cards([
     ('Systems Leadership Academy','/systems-leadership-academy/','Develop your ability to act with others on issues that cross organisational boundaries.','systems leadership'),
     ('Current programmes and tools','/offers/','Explore commissioning, transformation, practical tools, and bespoke team development.','current options')])+ '<p>For a question about a past cohort or your records, <a href="/contact/">contact the PSTA</a>.</p>')
page('resources/retired-jamboard','This Jamboard has been retired',
     'The former Jamboard workspace is no longer available.',
     '<p>This link was used for a past workshop or learning activity. It no longer opens a live board. If you need a particular output, contact us with the event name or the short link you followed; we can check whether a saved copy is available.</p><h2>Continue the work</h2>'+cards([
     ('Facilitation and workshop design','https://antlerboy.com/library/facilitation-and-systems-consulting/','Reading lists, methods, and guides for working with groups and systems.','the collection'),
     ('Learning through a live challenge','/learning-and-capability/','Supported team development connected to real public-service work.','the partnership')])+'<p><a href="/contact/">Ask about a workshop output</a> · <a href="/offers/">All current programmes and tools</a></p>')
for slug,title,lead in [
    ('resources/past-workshops','This workshop invitation has ended','The old poll, survey invitation, or session link has been retired.'),
    ('events/past-events','This event has ended','The old event invitation or registration link has been retired.')]:
    page(slug,title,lead,'<p>For materials from a particular session, contact us with its title or the short link you followed. This page does not collect survey responses or register you for an event.</p><h2>What is available now?</h2>'+cards([
       ('Current programmes and tools','/offers/','Find a learning programme, try a tool, or discuss a tailored programme for your team.','current options'),
       ('Public work library','https://antlerboy.com/library/','Public talks, writing, teaching, and practical resources.','the library')])+'<p><a href="/contact/">Ask about past materials</a> · <a href="https://eepurl.com/hSKY5n">Get news of future events</a></p>')
page('events/goldratt-july-2026','A different look at systems thinking — July 2026 webinar',
     'The PSTA webinar with Goldratt UK took place on 2 July 2026. Registration has closed.',
     '<p>This page preserves the route from the original webinar invitation. To ask about a recording or presentation materials, please <a href="mailto:info@publicservicetransformation.org?subject=Goldratt%20webinar%202%20July%202026%20materials">contact the PSTA</a>.</p><h2>Related resources and development</h2><ul><li><a href="/tools/commissioning-compass/">Commissioning Compass: systems assessment for change</a></li><li><a href="/systems-leadership-academy/">Systems Leadership Academy</a></li><li><a href="/assets/documents/commissioning-is-an-approach-to-transformation.pdf">Commissioning is an approach to transformation — the original 2019 paper</a></li><li><a href="/offers/">Current PSTA programmes and tools</a></li></ul>')

# These two legacy partner stubs contain no profile content. Give readers a
# maintained destination rather than publishing an empty, malformed page.
for slug in ['partners/apace','partners/fractal-consulting']:
    page(slug,'PSTA partners','Find our current partners and ways to work with the PSTA.',
         '<p>This historical partner address is retained for older links. <a href="/partners/">Browse the current partner information</a>, or <a href="/contact/">contact us about working together</a>.</p>')

routes=json.loads((Path(__file__).parents[1]/'content/link-cleanup-routes.json').read_text())
for old,new in routes['legacy'].items():
    p=root/old.strip('/')/'index.html'
    if p.exists():continue
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text('<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Resource moved | PSTA</title><meta name="description" content="Find the current page for this PSTA resource."><meta name="robots" content="noindex,follow"><link rel="canonical" href="'+html.escape(new,quote=True)+'"><meta http-equiv="refresh" content="0;url='+html.escape(new,quote=True)+'"></head><body><main id="main-content"><h1>This resource has moved</h1><p><a href="'+html.escape(new,quote=True)+'">Continue to the resource</a></p></main></body></html>')

# Keep launch buttons direct before any promotional short URL is migrated.
for p in root.rglob('*.html'):
    s=p.read_text()
    for old,new in routes['direct_tools'].items():s=s.replace(old,html.escape(new,quote=True))
    s=s.replace('https://link.redquadrant.com/m/PSTAOffers','/offers/')
    # Late partner generators reintroduced historical prefixes; repair the same
    # known production paths already handled by the main launch pass.
    s=s.replace('="/PSTA/','="/').replace('http://eepurl.com','https://eepurl.com')
    s=s.replace('/assets/partner-logos/redquadrant.svg','/assets/partner-logos/redquadrant.png')
    s=s.replace('/assets/img/favicon.png','/assets/img/psta-logo-white.png').replace('/assets/img/psta-logo-official.jpg','/assets/img/psta-logo-web.jpg').replace('/assets/img/partners/redquadrant-logo.jpg','/assets/partner-logos/redquadrant.svg')
    if 'href="#main-content"' in s and 'id="main-content"' not in s:s=re.sub(r'<main\b[^>]*>','<main id="main-content">',s,count=1)
    if '<main' not in s and 'href="#main-content"' in s:
        s=s.replace('<a class="skip-link" href="#main-content">Skip to content</a>', '<a class="skip-link" href="#main-content">Skip to content</a><main id="main-content">',1)
        s=s.replace('<footer', '</main><footer',1)
    p.write_text(s)
sitemap=root/'sitemap.xml';s=sitemap.read_text()
for slug in published:
    url=domain+'/'+slug+'/'
    if '<loc>'+url+'</loc>' not in s:s=s.replace('</urlset>','<url><loc>'+url+'</loc></url></urlset>')
sitemap.write_text(s)
print('Published offers, apprenticeship closure, retired resources, and original paper routes')
