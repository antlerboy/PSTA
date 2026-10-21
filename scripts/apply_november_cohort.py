"""Apply the January 2027 cohort update after the historical site assembly."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
for path in root.rglob('*'):
    if not path.is_file() or path.suffix not in {'.html', '.xml', '.json'}:
        continue
    text = path.read_text(encoding='utf-8')
    text = text.replace('7 Bell Yard', '167–169 Great Portland Street, 5th Floor').replace('WC2A 2JR', 'W1W 5PF')
    text = text.replace('September 2026 to February 2027', 'Starting January 2027')
    text = text.replace('The main programme runs to February 2027.', 'Exact dates and the full timetable are to be confirmed.')
    text = text.replace('November 2026 to February 2027', 'Starting January 2027')
    text = text.replace('November 2026 - February 2027', 'Starting January 2027')
    text = text.replace('September 2026 cohort', 'January 2027 cohort')
    text = text.replace('Applications are open for the January 2027 cohort.', 'Applications are open for the January 2027 cohort. Exact dates and the full timetable are to be confirmed.')
    text = text.replace('returns in September 2026', 'returns in January 2027')
    text = text.replace('Academy%20September%202026', 'Academy%20January%202027')
    text = re.sub(r'The launch webinar is on (?:<strong>)?Monday 14 September 2026, 10:00[–-]12:30(?:</strong>)?\. The first full anchor day is on (?:<strong>)?Wednesday 23 September 2026, 10:00[–-]16:30(?:</strong>)?\.', 'The next cohort starts in January 2027. Exact dates and the full timetable are to be confirmed.', text)
    text = text.replace('£2,490 per participant', '£2,490 excluding VAT per participant')
    text = text.replace('£2,490 excluding VAT per participant.Discounts', '£2,490 excluding VAT per participant. Discounts')
    # The current address is supplied explicitly in the controlling web plan.
    text = re.sub(r'7 Bell Yard,? London,? (?:WC2A 2JR)(?:,? UK)?', '167–169 Great Portland Street, 5th Floor, London, W1W 5PF', text)
    path.write_text(text, encoding='utf-8')
print('Applied January 2027 cohort: exact dates and full timetable to be confirmed')

# Add the approved offer before the existing final copy and internal-link audits.
from launch_service_change import apply_launch_service_change
apply_launch_service_change(root)

# Apply the sharper system-level National Commissioning Academy positioning.
import apply_nca_positioning  # noqa: E402,F401
