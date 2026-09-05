"""Apply the confirmed November cohort after the historical site assembly."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
for path in root.rglob('*'):
    if not path.is_file() or path.suffix not in {'.html', '.xml', '.json'}:
        continue
    text = path.read_text(encoding='utf-8')
    text = text.replace('7 Bell Yard', '167–169 Great Portland Street, 5th Floor').replace('WC2A 2JR', 'W1W 5PF')
    text = text.replace('September 2026 to February 2027', 'November 2026 to February 2027')
    text = text.replace('September 2026 cohort', 'November 2026 cohort')
    text = text.replace('returns in September 2026', 'returns in November 2026')
    text = text.replace('Academy%20September%202026', 'Academy%20November%202026')
    text = re.sub(r'The launch webinar is on (?:<strong>)?Monday 14 September 2026, 10:00[–-]12:30(?:</strong>)?\. The first full anchor day is on (?:<strong>)?Wednesday 23 September 2026, 10:00[–-]16:30(?:</strong>)?\.', 'The induction webinar is on Tuesday 10 November 2026. The revised anchor-day dates and session times will be confirmed by David Mason.', text)
    text = text.replace('£2,490 per participant', '£2,490 excluding VAT per participant')
    text = text.replace('£2,490 excluding VAT per participant.Discounts', '£2,490 excluding VAT per participant. Discounts')
    # The current address is supplied explicitly in the controlling web plan.
    text = re.sub(r'7 Bell Yard,? London,? (?:WC2A 2JR)(?:,? UK)?', '167–169 Great Portland Street, 5th Floor, London, W1W 5PF', text)
    path.write_text(text, encoding='utf-8')
print('Applied November cohort: induction 10 November; remaining dates await confirmation')
