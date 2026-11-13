from pathlib import Path
import re
import sys

root = Path(sys.argv[1])

# Owner-approved temporary service notice, 13 November 2026.
# Remove this block when the incident is confirmed resolved.
notice = '''<section id="microsoft-outage-notice" aria-labelledby="microsoft-outage-heading" style="background:#fff3cd;color:#222;border-bottom:3px solid #ad7412;padding:1.5rem 0">
<div class="shell">
<h2 id="microsoft-outage-heading">Global Microsoft outage: contacting the Academy</h2>
<p><strong>Updated <time datetime="2026-11-13T11:14:00+00:00">13 November 2026, 11:14 GMT</time></strong></p>
<p>The global Microsoft outage is affecting our team’s email and access to some other Microsoft services.</p>
<p>If you need help with an imminent session, programme, booking, or deadline, please contact Benjamin Taylor at <a href="mailto:benjamin.taylor@redquadrant.com">benjamin.taylor@redquadrant.com</a>. His email is working through a Gmail workaround. Please include the programme or session name, the date, and a phone number.</p>
<p>We’re working on temporary business email addresses and will publish them here once they’re tested and ready. Please don’t send learner information or project documents to personal email accounts.</p>
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
