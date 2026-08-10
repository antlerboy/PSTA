# The PSTA website: operations briefing for David Mason

**Status:** working production website and publishing system  
**Prepared:** 10 August 2026  
**Public site:** https://antlerboy.github.io/PSTA/  
**Repository:** https://github.com/antlerboy/PSTA

This briefing is for David to review the website itself and understand how the operational machinery works: feedback, content changes, news publication, social distribution, newsletter staging, deployment, access, and recovery when something goes wrong.

## What the website is for

The website is intended to do three jobs at once:

- make it easy for a commissioner, transformation lead, senior public servant, or organisational buyer to understand what the PSTA can help with and take a sensible next step;
- provide enough evidence, assurance, programme detail, and contact information for someone checking the PSTA before buying or commissioning work; and
- remain useful to alumni, partners, and practitioners through news, insight, tools, programmes, and community material.

It is deliberately a public website, not a transcript of internal strategy work. Copy should therefore make sense to a visitor who has never spoken to us.

## Public language and factual conventions

Please flag departures from these in the running feedback issue.

- Use **‘the PSTA’** in prose, not bare ‘PSTA’, except where the initials are genuinely functioning as a label, URL, file name, or metadata field.
- Use **‘the National Commissioning Academy’** as the programme name.
- Use **‘the Service Transformation Programme’** as the programme name.
- Use the Oxford comma.
- The current headline reach figure is **2,500+ Academy and Programme graduates across public services**.
- Use **‘See what your system is producing’**, not ‘See what the system is producing’.
- Describe what a visitor needs, can do, will learn, or can buy. Avoid shorthand that assumes internal context such as ‘buyer pressure’, ‘test build’, ‘launch review’, or references to conversations behind the website.

For the September 2026 National Commissioning Academy, the current source material says:

- launch webinar: **Monday 14 September 2026, 10:00–12:30**;
- first full anchor day: **Wednesday 23 September 2026, 10:00–16:30**;
- expected programme period: **September 2026 to February 2027**;
- price: **£2,490 per participant**;
- discounts: available for bookings of three or more and for organisations willing to host an anchor day; and
- primary programme contact: **david.mason@publicservicetransformation.org**.

Do not invent or infer dates, fees, availability, accreditation, evidence claims, partner status, or contact routes for other programmes. If the source is unclear, flag it.

## Partner status used on the website

The partner page is deliberately explicit about different kinds of relationship.

**Formal partners**

- E3M
- Nesta
- The Social Innovation Partnership

**Programme and delivery collaborators**

- RedQuadrant
- Basis

**Informal partner relationships**

- LocalGov Digital
- Browne Jacobson

APACE and Fractal Consulting are not listed as partners. Some programme history may still accurately say that a product or programme was developed with an organisation. That is provenance, not current partner status. If even those historical attributions should be removed, put that decision in the feedback thread rather than silently rewriting the history.

The partner logos are pinned or collected into the site build rather than hot-linked in the published HTML. This reduces the chance of a partner website change breaking the PSTA site.

## The main sections

The current multi-page site includes:

- homepage;
- programmes and individual programme pages;
- the National Commissioning Academy;
- the Service Transformation Programme;
- tools and resources;
- in-house work;
- community;
- partners;
- news and insight;
- about;
- contact;
- policies and assurance;
- privacy;
- accessibility; and
- redirects retained where useful for older PSTA URLs.

## Feedback and website review

There is one continuing website feedback thread:

https://github.com/antlerboy/PSTA/issues/2

Use it for rough observations, missing material, wrong wording, visual problems, programme changes, partner changes, broken links, and ideas for a later iteration. Comments do not need to be polished.

The homepage has a small white square in the extreme bottom-right corner which opens that issue. **Alt+Shift+N** also opens it.

The feedback issue is deliberately separate from the publishing form. A rough note should never accidentally become public news.

## Publishing approved news

The low-friction route is a GitHub issue form. Once David has repository Write access:

1. Open **Issues** in the PSTA repository.
2. Select **New issue**.
3. Choose **Publish a PSTA news item**.
4. Enter the public title, short summary, full story, optional primary link, author, and publication date.
5. Add or amend the suggested social post.
6. Tick the social channels that should receive the item.
7. Choose whether it should enter the newsletter queue.
8. Submit the issue.

The form is at:

https://github.com/antlerboy/PSTA/issues/new?template=publish-news.yml

The automation then checks that the person submitting has Write, Maintain, or Admin permission. If so, it creates a dated Markdown source file in `content/news/`, commits it to `main`, and closes the publishing issue after commenting with the expected public URL.

The website build turns that Markdown into:

- an individual public news page;
- an updated `/news/` index;
- an updated RSS feed at `/news/feed.xml`;
- an entry in the social queue; and
- an entry in the newsletter queue where selected.

Use the publishing form only for copy that is genuinely approved to go public. Drafts and ideas belong in the feedback issue, a document, or a branch/pull request.

## Social publishing and Buffer

The website creates a structured social queue at:

`editorial/social-queue.json`

The current channel vocabulary includes:

- RedQuadrant LinkedIn;
- the PSTA LinkedIn;
- Quadrant Resourcing LinkedIn;
- Benjamin's LinkedIn;
- Benjamin's X / Twitter; and
- other connected Buffer channels where deliberately configured.

There is an optional GitHub workflow which can send newly published items to a receiving automation through the repository secret:

`NEWS_DISTRIBUTION_WEBHOOK_URL`

That receiving automation can be Zapier, Make, n8n, Power Automate, or a small internal endpoint. Its job is to map the channel names above to actual Buffer profiles and create Buffer posts.

**Important current control:** the repository-side route exists, but do not assume automatic Buffer posting is active until the webhook secret, the receiving automation, and the Buffer profile mappings have all been configured and tested. The safe first implementation is to create Buffer drafts or queued posts, not instant posts across every account.

A sensible test is one harmless PSTA news item sent only to the PSTA profile, then progressively add RedQuadrant, Quadrant Resourcing, and Benjamin's profiles after checking formatting and account mapping.

## Newsletter staging and SurveyMonkey

Items marked for the newsletter are written to:

`editorial/newsletter-queue.csv`

The queue contains the publication date, title, summary, public URL, author, and status. It is intended as the editorial input to the existing SurveyMonkey newsletter process.

**It does not currently send or construct a SurveyMonkey newsletter automatically.** That is deliberate for now: a website news item and a composed newsletter are different editorial acts. The useful next automation is to turn queued items into a SurveyMonkey draft or an intermediate editorial queue, while leaving final selection, ordering, and sending under human control.

The RSS feed at https://antlerboy.github.io/PSTA/news/feed.xml can also feed downstream tools if useful.

## What actually gets edited

The repository currently has several layers. They are not all equally suitable for everyday editing.

### `content/news/`

This is the cleanest editable content source. Each approved news item is a Markdown file with metadata at the top. David should normally publish through the issue form rather than editing these by hand, but direct Markdown editing is possible.

### `overrides/`

These are full-page replacements accumulated during the website build. They are copied over the base site before deployment. They are useful operationally but should gradually be reduced as the site is simplified.

### `site-full-text/`

This holds the encoded archive from which the complete static base site is reconstructed. It is build material, not a sensible place for routine editorial work. **Do not hand-edit it.**

### `scripts/build_news.py`

Builds the news pages, news index, RSS feed, social queue, and newsletter queue from `content/news/`.

### `scripts/apply_feedback_iteration.py`

An older transformation pass that still supplies some whole-site wording and programme enrichment. It is retained for the moment, but its original all-site audit is no longer the final authority.

### `scripts/final_public_fix.py`

The final public-site identity and partner pass. It installs the pinned full PSTA wordmark, keeps it on white, builds the controlled partner page and partner logos, retires the APACE and Fractal partner profiles, fixes the feedback route, and runs the final identity/partner audit.

### `.github/workflows/pages.yml`

This is the production deployment recipe. Changes to it affect whether the website builds at all. Treat it as controlled infrastructure, not content.

## How deployment works

A merge or push to `main` triggers **Publish PSTA website** unless only generated editorial queue files changed.

The production sequence is:

1. check out the repository;
2. reconstruct the complete static site from `site-full-text/`;
3. apply `overrides/`;
4. run the older whole-site enrichment pass;
5. build news, RSS, and queues;
6. run the authoritative final public identity and partner pass;
7. run hard checks on the result;
8. upload the complete site as a GitHub Pages artefact; and
9. deploy it to GitHub Pages.

Actions and deployment history are visible here:

https://github.com/antlerboy/PSTA/actions

**A green commit does not by itself mean the public website changed. The `Publish PSTA website` run must complete successfully.** If the build fails, GitHub Pages leaves the previous successful site online. This is why an old version can still be visible even after newer code has been merged.

## Current deployment quality gates

The production workflow is intended to refuse deployment if key conditions are wrong. Current gates include:

- at least 30 page-level `index.html` files;
- the full pinned PSTA logo must exist;
- the homepage must contain the 2,500+ graduate figure;
- the National Commissioning Academy content must include the current £2,490 fee;
- company information must say Registered Social Enterprise;
- the partners page must contain E3M, Nesta, The Social Innovation Partnership, LocalGov Digital, and Browne Jacobson;
- APACE, Fractal Consulting, Alliance for Useful Evidence, and ‘wider partner history’ must not appear on the partner page;
- APACE and Fractal Consulting partner-profile directories must not exist;
- ‘Lead partner RedQuadrant’ must not remain in the public site; and
- the erroneous cropped `twitter-white.png` mark must not be referenced.

The point of these checks is to fail noisily rather than quietly publish a partial, stale, or internally worded website.

## If a deployment fails

Do not keep refreshing the public site. It will normally continue to show the last successful deployment.

Instead:

1. open **Actions**;
2. open the most recent **Publish PSTA website** run;
3. find the first failed step;
4. read that step's log rather than guessing from the public site;
5. fix the cause on a branch;
6. merge only when the branch is coherent; and
7. confirm the new Pages run finishes green before treating the change as live.

If the change is risky or difficult to diagnose, revert the offending merge and restore a known-good build before continuing.

## Access for David and Natasa

At the time this briefing was prepared, the repository collaborator list still contained only Benjamin's `antlerboy` account. David and Natasa therefore still need to be invited.

Benjamin can do that here:

https://github.com/antlerboy/PSTA/settings/access

Use **Add people**, invite the GitHub account belonging to David or Natasa, and give each **Write** access after acceptance.

Write access is enough to:

- use the approved-news publishing form;
- edit content files;
- create branches;
- open pull requests; and
- participate fully in editorial changes.

A normal GitHub account is enough to comment in the public feedback issue. Routine content editors do not need Admin access.

## What kind of change should use which route

**Rough observation, typo report, missing material, visual problem**  
Add a comment to issue #2.

**Approved news or programme announcement**  
Use the ‘Publish a PSTA news item’ issue form.

**Minor permanent page-copy change**  
Edit on a branch and open a pull request, or put the precise requested change in issue #2 for the next site iteration.

**Programme offer, price, dates, contact route, evidence claim, partner status**  
Treat as controlled factual content. Use a branch/pull request and have another person check the source before merge.

**Navigation, design, identity, legal/policy wording, deployment workflow**  
Use a branch and pull request. Check the complete Pages build after merge.

**Generated files under `editorial/`**  
Do not treat them as primary content; they are rebuilt from the news sources.

## Current operational links

- Public website: https://antlerboy.github.io/PSTA/
- Partner page: https://antlerboy.github.io/PSTA/partners/
- News: https://antlerboy.github.io/PSTA/news/
- RSS: https://antlerboy.github.io/PSTA/news/feed.xml
- Repository: https://github.com/antlerboy/PSTA
- Actions/deployments: https://github.com/antlerboy/PSTA/actions
- Running feedback: https://github.com/antlerboy/PSTA/issues/2
- Publish-news form: https://github.com/antlerboy/PSTA/issues/new?template=publish-news.yml
- News source: https://github.com/antlerboy/PSTA/tree/main/content/news
- Social queue: https://github.com/antlerboy/PSTA/blob/main/editorial/social-queue.json
- Newsletter queue: https://github.com/antlerboy/PSTA/blob/main/editorial/newsletter-queue.csv
- Repository access: https://github.com/antlerboy/PSTA/settings/access
- Publishing notes: https://github.com/antlerboy/PSTA/blob/main/docs/NEWS_AND_SOCIAL_PUBLISHING.md
- Editing/access notes: https://github.com/antlerboy/PSTA/blob/main/docs/EDITING_AND_ACCESS.md

## What I want David to review now

Please review the site as a prospective buyer and as the person who has to keep the programme information current. In particular, check:

- whether the homepage explains the PSTA to somebody arriving cold;
- whether the calls to action are the ones you would actually want a prospect to take;
- the National Commissioning Academy dates, price, offer, evidence, and contact route;
- the Service Transformation Programme description and contact links;
- every programme page for out-of-date dates, fees, availability, or programme names;
- the partner classification and whether each partner description is current;
- the partner logos and links;
- the 2,500+ graduate claim and any other evidence figures;
- contact email addresses, telephone numbers, and physical address;
- the first generated news item and whether its style is suitable for the public website;
- whether the proposed social-channel list matches the accounts we genuinely want David to control through Buffer;
- whether the newsletter queue contains enough information for the SurveyMonkey workflow; and
- any privacy, accessibility, policy, or assurance wording you would not be comfortable publishing as an organisational statement.

Put findings in issue #2. They can be terse. A page URL plus ‘this is wrong because…’ is enough.

## A simple operating rhythm

A workable light-touch routine would be:

**Weekly:** check issue #2; check for failed Actions runs; check imminent programme dates; publish any approved news; look at the social queue; and move suitable items into the newsletter planning process.

**Before every programme campaign:** verify dates, price, booking/contact route, host/group discounts, evidence, and named partners against the current marketing source.

**Monthly:** scan partners, links, programme status, contact details, and assurance pages; remove stale announcements; review whether any queued newsletter items have already been used.

**After any substantial website change:** check the production Pages run is green, then inspect the homepage, relevant programme page, partners, contact, and mobile layout rather than assuming the merge equals a deployment.

## What is still to set up

The core website, feedback route, news source, RSS, queues, and deployment mechanism exist. These operational pieces still need a human/account-level decision or setup:

1. invite David and Natasa to the repository with Write access;
2. connect `NEWS_DISTRIBUTION_WEBHOOK_URL` to a tested Buffer-routing automation;
3. map the actual Buffer profiles for RedQuadrant, the PSTA, Quadrant Resourcing, and Benjamin's accounts;
4. decide whether social items should land as drafts, queued posts, or scheduled posts — drafts/queue are safer initially;
5. decide how far to automate transfer from `newsletter-queue.csv` into SurveyMonkey while retaining final editorial control; and
6. after the website is signed off, decide when to move `www.publicservicetransformation.org` to this build.

There is also a maintainability job worth doing after content and design settle. The website works, but the non-news base currently lives as a reconstructed static archive plus overrides and transformation scripts. That is robust enough for iteration but not the cleanest long-term editing model for David. News is already easy to publish. The next technical tidy-up should turn the ordinary pages into straightforward source files or a small static-site content system, while retaining GitHub Pages, the issue-based publishing route, the feedback thread, and the deployment checks.
