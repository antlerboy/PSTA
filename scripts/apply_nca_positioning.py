#!/usr/bin/env python3
'''Sharpen the National Commissioning Academy positioning around system-level work.'''
from __future__ import annotations

from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
page = root / "programmes/national-commissioning-academy/index.html"
markup = page.read_text(encoding="utf-8")

main = r'''<main id="main-content" class="site-main">
<!-- PSTA_NCA_2026_START -->
<section class="page-hero page-hero-programme">
  <div class="shell">
    <nav class="breadcrumbs" aria-label="Breadcrumb">
      <a href="/">Home</a><span aria-hidden="true">/</span>
      <a href="/programmes/">Programmes</a><span aria-hidden="true">/</span>
      <span>National Commissioning Academy</span>
    </nav>
    <p class="eyebrow">Flagship cross-sector programme</p>
    <div class="page-hero-heading">
      <div>
        <h1>The National Commissioning Academy</h1>
        <p class="lede">For people responsible for outcomes no one organisation can deliver alone.</p>
        <p>When money, authority, information and responsibility sit in different places, a better project plan is not enough. Learn to see the whole system, convene the people who shape it, and make practical progress from where you stand.</p>
        <p class="hero-note"><strong>Starting January 2027 · £2,490 excluding VAT per participant</strong></p>
        <div class="hero-actions">
          <a class="button button-gold" href="mailto:info@publicservicetransformation.org?subject=National%20Commissioning%20Academy%20January%202027">Apply or ask a question</a>
        </div>
      </div>
      <span class="status status-large is-open">Applications open</span>
    </div>
  </div>
</section>

<!-- PSTA_ISLINGTON_WEBINAR_20261104_START -->
<section id="islington-webinar-invitation" class="section section-tint" aria-labelledby="islington-webinar-heading" data-event-start="2026-11-04T13:30:00Z" data-event-end="2026-11-04T14:30:00Z">
  <div class="shell">
    <p class="eyebrow">Webinar · Wednesday 4 November 2026 · 13:30–14:30 GMT</p>
    <h2 id="islington-webinar-heading">Outcomes commissioning in practice: lessons from Islington</h2>
    <p>Join Chrissie Gregory and Sharon Davidson, improvement consultants working with the London Borough of Islington, in conversation with Benjamin P Taylor. Explore how an outcomes focus can change the conversations and decisions behind children’s services reform, and how learning through the Commissioning Academy helped them sharpen their practice.</p>
    <p>This one-hour webinar is separate from the Academy cohort starting in January 2027. Exact Academy dates and the full timetable are to be confirmed. David will confirm registration arrangements and joining details.</p>
    <p><a class="button button-gold" href="mailto:david.mason@publicservicetransformation.org?subject=Islington%20webinar%204%20November">Register your interest with David Mason</a></p>
    <p><a class="text-link" href="/news/outcomes-commissioning-islington-webinar/">Read the webinar outline</a></p>
  </div>
</section>
<script>
(function () {
  const invitation = document.getElementById('islington-webinar-invitation');
  if (invitation && Date.now() >= Date.parse(invitation.dataset.eventEnd)) invitation.hidden = true;
}());
</script>
<!-- PSTA_ISLINGTON_WEBINAR_20261104_END -->

<div class="shell content-with-aside">
  <article class="prose">
    <h2>The outcome belongs to the whole system</h2>
    <p>Public organisations are built to manage their own service, budget and accountability. People live with the result of the whole system.</p>
    <p>A service can meet its target while demand, cost or risk moves somewhere else. A contract can deliver its specification while people's lives remain difficult. Providers, communities, professionals and citizens all shape what is possible.</p>
    <p>The Academy helps you work on that reality.</p>

    <h2>Commissioning as practical system change</h2>
    <p>Commissioning is not a cycle to complete or procurement by another name. It is the continuing work of shaping outcomes, decisions, markets, resources, relationships, evidence, incentives and community capacity — while no one controls the whole.</p>
    <p>You will work with the practical conditions that make change possible or stop it: who holds authority, where money flows, what people are rewarded for, whose knowledge counts, how providers behave, what communities can sustain, and where apparently sensible action creates consequences elsewhere.</p>

    <h2>The Academy earns its place when</h2>
    <ul>
      <li>the outcome crosses organisational, professional or geographical boundaries;</li>
      <li>no single person or organisation can direct the result;</li>
      <li>budgets, incentives and accountability pull in different directions;</li>
      <li>provider markets or community capacity shape what can actually be delivered;</li>
      <li>improving one part of the system may move demand, cost or risk into another; or</li>
      <li>you need to convene, decide, test and learn in conditions of genuine uncertainty.</li>
    </ul>
    <p>You do not need the word ‘commissioning’ in your job title. You do need responsibility for an outcome your organisation cannot secure by itself.</p>

    <h2>Work on the live problem</h2>
    <p>Bring a commissioning or system-change challenge from your own work. Use the programme to examine it from different positions, test your assumptions, make better decisions and turn learning into action.</p>
    <p>The cohort is deliberately mixed across local government, health, central government, policing, housing, civil society and other public services. That difference matters: it gives you access to knowledge, experience and challenge that do not exist inside one organisation or profession.</p>

    <h2>What you will do</h2>
    <ul>
      <li>define the outcome more sharply from the perspective of citizens and communities;</li>
      <li>trace how demand, cost, effort, risk and consequences move through the system;</li>
      <li>make power, incentives, resource flows and decision rights visible;</li>
      <li>work with provider behaviour, markets and community capacity rather than treating them as background;</li>
      <li>test practical interventions against the conditions in your own place or organisation;</li>
      <li>use facilitated action learning and peer challenge to improve judgement; and</li>
      <li>build a practical 100-day plan with people who can help move the work.</li>
    </ul>

    <h2>What you should leave with</h2>
    <p>A clearer outcome. A more honest account of the system producing the present result. Better choices about where to intervene. Tested next moves, a stronger network and a practical plan for action.</p>
    <p>The useful result is not a certificate on its own. It is being better able to act without pretending that your organisation controls the whole system.</p>
  </article>

  <aside class="page-aside" aria-label="At a glance">
    <h2>At a glance</h2>
    <dl>
      <div><dt>Status</dt><dd>Applications open</dd></div>
      <div><dt>For</dt><dd>People responsible for outcomes that depend on several organisations, professions, providers or communities</dd></div>
      <div><dt>Format</dt><dd>Cross-sector cohort, anchor days, expert sessions, action learning, peer challenge and live challenge work</dd></div>
      <div><dt>Start</dt><dd>January 2027</dd></div><div><dt>Timetable</dt><dd>Exact dates and the full timetable are to be confirmed.</dd></div>
      <div><dt>Fee</dt><dd>£2,490 excluding VAT per participant; group and host discounts are available</dd></div>
    </dl>
    <a class="button button-gold" href="mailto:info@publicservicetransformation.org?subject=National%20Commissioning%20Academy%20January%202027">Apply or ask a question</a>
  </aside>
</div>

<section class="section section-tint">
  <div class="shell">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Bring the people who can move it</p>
        <h2>Come alone if you must. Bring a team if you can.</h2>
      </div>
      <p>The Academy is strongest when learning can travel straight into shared decisions and live work.</p>
    </div>
    <div class="feature-panel">
      <div class="feature-copy">
        <p>A useful three-person team might include someone shaping commissioning or strategy, someone close to delivery, and a colleague or partner who sees another part of the system.</p>
        <p>Identify a senior sponsor who can help frame the challenge, protect time for application, open access to decisions and support action on the resulting 100-day plan.</p>
        <p><strong>Three-person team price: £6,349.50 excluding VAT.</strong> The standard 15% group discount applies to bookings of three or more places. Organisations willing to host an anchor day can also discuss host pricing.</p>
      </div>
      <div>
        <a class="button button-gold" href="mailto:david.mason@publicservicetransformation.org?subject=National%20Commissioning%20Academy%20team%20conversation">Book a 20-minute team-fit conversation</a>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="shell">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Evidence from earlier cohorts</p>
        <h2>Learning that travels back into the work</h2>
      </div>
      <p>Participants have used the Academy to translate sessions into organisational action, place commissioning at the centre of wider transformation, and develop a focused 100-day plan for victims and witnesses.</p>
    </div>
    <div class="credibility-grid" aria-label="Reported outcomes">
      <div class="credibility-item"><strong>98%</strong><span>made useful connections</span></div>
      <div class="credibility-item"><strong>91%</strong><span>rated it a good or excellent use of time</span></div>
      <div class="credibility-item"><strong>91%</strong><span>found it relevant or highly relevant</span></div>
      <div class="credibility-item"><strong>87%</strong><span>would recommend it</span></div>
    </div>
    <p><a class="button button-secondary" href="/commissioning-academy/testimonials/">Read participant experiences</a></p>
  </div>
</section>

<section class="cta-panel">
  <div>
    <p class="eyebrow">Bring the outcome that matters</p>
    <h2>Tell us what is happening, who needs to act, and what cannot wait.</h2>
    <p>Describe the live challenge, the people or organisations involved, and the change you need to make possible. We will help you test whether the Academy is the right place to do the work.</p>
  </div>
  <div class="cta-actions">
    <a class="button button-gold" href="mailto:info@publicservicetransformation.org?subject=National%20Commissioning%20Academy%20January%202027">Apply or ask a question</a>
  </div>
</section>
<!-- PSTA_NCA_2026_END -->
</main>'''

markup, count = re.subn(
    r"<main\b[^>]*>.*?</main>",
    main,
    markup,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit(f"Expected one main element; replaced {count}")

description = (
    "For people responsible for outcomes no one organisation can deliver alone. "
    "Work across boundaries, shape systems and turn a live commissioning challenge into practical action."
)
markup = re.sub(
    r'<meta name="description" content="[^"]*">',
    f'<meta name="description" content="{description}">',
    markup,
    count=1,
)
markup = re.sub(
    r'<meta property="og:description" content="[^"]*">',
    f'<meta property="og:description" content="{description}">',
    markup,
    count=1,
)

page.write_text(markup, encoding="utf-8")

check = page.read_text(encoding="utf-8")
required = [
    "For people responsible for outcomes no one organisation can deliver alone.",
    "The outcome belongs to the whole system",
    "Commissioning as practical system change",
    "Come alone if you must. Bring a team if you can.",
    "Three-person team price: £6,349.50 excluding VAT.",
    "PSTA_NCA_2026_START",
    "PSTA_NCA_2026_END",
]
missing = [item for item in required if item not in check]
if missing:
    raise SystemExit("Missing required Academy copy: " + "; ".join(missing))

print("Applied National Commissioning Academy system-level positioning")
