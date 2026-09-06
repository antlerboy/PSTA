"""Apply the authorised 6 September 2026 editorial and feedback updates."""
from pathlib import Path
import html
import json
import re
import sys
import shutil

root = Path(sys.argv[1])
source = Path(__file__).resolve().parents[1]
# Retired profiles must not survive reconstruction of the historical bundle.
for retired in ('partners/apace', 'partners/fractal-consulting'):
    shutil.rmtree(root / retired, ignore_errors=True)
modules = json.loads((source / 'content/curriculum-2026.json').read_text())
css = '''.iteration-secret-link{position:fixed!important;right:0!important;bottom:0!important;width:44px!important;height:44px!important;z-index:1000;background:transparent!important;border:0!important;box-shadow:none!important;border-radius:0!important;opacity:1!important}.iteration-secret-link::after{content:"";position:absolute;right:7px;bottom:7px;width:6px;height:6px;border-radius:50%;background:white;box-shadow:0 0 0 1px #777}.iteration-secret-link:focus-visible{outline:3px solid #ff8000!important;outline-offset:-3px}.curriculum-2026{padding-left:1.6rem;max-width:58rem}.curriculum-2026 li{padding:.5rem 0 1rem .5rem;border-bottom:1px solid #ddd}.curriculum-2026 h3{margin-bottom:.3rem}.curriculum-world{font-size:1rem;font-weight:700}.curriculum-2026 p{margin:.35rem 0}'''
dot = '<a class="iteration-secret-link" href="https://github.com/antlerboy/PSTA/issues/2" aria-label="Open the PSTA website updates" title="Website updates"></a>'

for page in root.rglob('*.html'):
    text = page.read_text()
    if 'WEB_ESTATE_REVIEW_20260906' in text:
        continue
    text = text.replace('an bespoke', 'a bespoke').replace('An bespoke', 'A bespoke')
    text = text.replace('starting November 2026', 'November 2026 to May 2027')
    text = text.replace('Starting November 2026', 'November 2026 to May 2027')
    if '</body>' not in text:
        continue
    # Existing dot is retained where present; generated pages receive it too.
    if not re.search(r'<a\b[^>]*class=[\'"][^\'"]*iteration-secret-link', text):
        text = text.replace('</body>', dot + '\n</body>')
    text = text.replace('</head>', '<!-- WEB_ESTATE_REVIEW_20260906 --><style>' + css + '</style></head>')
    route = page.relative_to(root).as_posix()
    if route == 'contribute/index.html':
        text = re.sub(r'<h2 id="after-the-github-repository-is-live">.*?(?=<h2 id="editorial-rule">)', '', text, flags=re.S)
    if route == 'tools/commissioning-compass/index.html':
        text = text.replace('<h2 id="use-it-with-a-group">', '<p>The Commissioning Compass is hosted on Teachable and can be accessed with a free Teachable account.</p><h2 id="use-it-with-a-group">')
        old = '<a class="button button-gold" href="/contact/">Discuss this with us</a><a class="text-link" href="https://link.redquadrant.com/commissioningcompass" target="_blank" rel="noopener noreferrer">Use the Commissioning Compass →</a>'
        new = '<a class="button button-gold" href="https://link.redquadrant.com/commissioningcompass" target="_blank" rel="noopener noreferrer">Use the Commissioning Compass →</a><a class="text-link" href="/contact/">Discuss this with us</a>'
        text = text.replace(old, new)
    if route == 'tools/adult-social-care-options-appraisal/index.html':
        text = text.replace('The source from which the Compass grew', 'The source from which our Commissioning Compass tool grew')
        text = text.replace('<h2 id="use-it-to">Use it to</h2>\n<ul>', '<h2 id="use-it-to">Use it to</h2>\n<ul>\n<li>Apply a version of the tool tailored to adult social care commissioners.</li>')
    if route == 'community/index.html':
        match = re.search(r'<h2 id="current-routes-in">.*?(?=<h3 id="newsletter-and-open-events">)', text, re.S)
        if match:
            section = match.group(0)
            text = text.replace(section, '').replace('<h2 id="alumni-contributions">', section + '<h2 id="alumni-contributions">')
    if route == 'programmes/leading-transformation/index.html':
        items = ''.join('<li><h3>' + html.escape(m['title']) + '</h3><p class="curriculum-world">' + html.escape(m['worldLabel']) + '</p><p>' + html.escape(m['focus']) + '</p></li>' for m in modules)
        curriculum = '<section id="curriculum"><h2>The 2026 learning route</h2><p>The revised 24-module curriculum moves across five perspectives: leadership and political life, citizens, services, management, and learning and change. These perspectives connect throughout the programme.</p><ol class="curriculum-2026">' + items + '</ol></section>'
        text = re.sub(r'<section id="curriculum">.*?</section>', curriculum, text, count=1, flags=re.S)
        learning = '<section><h2>How the learning works</h2><p>Bring a live transformation challenge into the programme. Use teaching, rehearsal, reflection, and application to connect the repertoire with decisions and work in your organisation. Live practice starts in module 3 and service prototyping in module 12. The final simulation requires a substantial delivery block and leads into a hundred-day plan.</p><p>The Five Core Practices recur throughout. The Four Dynamics are introduced in module 4 and applied fully to organisation design in module 18. Optional depth includes Seven Ways, Resource Optimisation, Patterns of Strategy, behavioural insight, Positive Deviance, Appreciative Inquiry, lean and operational tools, commissioning, and Breaking the Shell.</p><p>Bespoke programmes can combine supported study, facilitated discussion, webinars, action learning, coaching, and simulation. The 2026 curriculum develops the established programme. Ask about current materials and agree the mix, support, dates, and time commitment for your cohort before booking.</p></section>'
        text = re.sub(r'<section><h2>How the learning works</h2>.*?</section>', learning, text, count=1, flags=re.S)
        text = re.sub(r'<section class="section guide-fee">.*?</section>', '', text, flags=re.S)
        text = text.replace('a tailored organisational programme', 'a bespoke organisational programme')
        text = text.replace('Develop a broad repertoire and apply it to live transformation work.', 'Develop and apply your transformation practice through the revised 2026 curriculum, with 24 modules across five perspectives.')
    page.write_text(text)

print('Applied 2026 curriculum, public-copy corrections, and feedback controls on all served HTML pages')
