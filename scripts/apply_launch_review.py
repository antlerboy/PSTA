#!/usr/bin/env python3
"""Apply the final public-launch content, migration, and domain pass.

This runs last in the Pages build. It deliberately owns release-only concerns:
production paths, search indexing, the custom domain, repaired programme pages,
high-value legacy redirects, and copy that must not expose build notes.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "deploy")
REPO = Path(__file__).resolve().parents[1]
DOMAIN = "https://www.publicservicetransformation.org"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="ignore")


def write(path: str, value: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value, encoding="utf-8")


def replace_once(value: str, pattern: str, replacement: str, label: str) -> str:
    value, count = re.subn(pattern, replacement, value, count=1, flags=re.I | re.S)
    if count != 1:
        raise SystemExit(f"Could not replace {label}; matches: {count}")
    return value


def update_json_ld(markup: str, *, course_name: str | None = None,
                   description: str | None = None, canonical: str | None = None,
                   audience: str | None = None) -> str:
    pattern = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.I | re.S)

    def amend(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(2))
        except json.JSONDecodeError:
            return match.group(0)
        objects = data if isinstance(data, list) else [data]
        for item in objects:
            if not isinstance(item, dict):
                continue
            if item.get("@type") == "Course" and course_name:
                item["name"] = course_name
                item["description"] = description
                item["url"] = canonical
                if audience:
                    item["audience"] = {"@type": "Audience", "audienceType": audience}
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    return pattern.sub(amend, markup)


def page_from_template(template: str, destination: str, *, title: str,
                       description: str, canonical_path: str, main: str,
                       course_name: str | None = None,
                       audience: str | None = None) -> None:
    markup = read(template)
    canonical = DOMAIN + canonical_path
    markup = replace_once(markup, r"<title>.*?</title>",
                          f"<title>{html.escape(title)}</title>", "page title")
    markup = replace_once(
        markup,
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{html.escape(description, quote=True)}">',
        "meta description",
    )
    markup = replace_once(
        markup,
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{canonical}">',
        "canonical URL",
    )
    markup = re.sub(
        r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{html.escape(title.split(" | ")[0], quote=True)}">',
        markup,
        count=1,
        flags=re.I,
    )
    markup = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{html.escape(description, quote=True)}">',
        markup,
        count=1,
        flags=re.I,
    )
    markup = re.sub(
        r'<meta property="og:url" content="[^"]*">',
        f'<meta property="og:url" content="{canonical}">',
        markup,
        count=1,
        flags=re.I,
    )
    markup = update_json_ld(
        markup,
        course_name=course_name,
        description=description,
        canonical=canonical,
        audience=audience,
    )
    markup = replace_once(markup, r"<main\b[^>]*>.*?</main>", main, "main content")
    write(destination, markup)


def cta_panel() -> str:
    return '''<section class="cta-panel"><div><p class="eyebrow">Start with the work</p><h2>Tell us what is happening, who needs to act, and what cannot wait.</h2><p>We will help you decide whether a short diagnostic, an in-house cohort, a place-based academy, or an existing programme is the sensible next move.</p></div><div class="cta-actions"><a class="button button-gold" href="/PSTA/contact/">Talk to us</a><a class="text-link light" href="/PSTA/in-house/">See how in-house work starts →</a></div></section>'''


def repair_programme_pages() -> None:
    simulation_description = (
        "An immersive two-day commissioning simulation for public service teams to test "
        "strategy, collaboration, resource choices, and performance decisions without real-world risk."
    )
    simulation_main = f'''<main id="main-content" class="site-main">
<section class="page-hero page-hero-programme"><div class="shell"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/PSTA/">Home</a><span aria-hidden="true">/</span><a href="/PSTA/programmes/">Programmes</a><span aria-hidden="true">/</span><span>Commissioning simulation</span></nav><p class="eyebrow">Immersive two-day programme</p><div class="page-hero-heading"><div><h1>Commissioning simulation</h1><p class="lede">Face the consequences of strategic and operational decisions in a live but risk-free environment.</p></div><span class="status status-large is-current">Available in-house</span></div></div></section>
<div class="shell content-with-aside"><article class="prose">
<h2 id="strategy-meets-operations">Strategy meets operations</h2>
<p>The simulation places participants inside a changing public service system. Decisions made in one part of the system alter the pressures, relationships, resources, and outcomes elsewhere.</p>
<p>Because the consequences become visible during the programme, teams can examine their assumptions and try a different move without putting a real service or relationship at risk.</p>
<h2 id="what-participants-work-through">What participants work through</h2>
<ul><li>Managing a service as part of a wider system.</li><li>Deciding whether, where, and how to collaborate with other services and organisations.</li><li>Allocating limited resources across services with different needs.</li><li>Designing a performance framework with timely, useful measures.</li><li>Seeing how strategy and day-to-day operations interact.</li><li>Tracing the social consequences of management decisions.</li></ul>
<h2 id="what-previous-groups-valued">What previous groups valued</h2>
<p>Participants have described the simulation as a strong way to compare strategic options, see how teams and relationships work in practice, and think hard about the consequences of their choices.</p>
<p>It works particularly well for a group that needs a shared experience before tackling a live commissioning, partnership, or transformation challenge.</p>
<h2 id="how-it-runs">How it runs</h2>
<p>The simulation normally runs over two consecutive days for an organisational or cross-system cohort. We agree group size, location, facilitation, and price for each run.</p>
</article><aside class="page-aside" aria-label="At a glance"><h2>At a glance</h2><dl><div><dt>Status</dt><dd>Available in-house</dd></div><div><dt>For</dt><dd>Commissioners, managers, transformation teams, and system partners</dd></div><div><dt>Format</dt><dd>Facilitated, immersive simulation with reflection and debrief</dd></div><div><dt>Time</dt><dd>Two consecutive days</dd></div></dl><a class="button button-gold" href="mailto:sarah.johnston@publicservicetransformation.org?subject=Commissioning%20simulation">Ask about a team simulation</a></aside></div>
{cta_panel()}</main>'''
    page_from_template(
        "programmes/contract-management-development/index.html",
        "programmes/commissioning-simulation/index.html",
        title="Commissioning simulation | The Public Service Transformation Academy",
        description=simulation_description,
        canonical_path="/programmes/commissioning-simulation/",
        main=simulation_main,
        course_name="Commissioning simulation",
        audience="Commissioners, managers, transformation teams and system partners",
    )

    ten_step_description = (
        "An interactive three-day introduction to the principles and practice of public service "
        "commissioning, with reflection, action learning, and practical application."
    )
    ten_step_main = f'''<main id="main-content" class="site-main">
<section class="page-hero page-hero-programme"><div class="shell"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/PSTA/">Home</a><span aria-hidden="true">/</span><a href="/PSTA/programmes/">Programmes</a><span aria-hidden="true">/</span><span>Commissioning: a 10-step introduction</span></nav><p class="eyebrow">Entry-level programme</p><div class="page-hero-heading"><div><h1>Commissioning: a 10-step introduction</h1><p class="lede">Grasp the principles of effective commissioning, apply them quickly, and build a network for support and challenge.</p></div><span class="status status-large is-current">Available for cohorts</span></div></div></section>
<div class="shell content-with-aside"><article class="prose">
<h2 id="commissioning-as-a-mindset">Commissioning as a mindset</h2>
<p>This intensive introduction helps people develop public services that make a positive and lasting difference to local lives. It treats commissioning as a way of working with outcomes, citizens, resources, quality, partners, procurement, values, and innovation.</p>
<p>The programme was originally co-developed with the Association of Policing and Crime Chief Executives. It complements the deeper National Commissioning Academy.</p>
<h2 id="how-the-learning-works">How the learning works</h2>
<p>Three interactive programme days are normally spaced about two weeks apart. Participants can reflect, practise between sessions, and use a small action-learning set that may continue after the programme.</p>
<p>The title reflects ten core commissioning questions. A final eleventh question turns the learning into action.</p>
<ol><li><strong>What are we doing anyway?</strong></li><li><strong>What is commissioning?</strong></li><li><strong>Do we have to talk about leadership?</strong></li><li><strong>Are members of the public just customers?</strong></li><li><strong>How do we make the most of our resources?</strong></li><li><strong>Where does quality come into commissioning?</strong></li><li><strong>Can we talk about procurement now?</strong></li><li><strong>Where do our values fit in?</strong></li><li><strong>How can we work best with our partners?</strong></li><li><strong>How can we design in creativity and innovation?</strong></li><li><strong>What now?</strong></li></ol>
<h2 id="what-participants-leave-with">What participants leave with</h2>
<p>Participants should be able to act with more confidence, use a commissioning mindset in live work, and call on peers for practical support and challenge.</p>
</article><aside class="page-aside" aria-label="At a glance"><h2>At a glance</h2><dl><div><dt>Status</dt><dd>Available for cohorts</dd></div><div><dt>For</dt><dd>People who are new to commissioning or need a shared foundation</dd></div><div><dt>Format</dt><dd>Interactive learning, practice between sessions, and action learning</dd></div><div><dt>Time</dt><dd>Three days, normally spaced about two weeks apart</dd></div></dl><a class="button button-gold" href="mailto:sarah.johnston@publicservicetransformation.org?subject=Commissioning%2010-step%20introduction">Ask about a cohort</a></aside></div>
{cta_panel()}</main>'''
    page_from_template(
        "programmes/contract-management-development/index.html",
        "programmes/commissioning-ten-step-introduction/index.html",
        title="Commissioning: a 10-step introduction | The Public Service Transformation Academy",
        description=ten_step_description,
        canonical_path="/programmes/commissioning-ten-step-introduction/",
        main=ten_step_main,
        course_name="Commissioning: a 10-step introduction",
        audience="People who are new to commissioning or need a shared foundation",
    )


def participant_card(name: str, role: str, summary: str) -> str:
    return f'''<article class="card participant-card"><p class="eyebrow">What they valued</p><h2>{html.escape(name)}</h2><p>{html.escape(summary)}</p><p class="participant-role">{html.escape(role)}</p></article>'''


def write_participant_experiences() -> None:
    experiences = [
        ("Gareth Symonds", "Assistant Director of Commissioning, Surrey County Council", "Peer discussion about needs, innovation, outcomes, and transformation felt empowering."),
        ("Theresa Chambers", "Home Office", "The academy gave useful insight into commissioning services around what citizens need."),
        ("Mathew Kendall", "Assistant Director, Adult Social Care and Health, Barnet", "Joining with colleagues made it easier to translate each session into organisational action."),
        ("Eddie Pinkard", "Head of Transformation, States of Guernsey", "The experience placed better commissioning at the centre of a wider transformation journey."),
        ("Steve Scott", "Department for Work and Pensions", "The combination of theory and practical examples supported both personal development and work."),
        ("Mike Wheatley", "Prison Substance Misuse Co-Commissioning, National Offender Management Service", "The network and learning created an opportunity to return to the organisation and lead by example."),
        ("Linda Uren", "Gloucestershire County Council", "Provider perspectives, investment in communities, and the financial context prompted different thinking."),
        ("Jacqui McKinlay", "Director of Customer Services and Communications, Staffordshire County Council", "Time to think, varied speakers, and visits reinforced that commissioning is about people and the right questions, not only procurement."),
        ("Julie Taylor", "Assistant Chief Executive, London Borough of Barnet", "Cross-public-sector participation created valuable peer learning through shared experience and expertise."),
        ("Damian Roberts", "Strategic Director, Waverley Borough Council", "The academy made commissioning more accessible as good strategic management, from citizen insight to partnership relationships."),
        ("Office of the Police and Crime Commissioner for Leicestershire", "Participant group", "Protected thinking time, guest speakers, and peer challenge helped the group develop a focused 100-day plan for victims and witnesses."),
        ("Tom Woodcock", "Public Health Commissioning, Lancashire County Council", "Current thinking from government, provider input, commissioner experience, and debate made the programme valuable."),
    ]
    cards = "".join(participant_card(*item) for item in experiences)
    main = f'''<main id="main-content" class="site-main">
<section class="page-hero"><div class="shell"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/PSTA/">Home</a><span aria-hidden="true">/</span><a href="/PSTA/programmes/national-commissioning-academy/">The National Commissioning Academy</a><span aria-hidden="true">/</span><span>Participant experiences</span></nav><p class="eyebrow">Evidence from the work</p><h1>Participant experiences</h1><p class="lede">What people took from the National Commissioning Academy and used back in their organisations.</p></div></section>
<section class="section"><div class="shell"><div class="credibility-grid" aria-label="Reported outcomes"><div class="credibility-item"><strong>98%</strong><span>made useful connections</span></div><div class="credibility-item"><strong>91%</strong><span>rated it a good or excellent use of time</span></div><div class="credibility-item"><strong>91%</strong><span>found it relevant or highly relevant</span></div><div class="credibility-item"><strong>87%</strong><span>would recommend it</span></div></div><div class="section-heading"><div><p class="eyebrow">Across public services</p><h2>Learning that travels back into the work</h2></div><p>These summaries preserve participant feedback from earlier academy cohorts. Roles are shown as they were when the feedback was published.</p></div><div class="participant-grid">{cards}</div><p><a class="button button-gold" href="/PSTA/programmes/national-commissioning-academy/">View the current academy</a></p></div></section>
{cta_panel()}</main>'''
    page_from_template(
        "policies/index.html",
        "commissioning-academy/testimonials/index.html",
        title="Participant experiences | The Public Service Transformation Academy",
        description="Participant experiences and reported outcomes from National Commissioning Academy cohorts across public services.",
        canonical_path="/commissioning-academy/testimonials/",
        main=main,
    )


def replace_main(path: str, main: str) -> None:
    markup = read(path)
    markup = replace_once(markup, r"<main\b[^>]*>.*?</main>", main, f"main content in {path}")
    write(path, markup)


def update_assurance_pages() -> None:
    policies_main = '''<main id="main-content" class="site-main"><section class="page-hero"><div class="shell"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/PSTA/">Home</a><span aria-hidden="true">/</span><span>Policies and assurance</span></nav><p class="eyebrow">Clear public information</p><h1>Policies and assurance</h1><p class="lede">Legal, accessibility, privacy, and organisational assurance information for the Public Service Transformation Academy.</p></div></section><div class="shell prose prose-wide">
<h2 id="public-information">Public information</h2><ul><li><a href="/PSTA/privacy/">Privacy notice</a>: what this website collects, why, and how to contact us about personal information.</li><li><a href="/PSTA/accessibility/">Accessibility statement</a>: how the website has been checked, known limits, and how to report a problem.</li><li><a href="/PSTA/about/">About the academy</a>: our purpose, origins, social-enterprise status, and company information.</li></ul>
<h2 id="organisational-policies">Organisational policies and due diligence</h2><p>We do not publish every internal policy on the open web. If you are procuring from, commissioning, or partnering with us, email <a href="mailto:info@publicservicetransformation.org?subject=Supplier%20due%20diligence">info@publicservicetransformation.org</a> with the documents or evidence your process requires.</p><p>We will confirm what applies to the proposed work and provide the current approved material. This may include insurance, data-protection arrangements, equality and inclusion, safeguarding, environmental commitments, complaints, and quality assurance.</p>
<h2 id="company-information">Company information</h2><p>The Public Service Transformation Academy Limited is a company limited by guarantee, registered in England and Wales, company number 10046052. VAT number 244 4776 87. Registered office: 7 Bell Yard, London, WC2A 2JR, UK.</p>
</div></main>'''
    replace_main("policies/index.html", policies_main)

    accessibility_main = '''<main id="main-content" class="site-main"><section class="page-hero"><div class="shell"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/PSTA/">Home</a><span aria-hidden="true">/</span><span>Accessibility statement</span></nav><p class="eyebrow">Access for everyone</p><h1>Accessibility statement</h1><p class="lede">We want the Public Service Transformation Academy website to be usable by as many people as possible.</p></div></section><div class="shell prose prose-wide">
<p><strong>Last reviewed: 2 September 2026.</strong></p>
<h2 id="using-this-website">Using this website</h2><p>The site uses a consistent heading structure, keyboard-operable navigation, visible focus states, descriptive links, responsive layouts, and high-contrast text. Essential meaning is not conveyed by colour alone.</p><p>There is no autoplay, essential animation, third-party embed, or complex web form. Text can be enlarged, layouts reflow on narrow screens, and reduced-motion preferences are respected.</p>
<h2 id="how-we-checked-it">How we checked it</h2><p>Before release, we ran structural checks across every public page, checked internal links and alternative text, used keyboard-only navigation on representative pages, tested the narrow-screen navigation, and reviewed text and interface colour contrast.</p><p>This was an internal release review, not an independent accessibility audit or a full assistive-technology test matrix. The site is designed towards the Web Content Accessibility Guidelines version 2.2, level AA.</p>
<h2 id="known-limits">Known limits</h2><ul><li>Files, tools, or services reached through external links may have their own accessibility limits.</li><li>New partner-supplied documents, images, and video need accessibility checks before publication.</li><li>A future independent audit may identify issues that these release checks did not find.</li></ul>
<h2 id="report-a-problem">Report a problem</h2><p>Email <a href="mailto:info@publicservicetransformation.org?subject=Website%20accessibility">info@publicservicetransformation.org</a>. Include the page, the problem, and the browser or assistive technology you were using. We will try to provide the information another way and fix the underlying issue.</p>
</div></main>'''
    replace_main("accessibility/index.html", accessibility_main)


def update_sales_and_migration_copy() -> None:
    for path in ROOT.rglob("*.html"):
        markup = path.read_text(encoding="utf-8", errors="ignore")
        markup = markup.replace(
            "The National Commissioning Academy: next cohort expected September 2026 to February 2027",
            "National Commissioning Academy applications are open: September 2026 to February 2027",
        )
        markup = markup.replace(
            "The National Commissioning Academy: September 2026 to February 2027",
            "National Commissioning Academy applications are open: September 2026 to February 2027",
        )
        markup = markup.replace("Expected September 2026 to February 2027", "September 2026 to February 2027")
        markup = markup.replace("Register interest", "Applications open")
        markup = markup.replace("Commissioning: a 10 step introduction", "Commissioning: a 10-step introduction")
        markup = markup.replace(
            '>Applications open <span aria-hidden="true">→</span></a>',
            '>View dates and fees <span aria-hidden="true">→</span></a>',
        )
        markup = markup.replace("The next the National Commissioning Academy", "The next National Commissioning Academy")
        markup = markup.replace("The Academy and Programme graduates across public services", "Academy and programme graduates across public services")
        markup = markup.replace(
            "a short diagnostic, an in-house cohort, a place-based academy or an existing programme",
            "a short diagnostic, an in-house cohort, a place-based academy, or an existing programme",
        )
        markup = markup.replace(
            "You should be better able to see how the wider system is shaping results, define outcomes more sharply, work across boundaries, make better use of insight and evidence, and intervene without pretending that any one organisation controls the whole system.",
            "You should be better able to see how the wider system is shaping results, define outcomes more sharply, and work across boundaries. You should also make better use of insight and evidence, and intervene without pretending that any one organisation controls the whole system.",
        )
        markup = markup.replace(
            "We will ask what outcome matters, where the current system is producing something else, who can authorise or obstruct action, what the cohort can change while the programme runs, and what evidence would make the first phase worthwhile.",
            "We will ask what outcome matters, where the current system is producing something else, and who can authorise or obstruct action. We will also identify what the cohort can change while the programme runs and what evidence would make the first phase worthwhile.",
        )
        markup = markup.replace(
            "Compass v2.0 asks a wider question than ‘how well are we running the commissioning cycle?’ It looks at how a place forms the relationships, capabilities, arrangements and conditions through which people can live well.",
            "Compass v2.0 asks a wider question: how well are we shaping the whole system? It examines how a place forms the relationships, capabilities, and arrangements that help people live well.",
        )
        markup = markup.replace("The main programme is expected to run to February 2027.", "The main programme runs to February 2027.")
        markup = re.sub(
            r'href="mailto:david\.mason@publicservicetransformation\.org\?subject=A%20conversation%20about%20a%20Public%20Service%20Transformation%20Academy%20programme"',
            'href="/PSTA/contact/"',
            markup,
        )
        if path.relative_to(ROOT).as_posix() != "contact/index.html":
            markup = re.sub(
                r'href="mailto:david\.mason@publicservicetransformation\.org[^"]*"',
                'href="/PSTA/contact/"',
                markup,
            )
        path.write_text(markup, encoding="utf-8")

    home = read("index.html")
    home = home.replace("<div><dt>Expected</dt><dd>September 2026 to February 2027</dd></div>", "<div><dt>Dates</dt><dd>September 2026 to February 2027</dd></div>")
    home = home.replace(
        "<h2>The National Commissioning Academy</h2>\n<p>A flagship cross-sector programme",
        "<h2>The National Commissioning Academy</h2>\n<p><strong>Applications are open for the September 2026 cohort.</strong></p>\n<p>A flagship cross-sector programme",
        1,
    )
    testimonial_end = "</div>\n</div>\n</section>\n<section class=\"section section-gold\">"
    if "/commissioning-academy/testimonials/" not in home and testimonial_end in home:
        home = home.replace(
            testimonial_end,
            '</div>\n<p><a class="button button-gold" href="/PSTA/commissioning-academy/testimonials/">Read more participant experiences</a></p>\n</div>\n</section>\n<section class="section section-gold">',
            1,
        )
    home = home.replace(
        '<div class="hero-graphic" aria-label=',
        '<div class="hero-graphic" role="img" aria-label=',
        1,
    )
    write("index.html", home)

    nca = read("programmes/national-commissioning-academy/index.html")
    nca = nca.replace(
        '<p class="lede">A flagship cross-sector programme for people who need to improve outcomes by working with the whole system, not only individual services, contracts or procurement processes.</p></div><span class="status status-large is-open">Applications open</span>',
        '<p class="lede">A flagship cross-sector programme for people who need to improve outcomes by working with the whole system, not only individual services, contracts or procurement processes.</p><p class="hero-note"><strong>September 2026 to February 2027 · £2,490 per participant</strong></p><div class="hero-actions"><a class="button button-gold" href="mailto:info@publicservicetransformation.org?subject=National%20Commissioning%20Academy%20September%202026">Apply or ask a question</a></div></div><span class="status status-large is-open">Applications open</span>',
        1,
    )
    nca = re.sub(
        r'<h2 id="next-cohort">Next cohort</h2>\s*<p>.*?</p>',
        '<h2 id="next-cohort">Applications are open</h2><p>The next national cohort runs from September 2026 to February 2027. Contact us about fit, dates, group places, or the live challenge you would bring.</p>',
        nca,
        count=1,
        flags=re.I | re.S,
    )
    nca = nca.replace('<dt>Status</dt><dd>Applications open</dd>', '<dt>Status</dt><dd>Applications open</dd>')
    nca = re.sub(
        r'href="/PSTA/contact/">Applications open</a>',
        'href="mailto:info@publicservicetransformation.org?subject=National%20Commissioning%20Academy%20September%202026">Apply or ask a question</a>',
        nca,
    )
    nca = nca.replace(
        '<div><dt>Time</dt><dd>September 2026 to February 2027</dd></div></dl>',
        '<div><dt>Time</dt><dd>September 2026 to February 2027</dd></div><div><dt>Fee</dt><dd>£2,490 per participant; group and host discounts are available</dd></div></dl>',
        1,
    )
    nca = nca.replace(
        '<div class="feature-panel">\n      <div>\n        <h3>Bring a live challenge and leave with practical action</h3>',
        '<div class="feature-panel">\n      <div class="feature-copy">\n        <h3>Bring a live challenge and leave with practical action</h3>',
        1,
    )
    nca = nca.replace(
        "<h3>What previous participants reported</h3>",
        '<h3>What previous participants reported</h3>',
    )
    nca = nca.replace(
        "</div>\n  </div>\n</section>\n<!-- PSTA_NCA_2026_END -->",
        '</div><p><a class="button button-secondary" href="/PSTA/commissioning-academy/testimonials/">Read participant experiences</a></p>\n  </div>\n</section>\n<!-- PSTA_NCA_2026_END -->',
        1,
    )
    write("programmes/national-commissioning-academy/index.html", nca)

    home = read("index.html")
    home = home.replace(
        '>Explore the academy</a>',
        '>View dates, fees, and how to apply</a>',
        1,
    )
    write("index.html", home)

    contact = read("contact/index.html")
    contact = contact.replace(
        '<p>Email <a href="mailto:david.mason@publicservicetransformation.org?subject=Programme%20enquiry">david.mason@publicservicetransformation.org</a> with three things:</p>',
        '<p>David Mason is the named contact for programme and organisation enquiries. Email <a href="mailto:david.mason@publicservicetransformation.org?subject=Programme%20enquiry">david.mason@publicservicetransformation.org</a> with three things:</p>',
    )
    write("contact/index.html", contact)

    insights = read("insights/index.html")
    insights = re.sub(
        r'<h2 id="older-archive">Older archive</h2>\s*<p>.*?</p>',
        '<h2 id="what-moved-from-the-former-site">What moved from the former site</h2><p>We kept current programme detail, Commissioning Academy participant evidence, the Compass tools, and evergreen case material that still helps people act. Time-expired announcements and duplicated archive pages were not carried forward.</p><p><a href="/PSTA/commissioning-academy/testimonials/">Read participant experiences</a> or <a href="/PSTA/news/">see current news</a>.</p>',
        insights,
        count=1,
        flags=re.I | re.S,
    )
    write("insights/index.html", insights)

    somerset = read("insights/somerset-academies-case-study/index.html")
    somerset = re.sub(
        r'<p><a href="https://www\.publicservicetransformation\.org/resources-2/somerset-academies-creating-a-more-integrated-approach-to-health-and-social-care/">.*?</a>\.</p>',
        '<p>This page carries forward the evergreen findings from the original Somerset case study.</p>',
        somerset,
        count=1,
        flags=re.I | re.S,
    )
    write("insights/somerset-academies-case-study/index.html", somerset)


def replace_remote_partner_images() -> None:
    path = ROOT / "partners/index.html"
    markup = path.read_text(encoding="utf-8", errors="ignore")

    def fallback(match: re.Match[str]) -> str:
        name = html.escape(html.unescape(match.group(1)))
        return f'<div class="partner-logo-wrap" aria-hidden="true"><span class="partner-logo-fallback">{name}</span></div>'

    markup = re.sub(
        r'<div class="partner-logo-wrap"><img class="partner-logo"[^>]*alt="([^"]+)"[^>]*></div>',
        fallback,
        markup,
        flags=re.I,
    )
    path.write_text(markup, encoding="utf-8")

    for profile in (ROOT / "partners").glob("*/index.html"):
        profile_markup = profile.read_text(encoding="utf-8", errors="ignore")

        def profile_fallback(match: re.Match[str]) -> str:
            name = html.escape(html.unescape(match.group(1)))
            return f'<div class="partner-hero-logo" aria-hidden="true"><span class="partner-logo-fallback">{name}</span></div>'

        profile_markup = re.sub(
            r'<div class="partner-hero-logo"><img[^>]*alt="([^"]+)"[^>]*></div>',
            profile_fallback,
            profile_markup,
            flags=re.I,
        )
        profile_markup = profile_markup.replace(
            "the accredited the Service Transformation Programme",
            "the accredited Service Transformation Programme",
        )
        profile.write_text(profile_markup, encoding="utf-8")


def write_redirect(path: str, destination: str, label: str) -> None:
    title = f"{label} has moved | The Public Service Transformation Academy"
    canonical = DOMAIN + destination
    page = f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex, follow"><meta http-equiv="refresh" content="0; url={destination}"><link rel="canonical" href="{canonical}"><title>{html.escape(title)}</title></head>
<body><main id="main-content"><h1>{html.escape(label)} has moved</h1><p>Continue to <a href="{destination}">{html.escape(label)}</a>.</p></main></body></html>'''
    write(path.strip("/") + "/index.html", page)


def write_legacy_redirects() -> None:
    redirects = {
        "/commissioning-academy/": ("/programmes/national-commissioning-academy/", "The National Commissioning Academy"),
        "/contact-us/": ("/contact/", "Contact"),
        "/the-psta/contact-us/": ("/contact/", "Contact"),
        "/privacy-notice/": ("/privacy/", "Privacy notice"),
        "/purpose/": ("/about/", "Our purpose"),
        "/resources/": ("/insights/", "Insights and resources"),
        "/features/": ("/insights/", "Features and insight"),
        "/video/": ("/insights/", "Video and insight"),
        "/archive/": ("/insights/", "Archive and insight"),
        "/the-psta/": ("/about/", "About the academy"),
        "/the-psta/partners/": ("/partners/", "Partners"),
        "/related-organisations/": ("/partners/", "Related organisations"),
        "/the-psta/related-organisations/": ("/partners/", "Related organisations"),
        "/leading-transformation/": ("/programmes/leading-transformation/", "Leading Transformation"),
        "/service-transformation-programme/": ("/programmes/service-transformation-programme/", "The Service Transformation Programme"),
        "/contract-management-development-programme/": ("/programmes/contract-management-development/", "Contract Management Development Programme"),
        "/regional-transformation-academy/": ("/programmes/place-based-academies/", "Place-based and regional transformation academies"),
        "/commissioning-and-innovation-playing-on-a-bigger-stage/": ("/programmes/commissioning-and-innovation/", "Commissioning and innovation"),
        "/courses/commissioning-10-step-introduction/": ("/programmes/commissioning-ten-step-introduction/", "Commissioning: a 10-step introduction"),
        "/commissioning-academy/new-commissioning-simulation/": ("/programmes/commissioning-simulation/", "Commissioning simulation"),
        "/commissioning-academy/commissioning-simulation/": ("/programmes/commissioning-simulation/", "Commissioning simulation"),
        "/commissioning-academy/commissioning-health-check/": ("/programmes/commissioning-health-check/", "Commissioning health check"),
        "/resources-2/somerset-academies-creating-a-more-integrated-approach-to-health-and-social-care/": ("/insights/somerset-academies-case-study/", "The Somerset academies case study"),
    }
    for path, (destination, label) in redirects.items():
        write_redirect(path, destination, label)


def ensure_navigation(markup: str) -> str:
    if "site-nav" not in markup or "nav-toggle" in markup:
        return markup
    button = '<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-navigation"><span class="visually-hidden">Open navigation</span><span aria-hidden="true"></span><span aria-hidden="true"></span><span aria-hidden="true"></span></button>'
    markup = re.sub(r'<nav class="site-nav"', button + '<nav id="site-navigation" class="site-nav"', markup, count=1)
    if "site.js" not in markup:
        markup = markup.replace("</body>", '<script src="/assets/js/site.js" defer></script></body>', 1)
    return markup


def ensure_target_blank_rel(markup: str) -> str:
    def amend(match: re.Match[str]) -> str:
        tag = match.group(0)
        rel_match = re.search(r'\brel="([^"]*)"', tag, re.I)
        values = set(rel_match.group(1).split()) if rel_match else set()
        values.update(("noopener", "noreferrer"))
        rel = 'rel="' + " ".join(sorted(values)) + '"'
        if rel_match:
            return tag[:rel_match.start()] + rel + tag[rel_match.end():]
        return tag[:-1] + " " + rel + ">"
    return re.sub(r'<a\b[^>]*\btarget="_blank"[^>]*>', amend, markup, flags=re.I)


def is_non_indexable(path: Path, markup: str) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return (
        "http-equiv=\"refresh\"" in markup.lower()
        or rel in {"404.html", "404/index.html"}
        or rel.startswith("iteration-notes-")
    )


def ensure_head_metadata(path: Path, markup: str) -> str:
    if re.search(r"<html(?!\s[^>]*\blang=)[^>]*>", markup, re.I):
        markup = re.sub(r"<html([^>]*)>", r'<html lang="en-GB"\1>', markup, count=1, flags=re.I)
    if re.search(r"<main(?![^>]*\btabindex=)", markup, re.I):
        markup = re.sub(r"<main(?![^>]*\btabindex=)", '<main tabindex="-1"', markup, count=1, flags=re.I)
    non_indexable = is_non_indexable(path, markup)
    robots = "noindex, follow" if non_indexable else "index, follow"
    tag = f'<meta name="robots" content="{robots}">'
    if re.search(r'<meta name="robots"[^>]*>', markup, re.I):
        markup = re.sub(r'<meta name="robots"[^>]*>', tag, markup, count=1, flags=re.I)
    elif "</head>" in markup:
        markup = markup.replace("</head>", tag + "\n</head>", 1)

    if not non_indexable and not re.search(r'<link rel="canonical"', markup, re.I):
        rel = path.relative_to(ROOT).as_posix()
        route = "/" if rel == "index.html" else "/" + rel.removesuffix("index.html")
        markup = markup.replace("</head>", f'<link rel="canonical" href="{DOMAIN}{route}">\n</head>', 1)
    if not re.search(r'<link rel="icon"', markup, re.I) and "</head>" in markup:
        markup = markup.replace("</head>", '<link rel="icon" href="/assets/img/psta-logo-official.svg" type="image/svg+xml">\n</head>', 1)
    else:
        markup = re.sub(
            r'<link rel="icon" href="/(?:PSTA/)?assets/img/favicon\.png" type="image/png">',
            '<link rel="icon" href="/assets/img/psta-logo-official.svg" type="image/svg+xml">',
            markup,
            flags=re.I,
        )
    return markup


def switch_to_production_root() -> None:
    text_extensions = {".html", ".css", ".js", ".xml", ".txt", ".json"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_extensions:
            continue
        value = path.read_text(encoding="utf-8", errors="ignore")
        feedback_placeholder = "PSTA_GITHUB_FEEDBACK_URL"
        value = value.replace("https://github.com/antlerboy/PSTA/issues/2", feedback_placeholder)
        value = value.replace("https://antlerboy.github.io/PSTA/", DOMAIN + "/")
        value = value.replace("https://antlerboy.github.io/PSTA", DOMAIN)
        value = value.replace("http://eepurl.com", "https://eepurl.com")
        value = value.replace("site.css?v=20260830-4", "site.css?v=20260902-2")
        value = value.replace("site.css?v=20260902-1", "site.css?v=20260902-2")
        value = value.replace("/PSTA/", "/")
        value = value.replace('"/PSTA"', '"/"')
        value = re.sub(
            r'(/assets/js/site\.js)(?:\?v=[^"\']*)?',
            r'\1?v=20260902-1',
            value,
        )
        value = value.replace(feedback_placeholder, "https://github.com/antlerboy/PSTA/issues/2")
        if path.suffix.lower() == ".html":
            value = ensure_navigation(value)
            value = ensure_target_blank_rel(value)
            value = ensure_head_metadata(path, value)
        path.write_text(value, encoding="utf-8")

    build_info = ROOT / "build-info.json"
    if build_info.exists():
        value = build_info.read_text(encoding="utf-8", errors="ignore")
        value = value.replace('"base_path": "/PSTA"', '"base_path": "/"')
        build_info.write_text(value, encoding="utf-8")


def write_release_files() -> None:
    logo_source = REPO / "assets/psta-logo-official.jpg"
    if not logo_source.exists():
        raise SystemExit("The official JPG logo is missing")
    logo_target = ROOT / "assets/img/psta-logo-web.jpg"
    logo_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(logo_source, logo_target)

    (ROOT / "CNAME").write_text("www.publicservicetransformation.org\n", encoding="ascii")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://www.publicservicetransformation.org/sitemap.xml\n",
        encoding="utf-8",
    )

    locations: list[str] = []
    for path in sorted(ROOT.rglob("index.html")):
        markup = path.read_text(encoding="utf-8", errors="ignore")
        if is_non_indexable(path, markup):
            continue
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', markup, re.I)
        if canonical and canonical.group(1).startswith(DOMAIN):
            locations.append(canonical.group(1))
    unique = sorted(set(locations))
    items = "".join(f"  <url><loc>{html.escape(url)}</loc></url>\n" for url in unique)
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + items + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def append_launch_css() -> None:
    path = ROOT / "assets/css/site.css"
    css = path.read_text(encoding="utf-8", errors="ignore")
    marker = "/* PSTA public-launch review */"
    if marker in css:
        return
    css += '''

/* PSTA public-launch review */
.participant-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1.1rem;margin:2rem 0}
.participant-card{display:flex;flex-direction:column}.participant-card h2{font-size:1.3rem}.participant-card .participant-role{margin-top:auto;color:var(--muted);font-size:.85rem;font-weight:700}
.prose ol li+li{margin-top:.45rem}
.feature-copy h3{color:var(--white)}
.section-blue .button-gold{color:var(--black)}
.section-gold .eyebrow{color:var(--black)}
@media(max-width:780px){.participant-grid{grid-template-columns:1fr}}
'''
    path.write_text(css, encoding="utf-8")


def patch_interactions() -> None:
    path = ROOT / "assets/js/site.js"
    script = path.read_text(encoding="utf-8", errors="ignore")
    marker = "PSTA accessible navigation state"
    if marker in script:
        return
    script += '''

// PSTA accessible navigation state
(() => {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.site-nav');
  const label = toggle && toggle.querySelector('.visually-hidden');
  if (!toggle || !nav || !label) return;
  const syncLabel = () => {
    label.textContent = toggle.getAttribute('aria-expanded') === 'true' ? 'Close navigation' : 'Open navigation';
  };
  toggle.addEventListener('click', syncLabel);
  nav.addEventListener('click', syncLabel);
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      toggle.setAttribute('aria-expanded', 'false');
      nav.classList.remove('is-open');
      syncLabel();
      toggle.focus();
    }
  });
  syncLabel();
})();
'''
    path.write_text(script, encoding="utf-8")


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Build root does not exist: {ROOT}")
    repair_programme_pages()
    write_participant_experiences()
    update_assurance_pages()
    update_sales_and_migration_copy()
    replace_remote_partner_images()
    write_legacy_redirects()
    append_launch_css()
    patch_interactions()
    switch_to_production_root()
    write_release_files()
    print("Public-launch review applied: production paths, content, redirects, and indexing are ready")


if __name__ == "__main__":
    main()
