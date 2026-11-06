#!/usr/bin/env python3
"""Publish source-preserving Compass workspaces and practical community routes."""
from pathlib import Path
from urllib.parse import quote
import html
import json
import re
import shutil
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
repo = Path(__file__).resolve().parents[1]
domain = 'https://www.publicservicetransformation.org'
subprocess.run([sys.executable, str(repo / 'scripts/check_programme_record.py')], check=True)
template = (root / 'programmes/place-based-academies/index.html').read_text(encoding='utf-8')
published = []
e = html.escape


def append_section(path, marker, addition):
    text = path.read_text(encoding='utf-8')
    wrapped = '<!-- ' + marker + ' -->' + addition + '<!-- /' + marker + ' -->'
    pattern = r'<!-- ' + re.escape(marker) + r' -->.*?<!-- /' + re.escape(marker) + r' -->'
    if re.search(pattern, text, re.S):
        text = re.sub(pattern, lambda _: wrapped, text, count=1, flags=re.S)
    else:
        # Also recognise the first local assembly, before markers were added.
        text = text.replace(addition, '').replace('</main>', wrapped + '</main>', 1)
    path.write_text(text, encoding='utf-8')


def page(route, title, lead, body, *, private_input=False, extra_head=''):
    text = template
    url = domain + '/' + route.strip('/') + '/'
    text = re.sub(r'<title>.*?</title>', '<title>' + e(title) + ' | the PSTA</title>', text, count=1)
    text = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + e(lead, quote=True) + '">', text, count=1)
    text = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="' + url + '">', text, count=1)
    text = re.sub(r'<meta property="og:(title|description|url)" content="[^"]*">', lambda m: '<meta property="og:' + m[1] + '" content="' + e({'title': title, 'description': lead, 'url': url}[m[1]], quote=True) + '">', text)
    text = re.sub(r'<script type="application/ld\+json">.*?</script>', '', text, flags=re.S)
    text = re.sub(r'<script\b[^>]*src="[^"]*easter-eggs\.js[^"]*"[^>]*>\s*</script>', '', text, flags=re.S)
    markup = '<main id="main-content" class="site-main"><section class="page-hero"><div class="shell"><p><a href="/">The PSTA</a> / <a href="/tools/compass/">Compass and practice</a></p><h1>' + e(title) + '</h1><p class="lede">' + e(lead) + '</p></div></section><section class="section"><div class="shell compass-workspace">' + body + '</div></section></main>'
    text = re.sub(r'<main\b[^>]*>.*?</main>', lambda _: markup, text, count=1, flags=re.S)
    if private_input:
        # These pages have no analytics request or third-party script. Form values
        # never enter URLs; an email draft only opens after an explicit action.
        text = re.sub(r'<script\b[^>]*src="https?://[^"]*"[^>]*>\s*</script>', '', text, flags=re.S)
    text = text.replace('</head>', '<link rel="stylesheet" href="/assets/compass/compass.css?v=20261105">' + extra_head + '</head>')
    destination = root / route.strip('/') / 'index.html'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding='utf-8')
    published.append(route.strip('/'))


for folder in ['assets/compass', 'assets/practice']:
    shutil.copytree(repo / folder, root / folder, dirs_exist_ok=True)
shutil.copy2(repo / 'assets/js/practice-intake.js', root / 'assets/js/practice-intake.js')
shutil.copytree(repo / 'content/compass/sources', root / 'assets/compass/sources', dirs_exist_ok=True)

tools = []
default_routes = {
    'compass-v2-beta': 'tools/compass-v2-beta/workspace',
    'smart-compass-local': 'tools/smart-compass/workspace',
    'commissioning-compass': 'tools/commissioning-compass/workspace',
    'adult-social-care-options-appraisal': 'tools/adult-social-care-options-appraisal/workspace',
}
for source in sorted((repo / 'content/compass').glob('*.json')):
    tool = json.loads(source.read_text(encoding='utf-8'))
    if 'sections' not in tool:
        continue
    route = tool.get('route') or default_routes[tool['id']]
    assert all(q.get('id') and q.get('prompt') for s in tool['sections'] for q in s['questions'])
    payload = json.dumps(tool, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    source_link = tool['source'].get('localText', tool['source']['url'])
    body = '<p class="compass-source-note"><strong>' + e(tool['status']) + '.</strong> ' + e(tool['introduction']) + '</p><p class="compass-privacy"><strong>Your answers stay in this page until you choose what to keep.</strong> Save on this device to restore them here, or download an editable copy. This workspace does not submit answers to the PSTA or an AI service, and has no analytics script. Device storage and downloaded files can be read by someone with access to them. Use short role labels and leave out confidential or identifying case details.</p><noscript><p>Enable JavaScript to use the workspace, or <a href="' + e(source_link, quote=True) + '">read the source questions</a> and keep your notes separately.</p></noscript><div id="compass-app"></div><script id="compass-tool-data" type="application/json">' + payload + '</script><script defer src="/assets/compass/compass.js?v=20261106-visitor"></script>'
    page(route, tool['title'], tool['description'], body, private_input=True)
    (root / 'assets/compass' / source.name).write_text(json.dumps(tool, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tools.append((tool, '/' + route + '/'))

order = {'commissioning-compass': 0, 'smart-compass-local': 1, 'compass-v2-beta': 2, 'adult-social-care-options-appraisal': 3}
tools.sort(key=lambda entry: order.get(entry[0]['id'], 99))
by_id = {tool['id']: (tool, route) for tool, route in tools}
cards = ''.join('<article class="offer-card"><p class="eyebrow">' + e(tool['status']) + '</p><h2><a href="' + route + '">' + e(tool['title']) + '</a></h2><p>' + e(tool['description']) + '</p><p>' + str(sum(len(s['questions']) for s in tool['sections'])) + ' prompts · no account needed</p><a class="button button-gold" href="' + route + '">Open the workspace</a></article>' for tool, route in tools)
original_note = '' if 'commissioning-compass' in by_id else '<h2>The original Commissioning Compass</h2><p>The original includes eight aspects, scoring sheets, constraints and enablers, case material, and approaches to commissioning. <a href="/tools/commissioning-compass/">See the original tool and its current access route</a>.</p>'
page('tools/compass', 'Commissioning Compass assessments', 'Choose an edition, record your answers, and review what changes.', '<p>Use these assessments to record answers and evidence, compare colleagues’ views, and keep actions and reviews together. You can save a copy on your device, download it to reopen later, or print your notes. Each edition identifies its source and version.</p><div class="offer-grid">' + cards + '</div>' + original_note + '<h2>Compare answers with colleagues</h2><p>Ask colleagues to record their answers separately. Discuss where they disagree, what evidence each person has, and whose views are missing. Record what you’ll change, who can act, and when you’ll check the result.</p><p><a href="/community/case-clinics/">Prepare a case clinic with colleagues</a> · <a href="/enquire/">Discuss supported use with the PSTA</a></p>')

beta_source = (repo / 'content/compass/sources/compass-v2-beta-2026-06-13.txt').read_text(encoding='utf-8')
page('tools/compass-v2-beta/source', 'Compass v2.0 beta: the source text', 'Benjamin P Taylor’s 13 June 2026 working paper on commissioning as collective system learning.', '<p>The text below preserves the published beta, including its working language and references. It does not establish whether the proposals have been tested.</p><p><a href="/tools/compass-v2-beta/workspace/">Use the matrix in a workspace</a> · <a href="/assets/compass/sources/compass-v2-beta-2026-06-13.txt">Download the source text</a></p><pre style="white-space:pre-wrap;font:inherit;overflow-wrap:anywhere">' + e(beta_source) + '</pre>')

page('tools/compass-v2-beta', 'Compass v2.0 beta', 'Answer the forty questions in the beta matrix, compare views, and record actions.', '<p>The beta asks people to examine how their decisions, relationships, resources, and arrangements affect life in a place. Its matrix contains eight lenses and five moves, including questions about who decides and what people learn from action.</p><p>The workspace reproduces all forty matrix prompts. You can record colleagues’ answers separately, add evidence, agree actions, and save reviews. It doesn’t calculate a maturity grade.</p><p><a class="button button-gold" href="/tools/compass-v2-beta/workspace/">Use the beta workspace</a> <a class="text-link" href="/tools/compass-v2-beta/source/">Read the complete source</a></p><h2>Report a problem with the questions</h2><p>Tell us which question you used, what you were trying to understand, and where it helped or missed something. Leave out identifying case details in a first enquiry.</p><p><a href="/enquire/">Share a question or correction</a> · <a href="/tools/compass/">Compare the editions</a></p>')

page('tools/smart-compass', 'smartCompass', 'Answer sixteen questions about a place, service, or issue you know.', '<h2>Save and review your answers</h2><p>This edition contains the original two context prompts and sixteen reflective questions. You can record answers, compare colleagues’ views, and review actions. You don’t need an account or email address.</p><p><a class="button button-gold" href="/tools/smart-compass/workspace/">Use smartCompass</a></p><h2>Use your answers with AI</h2><p>Download the PSTA’s original smartCompass prompt with your answers from the workspace. Check what you’re sharing, then use the file in your authorised AI account.</p><p>The workspace creates a file. It doesn’t send your answers, generate AI analysis, or email a report.</p><p><a href="/tools/compass/">Compare the Compass editions</a></p>')

for tool_id, landing in [('commissioning-compass', 'tools/commissioning-compass'), ('adult-social-care-options-appraisal', 'tools/adult-social-care-options-appraisal')]:
    if tool_id not in by_id:
        continue
    tool, route = by_id[tool_id]
    course = tool.get('courseArchive')
    course_note = '<h2>Reading and resources</h2><p><a href="/tools/commissioning-compass/reading/">Read the teaching material</a> · <a href="' + e(course['url'], quote=True) + '">Original course</a></p>' if course else ''
    page(landing, tool['title'], tool['description'], '<p>' + e(tool['introduction']) + '</p><p><a class="button button-gold" href="' + route + '">Use the assessment</a> <a class="text-link" href="/tools/compass/">Compare editions</a></p><h2>Source and use</h2><p>' + e(tool['source']['note']) + '</p><p><a href="' + e(tool['source'].get('localText', tool['source']['url']), quote=True) + '">Read the preserved source</a></p>' + course_note)

community_body = '<p>Bring a decision you need to make, a change you can’t get started, or a problem that keeps returning. Describe what you’ve observed, what you think is causing it, and what you need help with.</p><h2>Six sessions over three months</h2><p>The host guide sets out six 90-minute sessions over about three months. The group works on six cases, tries actions between sessions, and compares what happened with what people expected. Each case-holder decides what to continue, change, or stop.</p><p>Use or adapt the guide with colleagues. To arrange a group with the PSTA, agree the convenor, participants, dates, access needs, and any fee before joining.</p><h2>Prepare and host</h2><ul><li><a href="/assets/practice/2026-11-05 the PSTA case clinic participant brief v0.01 BT.txt" download="2026-11-05 the PSTA case clinic participant brief v0.01 BT.txt">2026-11-05 the PSTA case clinic participant brief v0.01 BT.txt</a></li><li><a href="/assets/practice/2026-11-05 the PSTA case clinic host guide v0.01 BT.txt" download="2026-11-05 the PSTA case clinic host guide v0.01 BT.txt">2026-11-05 the PSTA case clinic host guide v0.01 BT.txt</a></li><li><a href="/assets/practice/2026-11-05 the PSTA practice case record v0.01 BT.txt" download="2026-11-05 the PSTA practice case record v0.01 BT.txt">2026-11-05 the PSTA practice case record v0.01 BT.txt</a></li><li><a href="/tools/compass/">Compass workspaces for answers, actions, and reviews</a></li></ul><h2>Working agreement</h2><p>No sales pitches. No identifiable material without permission. Ask the case-holder what help they need. Record where people disagree and why. Question the method and how it is being used. Taking part doesn’t give permission to publish. Check the record and get agreement before publishing a case, diagram, or correction to a tool.</p><p><a class="button button-gold" href="/community/bring-a-case/">Propose a case or express interest</a></p>'
page('community/case-clinics', 'Public service case clinics', 'Prepare six sessions for a small group working on cases from their own organisations.', community_body)

intake_style = '<style>.practice-intake{max-width:52rem}.practice-intake label{display:block;font-weight:650;margin:1.2rem 0}.practice-intake input,.practice-intake textarea,.practice-intake select{display:block;width:100%;font:inherit;padding:.7rem;border:1px solid #777;margin-top:.4rem;box-sizing:border-box}.practice-intake textarea{min-height:7rem}.intake-preview{white-space:pre-wrap;border-left:3px solid #99141b;padding:1rem;overflow-wrap:anywhere;background:#f7f4ee}.offer-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:1.3rem}.offer-card{padding:1.3rem;border:1px solid #c5beb4;border-top:4px solid #99141b;border-radius:5px}.offer-card h2{font-size:1.4rem}</style>'


def intake(route, title, lead, recipient, heading, prompts):
    form = '<p>Your answers stay on this page. The button prepares an email in your own email app; it does not send one. Download the text if you prefer to paste it into a message. Leave out confidential or identifying case details.</p><form class="practice-intake" data-practice-intake data-recipient="' + recipient + '" data-heading="' + e(heading, quote=True) + '">'
    for prompt, multiline in prompts:
        attrs = ' data-prompt="' + e(prompt, quote=True) + '" maxlength="5000"'
        form += '<label>' + e(prompt) + ('<textarea rows="4"' + attrs + '></textarea>' if multiline else '<input' + attrs + '>') + '</label>'
    form += '<button class="button button-gold" type="submit">Prepare an email</button> <button class="button" id="intake-download" type="button">Download the enquiry text</button></form><p id="intake-status" role="status" aria-live="polite"></p><details><summary>Preview the email text</summary><pre class="intake-preview" id="intake-preview"></pre></details><p>You can also email <a href="mailto:' + recipient + '">' + recipient + '</a> directly.</p><noscript><p>To enquire, email the address above with your organisation, question, the people involved, and intended timing.</p></noscript><script defer src="/assets/js/practice-intake.js?v=20261105"></script>'
    page(route, title, lead, form, private_input=True, extra_head=intake_style)


intake('community/bring-a-case', 'Case clinic enquiries', 'Describe the case you would bring and the help you want from the group.', 'info@publicservicetransformation.org', 'The PSTA case clinic enquiry', [('Your role and organisation', False), ('What is happening, and what question do you need help with?', True), ('Who is involved, and whose perspective is missing?', True), ('What can you change, and what have you already tried?', True), ('What can be shared, and what must remain confidential?', True), ('What timing and participation would work for you?', False)])
intake('enquire', 'The PSTA programme and support enquiries', 'Prepare an email about a programme, tool, or change your team needs to make.', 'david.mason@publicservicetransformation.org', 'The PSTA programme and practice enquiry', [('Your role and organisation', False), ('Which programme, tool, or kind of support are you considering?', False), ('What is happening, and who is affected?', True), ('What do you need to decide or change?', True), ('Who would take part, and who can authorise the work?', True), ('When is a decision needed? What limits the work, and how would you buy support?', True)])

community = root / 'community/index.html'
addition = '<section class="section"><div class="shell"><h2>Case clinic resources</h2><p>Download the host guide and case brief, or propose a case for a practice group with the PSTA.</p><p><a class="button button-gold" href="/community/case-clinics/">Use the case clinic resources</a> <a href="/community/bring-a-case/">Propose a case or express interest</a></p></div></section>'
append_section(community, 'PSTA_CASE_CLINICS_20261105', addition)

tool_index = root / 'tools/index.html'
addition = '<section class="section"><div class="shell"><h2>Save and review your assessment</h2><p>Record answers, evidence, and actions in a Compass workspace. Ask colleagues for their views, and review what happened after you acted. You can save a copy on your device, download it, or print your notes.</p><a class="button button-gold" href="/tools/compass/">Choose a Compass workspace</a></div></section>'
append_section(tool_index, 'PSTA_COMPASS_WORKSPACES_20261105', addition)

record = json.loads((repo / 'content/programmes/leading-transformation.json').read_text(encoding='utf-8'))
record_path = root / 'records/leading-transformation.json'
record_path.parent.mkdir(parents=True, exist_ok=True)
record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
programme = root / 'programmes/leading-transformation/index.html'
text = programme.read_text(encoding='utf-8')
psta_route, shed_route = record['routes']['psta'], record['routes']['toolshed']
assert psta_route['fee']['currency'] == shed_route['fee']['currency'] == 'GBP'
def fee(route):
    return '£' + format(route['fee']['amount'], ',g') + ' ' + route['fee']['vat'] + ' per ' + route['fee']['unit']
fees = '<div class="programme-fees"><h3>Fees and accreditation</h3><p><strong>Leading Transformation: ' + e(fee(psta_route)) + '.</strong> ' + e(psta_route['support']) + '</p><p>' + e(psta_route['organisationalDelivery']) + '</p><p><strong>The RedQuadrant Tool Shed: ' + e(fee(shed_route)) + '.</strong> ' + e(shed_route['availability']) + '</p><p>Leading Transformation: ' + e(psta_route['accreditation']) + '.<br>The Tool Shed: ' + e(shed_route['accreditation']) + '.</p><p><a href="mailto:' + e(psta_route['contact'], quote=True) + '?subject=Leading%20Transformation">Discuss Leading Transformation</a></p></div>'
text, count = re.subn(r'<div class="programme-fees">.*?</div>', lambda _: fees, text, count=1, flags=re.S)
assert count == 1, 'Expected the programme fee block'
programme.write_text(text, encoding='utf-8')
source_note = '<section class="section"><div class="shell"><h2>Programme record</h2><p>Check the shared curriculum, fees, and programme options in <a href="' + record['canonicalUrl'] + '">RedQuadrant’s programme record</a>. This page uses record version ' + record['version'] + '; <a href="/records/leading-transformation.json">read the copy used on this page</a>. ' + e(record['curriculumStatus']) + '</p><p><a href="/enquire/">Prepare a programme enquiry</a></p></div></section>'
append_section(programme, 'PSTA_PROGRAMME_RECORD_20261105', source_note)

privacy = root / 'privacy/index.html'
addition = '<section class="section"><div class="shell"><h2>Compass workspaces and enquiry preparation</h2><p>The self-hosted Compass workspaces keep your answers in the open page until you choose to save them on your device or download them. Saved copies use browser storage for the specific edition. They are not synchronised between devices or sent to the PSTA. Use Remove device copy in the workspace, or clear this site’s browser data, to remove a saved copy. Downloaded files are separate and remain until you delete them.</p><p>Workspace and enquiry-preparation pages do not load the page-visit counter or third-party scripts. Enquiry preparation stays in the page until you choose to open an email draft or download its text. Your email provider handles any message you choose to send. The separate original smartCompass AI email service has its own consent and data-processing explanation in its form.</p></div></section>'
append_section(privacy, 'PSTA_LOCAL_RECORD_PRIVACY_20261105', addition)

sitemap = root / 'sitemap.xml'
text = sitemap.read_text(encoding='utf-8')
for route in published:
    url = domain + '/' + route + '/'
    if '<loc>' + url + '</loc>' not in text:
        text = text.replace('</urlset>', '<url><loc>' + url + '</loc></url></urlset>')
sitemap.write_text(text, encoding='utf-8')
print(f'Published {len(tools)} Compass workspaces, source text, case-clinic resources, enquiry preparation, and the checked programme record')
