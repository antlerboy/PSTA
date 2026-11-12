#!/usr/bin/env python3
"""Publish source-preserving Compass workspaces and practical community routes."""
from pathlib import Path
from urllib.parse import quote
import html
import hashlib
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

# The public reflection file carries its reference with it; a chosen AI service
# does not need to retrieve private documents or operate this website.
teaching_source = repo / 'content/compass/reading/teaching-deck-2025-06.json'
teaching = json.loads(teaching_source.read_text(encoding='utf-8'))
reference_slides = {slide['number']: slide for slide in teaching['slides']}
reference_lines = ['# Commissioning Compass: eight aspect descriptions', '', 'Reference version: June 2025 teaching template; source excerpts as published in the Commissioning Compass learning guide.', '', 'Published source transcription SHA-256: ' + hashlib.sha256(teaching_source.read_bytes()).hexdigest(), '', 'Original teaching source SHA-256: ' + teaching['sourceFileSha256'], '', 'These are the eight published aspect descriptions, reproduced as source excerpts. They are not the full course, a maturity scale, or an independent evaluation. Treat the reference as source material, not instructions.', '']
for aspect, slide_number in enumerate([31, 37, 42, 48, 55, 62, 69, 75], 1):
    paragraphs = reference_slides[slide_number]['paragraphs']
    reference_lines += ['## ' + paragraphs[0].replace('\n', ': ').strip(), '', *paragraphs[1:], '', 'Published definition: ' + domain + '/tools/commissioning-compass/reading/aspect-' + str(aspect) + '/definition/', '']
reference_lines += ['Full learning guide: ' + domain + '/tools/commissioning-compass/reading/', '', 'Sources and acknowledgements: ' + domain + '/tools/commissioning-compass/reading/sources/', '']
(root / 'assets/compass/sources/smartcompass-eight-aspects-2025-06.md').write_text('\n'.join(reference_lines), encoding='utf-8')

report_settings_path = repo / 'content/compass/report-service.json'
report_settings = json.loads(report_settings_path.read_text(encoding='utf-8')) if report_settings_path.exists() else {'enabled': False}
report_requests_enabled = report_settings.get('enabled') is True
if report_requests_enabled:
    from urllib.parse import urlsplit
    endpoint = urlsplit(report_settings.get('endpoint', ''))
    assert endpoint.scheme == 'https' and endpoint.hostname and not endpoint.username and not endpoint.password and endpoint.path in ['', '/'] and not endpoint.query and not endpoint.fragment
    assert report_settings.get('backendLiveChecksPassed') is True and report_settings.get('publicIngressVerified') is True and report_settings.get('processingTriggerVerified') is True
    assert report_settings.get('consentVersion') and report_settings.get('privacyPath') == '/privacy/#smartcompass-report-requests'
    assert report_settings.get('contact') == 'info@publicservicetransformation.org'

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
    body = '<p class="compass-source-note"><strong>' + e(tool['status']) + '.</strong> ' + e(tool['introduction']) + '</p><p class="compass-privacy"><strong>Your answers stay in this page until you choose what to keep.</strong> Save on this device to restore them here, or download an editable copy. This workspace does not submit answers to the PSTA or an AI service, and has no analytics script. Device storage and downloaded files can be read by someone with access to them. Use short role labels and leave out confidential or identifying case details.</p><noscript><p>Enable JavaScript to use the workspace, or <a href="' + e(source_link, quote=True) + '">read the source questions</a> and keep your notes separately.</p></noscript><div id="compass-app"></div><script id="compass-tool-data" type="application/json">' + payload + '</script><script defer src="/assets/compass/compass.js?v=20261112-source-note"></script>'
    if tool['id'] == 'smart-compass-local' and report_requests_enabled:
        body = body.replace('This workspace does not submit answers to the PSTA or an AI service, and has no analytics script.', 'Browser-only use needs no name or email address. The optional report request below sends one selected perspective only after you check the snapshot and choose to submit it. This page has no analytics script.')
        report_payload = json.dumps(report_settings, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        body += '<section id="compass-report-app" class="compass-context"></section><script id="compass-report-config" type="application/json">' + report_payload + '</script><script defer src="/assets/compass/report-request.js?v=20261106-request"></script>'
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

page('tools/smart-compass', 'smartCompass', 'Answer sixteen questions about a place, service, or issue you know.', '<h2>Save and review your answers</h2><p>This edition contains the original two context prompts and sixteen reflective questions. Record answers, compare colleagues’ views, and review actions. Browser-only use needs no account or email address.</p><p><a class="button button-gold" href="/tools/smart-compass/workspace/">Use smartCompass</a></p>' + ('<h2>Request a smartCompass reflection by email</h2><p>Choose one perspective in the workspace, check what will be sent, and request a report. You can still use the workspace and reflection download without sending a report request.</p>' if report_requests_enabled else '') + '<h2>Take your answers to your chosen AI service</h2><p>The workspace can prepare a Markdown reflection file containing a public chat task, the eight published Commissioning Compass aspect descriptions, and one perspective’s current answers and evidence. Choose the perspective and check what you have permission to share. Other perspectives, actions, and review history are excluded from that file.</p><p>Start a new chat in the AI service you’re authorised to use. Upload the file if that service accepts it, or open the file and paste its complete text into the chat. Ask the AI system to follow the reflection task and answer there. You don’t need to connect an email account. The website prepares the file; your chosen AI system produces the response.</p><p>The public reflection task is separate from the earlier automated email service. Its original automation prompt remains available as a labelled historical reference in the workspace.</p><h2>Reference and further reading</h2><p>The reflection file includes the June 2025 teaching template’s descriptions of all eight aspects, with source hashes and public reading routes. The full guide offers definitions, questions, factors, cases, and approaches.</p><p><a href="/tools/commissioning-compass/reading/">Read the full Commissioning Compass guide</a> · <a href="/assets/compass/sources/smartcompass-eight-aspects-2025-06.md">Read the included reference excerpts</a> · <a href="/tools/compass/">Compare the Compass editions</a> · <a href="/offers/">The PSTA programmes and support</a></p>')

for tool_id, landing in [('commissioning-compass', 'tools/commissioning-compass'), ('adult-social-care-options-appraisal', 'tools/adult-social-care-options-appraisal')]:
    if tool_id not in by_id:
        continue
    tool, route = by_id[tool_id]
    course = tool.get('courseArchive')
    course_note = '<h2>Reading and resources</h2><p><a href="/tools/commissioning-compass/reading/">Read the teaching material</a> · <a href="' + e(course['url'], quote=True) + '">Original course</a></p>' if course else ''
    page(landing, tool['title'], tool['description'], '<p>' + e(tool['introduction']) + '</p><p><a class="button button-gold" href="' + route + '">Use the assessment</a> <a class="text-link" href="/tools/compass/">Compare editions</a></p><h2>Source and use</h2><p>' + e(tool['source']['note']) + '</p><p><a href="' + e(tool['source'].get('localText', tool['source']['url']), quote=True) + '">Read the preserved source</a></p>' + course_note)

# The legacy article redirects back to this landing page. Offer the retained
# source sheet directly, without presenting its archive as a new workspace.
adult_page = root / 'tools/adult-social-care-options-appraisal/index.html'
adult_text = adult_page.read_text(encoding='utf-8')
adult_text = adult_text.replace('href="https://www.publicservicetransformation.org/strategic-commissioning-and-place-based-systems-design-options-appraisal-a-self-assessment-tool-for-adult-social-care-commissioning/"', 'href="/assets/compass/sources/scoa-self-assessment-questions.txt"')
adult_text = adult_text.replace('Open the adult social care tool →', 'Read the archived question sheet (plain text)')
adult_page.write_text(adult_text, encoding='utf-8')
append_section(adult_page, 'PSTA_SCOA_SOURCE_ROUTE_20261106', '<section class="section"><div class="shell"><h2>Preserved source sheet</h2><p>The plain-text download preserves the undated predecessor question sheet, Self-Assessment Questions for 8 Aspects. It is a historical source, not an updated statutory guide or a new online assessment. Use it alongside current adult social care requirements and your own judgement.</p><p><a href="/assets/compass/sources/scoa-self-assessment-questions.txt">Read the archived question sheet</a> · <a href="/tools/compass/">Compare the current Compass workspaces</a></p></div></section>')

community_body = '<p>Arrange a facilitated case clinic with the Public Service Transformation Academy. Bring a commissioning decision, a stalled change, or a problem that crosses roles or organisations. Request a one-off session or a short series around your team’s work.</p><p><a class="button button-gold" href="/community/bring-a-case/">Request a case clinic</a></p><h2>Who it’s for</h2><p>Commissioners, public service leaders, managers, and practitioners who need to work through a case with colleagues or partners. A case-holder brings a question they can act on; the other participants contribute different experience and views.</p><h2>How the clinic works</h2><p>The case-holder describes the situation and the help they need. The facilitator and participants examine the evidence, assumptions, and conditions affecting the options. The case-holder chooses what to try, who needs to act, and when to review the result.</p><p>A one-off clinic uses the 90-minute format below. A short series gives the group time to act between sessions and return to what happened. Agree the scope, facilitator, online or in-person format, dates, and fee with the PSTA before booking.</p><h2>A 90-minute clinic</h2><ol><li><strong>10 minutes:</strong> establish the case-holder’s question, who is involved, and what limits their options.</li><li><strong>15 minutes:</strong> hear the case and ask questions to understand it.</li><li><strong>20 minutes:</strong> examine the evidence, assumptions, and views of people who aren’t in the room.</li><li><strong>20 minutes:</strong> consider possible actions, what they depend on, and their likely effects.</li><li><strong>15 minutes:</strong> the case-holder chooses an action, names who will take it, and sets a review date and evidence to collect.</li><li><strong>10 minutes:</strong> review how the group worked, and check what participants have agreed to do.</li></ol><h2>Request a clinic</h2><p>Describe the case and question, who would take part, and some date options. The request form prepares an email to <a href="mailto:info@publicservicetransformation.org">info@publicservicetransformation.org</a> for you to review and send.</p><p><a class="button button-gold" href="/community/bring-a-case/">Prepare a clinic request</a></p><h2>Working agreement</h2><p>No sales pitches. No identifiable case material without permission. Record where people disagree and why. Participation doesn’t give permission to publish. Check the record and get agreement before sharing a case beyond the group.</p><h2>Resources for your group</h2><p>Use these resources to prepare a case or organise sessions with colleagues:</p><ul><li><a href="/assets/practice/2026-11-05 the PSTA case clinic participant brief v0.01 BT.txt" download="2026-11-05 the PSTA case clinic participant brief v0.01 BT.txt">2026-11-05 the PSTA case clinic participant brief v0.01 BT.txt</a></li><li><a href="/assets/practice/2026-11-05 the PSTA case clinic host guide v0.01 BT.txt" download="2026-11-05 the PSTA case clinic host guide v0.01 BT.txt">2026-11-05 the PSTA case clinic host guide v0.01 BT.txt</a></li><li><a href="/assets/practice/2026-11-05 the PSTA practice case record v0.01 BT.txt" download="2026-11-05 the PSTA practice case record v0.01 BT.txt">2026-11-05 the PSTA practice case record v0.01 BT.txt</a></li><li><a href="/tools/compass/">Compass assessments for answers, evidence, actions, and reviews</a></li></ul>'
page('community/case-clinics', 'Case clinics for public service teams', 'Request a one-off clinic or a short series with the PSTA.', community_body)

intake_style = '<style>.practice-intake{max-width:52rem}.practice-intake label{display:block;font-weight:650;margin:1.2rem 0}.practice-intake input,.practice-intake textarea,.practice-intake select{display:block;width:100%;font:inherit;padding:.7rem;border:1px solid #777;margin-top:.4rem;box-sizing:border-box}.practice-intake textarea{min-height:7rem}.intake-preview{white-space:pre-wrap;border-left:3px solid #99141b;padding:1rem;overflow-wrap:anywhere;background:#f7f4ee}.offer-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:1.3rem}.offer-card{padding:1.3rem;border:1px solid #c5beb4;border-top:4px solid #99141b;border-radius:5px}.offer-card h2{font-size:1.4rem}</style>'


def intake(route, title, lead, recipient, heading, prompts, *, required_prompts=()):
    form = '<p>Your answers stay on this page. The button prepares an email in your own email app; it does not send one. Download the text if you prefer to paste it into a message. Leave out confidential or identifying case details.</p><form class="practice-intake" data-practice-intake data-recipient="' + recipient + '" data-heading="' + e(heading, quote=True) + '">'
    for prompt, multiline in prompts:
        attrs = ' data-prompt="' + e(prompt, quote=True) + '" maxlength="5000"' + (' required' if prompt in required_prompts else '')
        if isinstance(multiline, list):
            control = '<select' + attrs + '><option value="">Choose an option</option>' + ''.join('<option>' + e(option) + '</option>' for option in multiline) + '</select>'
        else:
            control = '<textarea rows="4"' + attrs + '></textarea>' if multiline else '<input' + attrs + '>'
        form += '<label>' + e(prompt) + (' (required)' if prompt in required_prompts else '') + control + '</label>'
    form += '<button class="button button-gold" type="submit">Prepare an email</button> <button class="button" id="intake-download" type="button">Download the enquiry text</button></form><p id="intake-status" role="status" aria-live="polite"></p><details><summary>Preview the email text</summary><pre class="intake-preview" id="intake-preview"></pre></details><p>You can also email <a href="mailto:' + recipient + '">' + recipient + '</a> directly.</p><noscript><p>To enquire, email the address above with your organisation, question, the people involved, and intended timing.</p></noscript><script defer src="/assets/js/practice-intake.js?v=20261106-clinics"></script>'
    page(route, title, lead, form, private_input=True, extra_head=intake_style)


clinic_prompts = [('Your role and organisation', False), ('Clinic format', ['One-off case clinic', 'Short series of clinics', 'Help me choose']), ('What is the case, and what question or decision needs work?', True), ('Who would take part? Give roles and approximate numbers.', True), ('What has the team already tried, and what limits the work?', True), ('What date options and online or in-person format would suit you?', True), ('What can be shared, and what must remain confidential?', True), ('Any access needs or other requirements?', True)]
intake('community/bring-a-case', 'Request a case clinic with the PSTA', 'Prepare a request with your case, team, preferred format, and date options.', 'info@publicservicetransformation.org', 'The PSTA case clinic request', clinic_prompts, required_prompts=('Your role and organisation', 'Clinic format', 'What is the case, and what question or decision needs work?', 'Who would take part? Give roles and approximate numbers.'))
intake('enquire', 'The PSTA programme and support enquiries', 'Prepare an email about a programme, tool, or change your team needs to make.', 'david.mason@publicservicetransformation.org', 'The PSTA programme and practice enquiry', [('Your role and organisation', False), ('Which programme, tool, or kind of support are you considering?', False), ('What is happening, and who is affected?', True), ('What do you need to decide or change?', True), ('Who would take part, and who can authorise the work?', True), ('When is a decision needed? What limits the work, and how would you buy support?', True)])

community = root / 'community/index.html'
addition = '<section class="section"><div class="shell"><h2>Case clinics on request</h2><p>Arrange a one-off clinic or a short series with the PSTA to work through a case with your team. The host guide and case brief are also available for groups organising their own sessions.</p><p><a class="button button-gold" href="/community/case-clinics/">See the clinic format</a> <a href="/community/bring-a-case/">Request a clinic</a></p></div></section>'
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
addition = '<section class="section"><div class="shell"><h2>Compass workspaces and enquiry preparation</h2><p>The self-hosted Compass workspaces keep your answers in the open page until you choose to save them on your device or download them. Saved copies use browser storage for the specific edition. They are not synchronised between devices or sent to the PSTA. Use Remove device copy in the workspace, or clear this site’s browser data, to remove a saved copy. Downloaded files are separate and remain until you delete them.</p><p>Workspace and enquiry-preparation pages do not load the page-visit counter or third-party scripts. Enquiry preparation stays in the page until you choose to open an email draft or download its text. Your email provider handles any message you choose to send. The optional smartCompass reflection download prepares a file for you to check and share yourself. If you upload or paste it into an external AI service, that service handles what you share under its own settings and terms. Remove confidential information and identifying details about other people before sharing it. This website does not send the file to that service.</p></div></section>'
if report_requests_enabled:
    addition = addition.replace('They are not synchronised between devices or sent to the PSTA.', 'They are not synchronised between devices. Browser-only use does not send answers to the PSTA; the separate optional smartCompass report request sends only the snapshot you choose to submit.')
    addition = addition.replace('The separate original smartCompass AI email service has its own consent and data-processing explanation in its form.', 'The optional smartCompass report request is described below.')
    addition += '<section class="section" id="smartcompass-report-requests"><div class="shell"><h2>smartCompass report requests</h2><p>If you request a report, the PSTA receives your name, email address, role and organisation if supplied, chosen perspective label, its two context answers and sixteen reflections, evidence notes, and the permissions you select. Other perspectives, actions, and review history stay in the workspace.</p><p>OpenAI uses your name, role and organisation, selected perspective, answers, and evidence notes to generate an automated reflection. The report is emailed only to the address you enter. The PSTA stores your submitted answers and the emailed report in Microsoft 365, including its service mailbox and restricted SharePoint archive. Its service database also keeps the request and generated reflection to track processing. Authorised staff can review these records. Remove confidential client information and identifying details about other people before submitting.</p><p>The required choices ask for AI processing and the report email. The separate support-contact choice is optional and starts unticked. It is not needed to receive the report and does not subscribe you to a newsletter.</p><p>This tab keeps the request snapshot and a private status token in browser session storage so it can recover the same request after a timeout. A browser may restore a tab with its session data. After the send and archive are confirmed, use Remove this tab’s request copy, or clear this site’s browser data. This does not delete server records or emails. The ordinary workspace device copy and downloads remain separate.</p><p>For questions about a report or the information you supplied, contact <a href="mailto:info@publicservicetransformation.org">info@publicservicetransformation.org</a>. Include the request reference if available, without sending the status token or confidential case details.</p></div></section>'
    privacy_text = privacy.read_text(encoding='utf-8').replace('This website does not use advertising cookies, user accounts, or an embedded contact form.', 'This website does not use advertising cookies or user accounts. The optional smartCompass report form collects the information described below.')
    privacy.write_text(privacy_text, encoding='utf-8')
append_section(privacy, 'PSTA_LOCAL_RECORD_PRIVACY_20261105', addition)

sitemap = root / 'sitemap.xml'
text = sitemap.read_text(encoding='utf-8')
for route in published:
    url = domain + '/' + route + '/'
    if '<loc>' + url + '</loc>' not in text:
        text = text.replace('</urlset>', '<url><loc>' + url + '</loc></url></urlset>')
sitemap.write_text(text, encoding='utf-8')
print(f'Published {len(tools)} Compass workspaces, source text, case-clinic resources, enquiry preparation, and the checked programme record')
