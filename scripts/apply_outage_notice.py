from pathlib import Path
import re
import sys

root = Path(sys.argv[1])

# Owner-approved temporary service notice, 13 November 2026.
# Remove this block when the incident is confirmed resolved.
notice = '''<section id="microsoft-outage-notice" aria-labelledby="microsoft-outage-heading" style="background:#fff3cd;color:#222;border-bottom:3px solid #ad7412;padding:1.5rem 0">
<div class="shell">
<h2 id="microsoft-outage-heading">Global Microsoft outage: contacting the Academy</h2>
<p><strong>Updated <time datetime="2026-11-13T13:47:00+00:00">13 November 2026, 13:47 GMT</time></strong></p>
<p>Access is improving following the global Microsoft outage, but this is not yet an all-clear. Some colleagues are regaining access to email and Microsoft services. Intermittent access problems and delayed email delivery may continue, and we are checking recovery across our team.</p>
<p>If you need help with an imminent session, programme, booking, or deadline, please contact Benjamin Taylor at <a href="mailto:benjamin.taylor@redquadrant.com">benjamin.taylor@redquadrant.com</a>. His email is working through a Gmail workaround. Please include the programme or session name, the date, and a phone number.</p>
<p>Please continue to use your usual business email contacts, but call or contact Benjamin if your enquiry is urgent or you have not received a response. Please don’t send learner information or project documents to personal email accounts.</p>
<p>If you’re waiting for an urgent response, please contact Benjamin or call your usual programme contact. Apologies for the disruption.</p>
</div></section>'''
for relative in ('index.html', 'contact/index.html'):
    target = root / relative
    html = target.read_text(encoding='utf-8')
    if 'id="microsoft-outage-notice"' not in html:
        html, inserted = re.subn(r'(<main\b[^>]*>)', lambda m: m.group(0) + notice, html, count=1)
        if inserted != 1:
            raise SystemExit(f'Cannot locate main content for service notice: {relative}')
        target.write_text(html, encoding='utf-8')
print('Added dated Microsoft outage notice to home and contact pages')
