'''Apply David Mason's approved contract management amendments from issue #17.'''
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
page = root / 'programmes/contract-management-development/index.html'
text = page.read_text(encoding='utf-8')
text = text.replace('Next cohort to be announced', 'Open to applications')
text = text.replace('<div><dt>Time</dt><dd>Cohort schedule agreed for each run</dd></div>', '<div><dt>Launch</dt><dd>Wednesday 11 November 2026</dd></div><div><dt>Fee</dt><dd>£1,350 plus VAT per participant; group booking discounts available</dd></div>')
text = text.replace('Ask about the next cohort', 'Apply or ask about a place')
fees = '''<section class="section guide-fee"><div class="shell">
<h2>November 2026 programme: dates and fees</h2>
<p>Applications are open. The programme launches on <strong>Wednesday 11 November 2026</strong>.</p>
<p><strong>£1,350 plus VAT per participant.</strong> Discounts are available for group bookings.</p>
<p>To secure your place or find out more, contact Sarah Johnston on <a href="tel:+447701049836">07701 049836</a> or <a href="mailto:sarah.johnston@publicservicetransformation.org">sarah.johnston@publicservicetransformation.org</a>.</p>
<h2>A bespoke cohort for your organisation</h2>
<p>Our guide price is <strong>£8,950 excluding VAT</strong> for a bespoke cohort of up to 16 people: six 90-minute online development sessions, a three-hour application session, preparation, and practice materials.</p>
<p>This is an indicative starting price for the scope described. We agree a written fixed-fee proposal before booking. Venue, travel, accommodation, additional coaching, and external assessment fees are separate where required.</p>
<p><a class="button button-gold" href="mailto:sarah.johnston@publicservicetransformation.org?subject=Contract%20Management%20Development%20Programme">Discuss a place or a bespoke cohort with Sarah</a></p>
</div></section>'''
text, count = re.subn(r'<section class="section guide-fee">.*?</section>', fees, text, flags=re.S)
if count != 1:
    raise SystemExit(f'Expected one contract management fee section; found {count}')
page.write_text(text, encoding='utf-8')
print('Applied contract management November cohort, participant fee, bespoke scope, and Sarah contact')

# Keep the programme chooser consistent with the detailed offer.
listing = root / 'programmes/index.html'
text = listing.read_text(encoding='utf-8')
def update_card(match):
    card = match.group(0)
    if '/programmes/contract-management-development/' in card:
        card = card.replace('Next cohort to be announced', 'Open to applications')
        card = card.replace('Cohort schedule agreed for each run', 'Launching Wednesday 11 November 2026')
    return card
text = re.sub(r'<article\b[^>]*>.*?</article>', update_card, text, flags=re.S)
listing.write_text(text, encoding='utf-8')
