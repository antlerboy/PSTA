from pathlib import Path
import re,html,json,sys
r=Path(sys.argv[1]);src=Path(__file__).resolve().parents[1]
prices=json.loads((src/'content/guide-prices.json').read_text())
p=r/'programmes/national-commissioning-academy/index.html';s=p.read_text()
team='''<section class="section"><div class="shell"><h2>Bring a team and a live challenge</h2><p>A small cross-boundary team can use the Academy to work on a commissioning or transformation problem while developing its practice. A useful team might include a commissioning lead, someone responsible for delivery, and a colleague or partner who sees another part of the system.</p><p>Identify a senior sponsor who can help frame the challenge, protect time for application, and support action on the resulting 100-day plan. Discuss the intended outcomes, citizen experience, relationships, constraints, and decisions that the team needs to work through.</p><h3>Team pricing</h3><p>The individual fee is £2,490 excluding VAT. The 15% group discount for three or more places gives a three-person team price of <strong>£6,349.50 excluding VAT</strong>, or <strong>£10,582.50 excluding VAT for five</strong>.</p><p><a class="button button-gold" href="mailto:david.mason@publicservicetransformation.org?subject=20-minute%20Academy%20team-fit%20conversation">Book a 20-minute team-fit conversation</a></p><p>Tell David your organisation, the live challenge, likely colleagues, sponsor, and preferred time for a conversation. We will confirm fit, the programme commitment, and purchasing arrangements before you book.</p></div></section>'''
s=s.replace('</main>',team+'</main>');p.write_text(s)
for slug,(price,scope) in prices.items():
 p=r/slug/'index.html';s=p.read_text()
 section='<section class="section guide-fee"><div class="shell"><h2>Guide price and scope</h2><p><strong>'+price+' excluding VAT.</strong> '+scope+'</p><p>These are indicative starting prices for the scope described. We agree a written fixed-fee proposal before booking. Venue, travel, accommodation, additional coaching, and external assessment fees are separate where required.</p><p><a class="button button-gold" href="mailto:david.mason@publicservicetransformation.org?subject='+slug+'">Ask for a proposal</a></p></div></section>'
 s=s.replace('</main>',section+'</main>');p.write_text(s)
for p in r.rglob('*.html'):
 s=p.read_text();s=s.replace('In-house','Bespoke').replace('in-house','bespoke').replace('10-step','ten-step')
 s=s.replace('November 2026 to February 2027','starting November 2026').replace('November 2026–February 2027','starting November 2026').replace('The main programme runs through to February 2027.','David will confirm the full programme calendar before booking.')
 # Restore historical URL paths while changing visible terminology.
 s=s.replace('/bespoke/','/in-house/')
 s=re.sub(r'<section[^>]*>\s*(?:<div[^>]*>\s*)?<h2>What moved from the former site</h2>.*?</section>','',s,flags=re.S)
 s=s.replace('<a href="/insights/">Insights</a>','<a href="/news/">News</a><a href="/insights/">Insights</a>') if '<a href="/news/">News</a>' not in s.split('</header>')[0] else s
 s=s.replace('No open cohort date or fixed fee is currently advertised here; enquire about a bespoke or partnership programme.','Enquire about a bespoke or partnership programme; a guide scope and fee are set out below.')
 s=s.replace('Duration, dates, faculty, and fee are agreed for the cohort.','The design and final fee are agreed for the cohort.')
 if 'class="people-grid"' in s and '<h3>Terry Rich</h3>' not in s:
  s=s.replace('<div class="people-grid">','<div class="people-grid"><article class="person-card"><div class="person-mark" aria-hidden="true">TR</div><div><h3>Terry Rich</h3><p class="eyebrow">Chair</p><p>Terry chairs the PSTA board, supporting its public purpose, governance, and development.</p></div></article>',1)
 for name,file in [('E3M','e3m'),('Nesta','nesta'),('The Social Innovation Partnership','tsip'),('RedQuadrant','redquadrant'),('Basis','basis'),('LocalGov Digital','localgov-digital'),('Browne Jacobson','browne-jacobson')]:
  matches=list((r/'assets/partner-logos').glob(file+'.*'))
  if matches:s=s.replace('<span class="partner-logo-fallback">'+name+'</span>','<img src="/assets/partner-logos/'+matches[0].name+'" alt="'+name+'" loading="lazy">')
 s=s.replace('Try smartCompass','Use smartCompass').replace('Try SmartCompass','Use SmartCompass')
 s=s.replace('</head>','<style>.site-footer{padding:32px 0 0}.footer-grid{gap:22px}.site-footer h2{font-size:17px}.site-footer p,.site-footer a{font-size:14px}.footer-logo img{max-width:170px;max-height:70px;object-fit:contain}.footer-legal{font-size:12px;padding:18px 24px}.guide-fee{border-top:3px solid #b98736}.partner-logo-wrap img{width:170px;max-height:75px;object-fit:contain}@media(max-width:700px){.footer-grid{grid-template-columns:1fr 1fr}.guide-fee .shell{padding-inline:20px}}</style></head>')
 p.write_text(s)
# Useful permanent aliases for readers arriving through old blog links.
for slug in ['blog','blogs']:
 p=r/slug/'index.html';p.parent.mkdir(exist_ok=True);p.write_text('<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PSTA news and practice</title><meta name="robots" content="noindex,follow"><link rel="canonical" href="https://www.publicservicetransformation.org/news/"><meta http-equiv="refresh" content="0;url=/news/"></head><body><main><h1>PSTA news and practice</h1><a href="/news/">Read our news and practice notes</a></main></body></html>')
print('Added twelve scoped guide prices, Terry Rich, partner logos, news navigation, and compact footers')
