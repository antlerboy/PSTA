# The PSTA website: review and operations briefing for David Mason

## What this is

This repository contains the rebuilt multi-page website for the Public Service Transformation Academy. It is currently published as a GitHub Pages test site at:

https://antlerboy.github.io/PSTA/

The intention is to give the PSTA a public site that is easier to maintain, clearer about what we actually offer, and much less dependent on one person manually editing WordPress.

This document is the working briefing for reviewing the site and then operating it. Please use it as the index to the system rather than trying to infer how the repository works.

## What I need you to review

Please review the site as a public website, rather than as an internal strategy document. In particular, check whether a commissioner, transformation lead, senior public servant, partner, or prospective participant can understand what the PSTA is, what it offers, why it is credible, and what to do next.

The highest-priority pages are:

- Home: https://antlerboy.github.io/PSTA/
- Programmes: https://antlerboy.github.io/PSTA/programmes/
- The National Commissioning Academy: https://antlerboy.github.io/PSTA/programmes/national-commissioning-academy/
- The Service Transformation Programme: https://antlerboy.github.io/PSTA/programmes/service-transformation-programme/
- In-house work: https://antlerboy.github.io/PSTA/in-house/
- Tools: https://antlerboy.github.io/PSTA/tools/
- Community: https://antlerboy.github.io/PSTA/community/
- Partners: https://antlerboy.github.io/PSTA/partners/
- News: https://antlerboy.github.io/PSTA/news/
- About: https://antlerboy.github.io/PSTA/about/
- Contact: https://antlerboy.github.io/PSTA/contact/

Please check programme facts, dates, prices, contact routes, partner descriptions, claims and evidence, and anything that sounds like an internal conversation rather than public copy.

There are some house rules already agreed for the public site. Use 'the PSTA' rather than bare 'PSTA' in prose. Use 'the National Commissioning Academy' and 'the Service Transformation Programme'. Use the Oxford comma. The main graduate claim is '2,500+ Academy and Programme graduates across public services'. The PSTA is described in the company details as a Registered Social Enterprise.

## How to leave review comments

Use the single running feedback thread:

https://github.com/antlerboy/PSTA/issues/2

You only need a GitHub account to comment there. For each observation, say which page or heading it relates to and what you want changed. Rough notes are fine. This thread is deliberately the place for incomplete thoughts, missing material, visual problems, factual corrections, and ideas for later iterations.

There is also a small feedback control at the bottom-right of the homepage. `Alt+Shift+N` opens the same thread.

Do not use the news publishing form for rough feedback. That form creates public content.

## Partners

The current agreed structure is:

Formal partners:

- E3M
- Nesta
- The Social Innovation Partnership (TSIP)

Programme and delivery collaborators:

- RedQuadrant
- Basis

Informal partner relationships:

- LocalGov Digital
- Browne Jacobson

APACE and Fractal Consulting are not to appear as current partners. 'Alliance for Useful Evidence' is not to be used as the name for Nesta. The public page should use logos and distinguish these relationship types rather than presenting every historic relationship as equivalent.

If any of these statuses are wrong or have changed, add the correction to the feedback thread rather than directly editing the generated partners page.

## How the website is built

The site is static HTML published through GitHub Pages. The repository is `antlerboy/PSTA`.

The complete site is reconstructed by `.github/workflows/pages.yml`. The workflow:

1. reconstructs the full site from the checked-in site bundle;
2. applies explicit overrides and public-copy corrections;
3. builds the news section and RSS feed;
4. applies the final identity and partner pass;
5. runs automated checks for page count, required public wording, partner structure, retired partners, company details, and key programme information; and
6. publishes the tested `deploy/` folder to GitHub Pages.

A failed build does not replace the live site. This is useful for safety but can be confusing: if a change has been committed but the live site still looks old, first check whether the latest Pages build failed. The Actions page is:

https://github.com/antlerboy/PSTA/actions

The live site should therefore be treated as 'the last successful build', not automatically as 'the current contents of main'.

## Routine publishing: news and updates

For an approved news item, use the structured GitHub issue form rather than editing HTML:

https://github.com/antlerboy/PSTA/issues/new?template=publish-news.yml

The form asks for the public title, summary, full story, optional primary link, author, publication date, suggested social post, social channels, and whether it should enter the newsletter queue.

When a permitted editor submits the form, the automation creates the source news file, rebuilds the site, adds the public article, updates the news index and RSS feed, refreshes the social queue, refreshes the newsletter queue, and can pass the item to an external distribution service.

Use the publishing form only when the words are ready to go public. The running feedback thread is the place for ideas and drafts.

## Social media operation

The site creates a structured social queue at:

`editorial/social-queue.json`

The publishing form can mark an item for:

- RedQuadrant LinkedIn
- the PSTA LinkedIn
- Quadrant Resourcing LinkedIn
- Benjamin's LinkedIn
- Benjamin's X/Twitter
- other connected Buffer channels

The repository does not currently contain the credentials needed to post directly to those accounts. It is designed to pass a clean payload to a separate automation layer, which can then create Buffer drafts or queued posts.

The missing operational connection is the repository secret `NEWS_DISTRIBUTION_WEBHOOK_URL`. Once a Zapier, Make, n8n, Power Automate, or equivalent webhook has been set up and mapped to the appropriate Buffer profiles, adding that secret will connect the website publishing operation to the social distribution operation.

The default should be to create drafts or queued posts for review, not to spray unreviewed copy straight onto every channel.

Until the webhook is connected, website publication, RSS, the social queue, and the newsletter queue still work; social distribution is simply a manual step.

## Newsletter operation

Items selected for newsletters are added to:

`editorial/newsletter-queue.csv`

This contains the date, title, summary, public URL, author, and status. It is the holding queue for future PSTA newsletter material.

Our actual newsletter route is SurveyMonkey, so the next integration should be SurveyMonkey-specific rather than introducing another email platform. There are two sensible options: keep the CSV as the editorial queue and copy/import approved items into SurveyMonkey, or extend the same distribution webhook so it creates a SurveyMonkey draft or otherwise hands the approved item into the existing SurveyMonkey process. No automatic SurveyMonkey send has been enabled.

## RSS

Every published news item also enters the RSS feed:

https://antlerboy.github.io/PSTA/news/feed.xml

This gives us a simple machine-readable feed that can be reused by other sites, internal tools, syndication, or future automation without rebuilding the editorial process again.

## Access for you and Natasa

Anyone with a GitHub account can comment in the public feedback thread.

To use the automatic news publishing form or edit repository content, you need Write access. Benjamin can add you from:

https://github.com/antlerboy/PSTA/settings/access

The intended permissions are:

- Benjamin: Admin
- David: Write
- Natasa: Write, if she is going to edit or publish

Write access allows content editing, branches, pull requests, and approved news publication. It does not give account billing or unrelated-repository access.

## Safe way to make different kinds of changes

Use the following operating rule:

- rough observations, corrections, ideas, and design comments: issue #2;
- approved news and insight items: the 'Publish a PSTA news item' form;
- substantial page, navigation, programme, policy, structural, or design changes: branch and pull request, normally implemented from the feedback thread;
- account permissions, GitHub Pages settings, secrets, domain changes, and integration credentials: repository owner/admin.

This keeps review notes, public publishing, and technical changes separate.

## The National Commissioning Academy

The current page has been expanded using the current September 2026 marketing material. It should show the September 2026 to February 2027 cohort, the launch webinar, the first anchor day, the applied five-cycle design, 100-day plans, participant evidence, a £2,490 individual fee, group/host discounts, and David as the principal contact.

Please check all of these against what you are actually selling now. If any date or commercial term has changed, say so in issue #2 and we will make the public source canonical rather than allowing several different leaflets to drift apart.

## The Service Transformation Programme

The public page has been revised so the programme is consistently named 'the Service Transformation Programme' and uses the current PSTA contact route rather than an invented or internal one.

Please check the actual contact destination, current delivery arrangements, programme wording, and whether there are any new dates or calls to action that should replace the present generic contact link.

## The feedback and iteration loop

The intended operating cycle is deliberately simple.

You and other reviewers put observations into issue #2. Those comments accumulate rather than disappearing into email or Teams. A website iteration then works through the thread, changes the source/build rules, tests the whole site, deploys it, and records what has been picked up. The thread remains the audit trail and the place to start the next iteration.

For quick factual corrections it may make sense to implement immediately. For bigger design or structure changes, collect several related comments and change them together so the site does not thrash between versions.

## What the automated checks are for

The build contains tests because we have already seen apparently successful-looking changes fail to reach the live site, and older generated content can otherwise reappear.

The checks are meant to stop publication if, for example, the full site collapses to a tiny version, the required programme pages vanish, the key Academy price disappears, retired partners return, or the company footer loses required wording.

They are a guardrail, not a substitute for visual review. A page can pass a text test and still have a broken image, bad spacing, or poor public copy. That is why the feedback thread and human review remain part of the operating system.

## What still needs a decision or account-level set-up

At the time of writing, these are the remaining operational choices rather than website-copy work:

1. Give David Write access and, if wanted, Natasa Write access.
2. Connect the `NEWS_DISTRIBUTION_WEBHOOK_URL` to the chosen automation service and map the actual Buffer profiles.
3. Decide the desired Buffer policy: drafts by default, queued posts by default, or different rules for different accounts.
4. Connect or define the SurveyMonkey newsletter step. The website queue exists; automatic SurveyMonkey drafting/sending does not.
5. Decide when this GitHub Pages version is good enough to replace the existing public site.
6. At cut-over, decide the production domain and rewrite the current `/PSTA/` project-path links for a root custom domain.
7. Decide whether the old WordPress site becomes an archive, redirects into the new site, or is retired completely.

## What David should not need to do

You should not need to edit generated HTML, understand the compressed site bundle, run Python scripts, debug GitHub Actions, or manually assemble RSS. Those are implementation details.

Your routine jobs should be: review the public offer, flag corrections, publish approved news, choose where an item should be distributed, maintain programme facts, and help decide what should be promoted next.

If the operating system starts requiring you to understand the machinery underneath it, that is a design fault to fix rather than a new skill requirement for you.

## Useful links

Live test site: https://antlerboy.github.io/PSTA/

Running feedback: https://github.com/antlerboy/PSTA/issues/2

Publish approved news: https://github.com/antlerboy/PSTA/issues/new?template=publish-news.yml

Repository: https://github.com/antlerboy/PSTA

Actions and deployment status: https://github.com/antlerboy/PSTA/actions

Repository access: https://github.com/antlerboy/PSTA/settings/access

Detailed news operation: `docs/NEWS_AND_SOCIAL_PUBLISHING.md`

Detailed access operation: `docs/EDITING_AND_ACCESS.md`

News source format: `content/news/README.md`
