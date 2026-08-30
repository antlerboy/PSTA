# Public Service Transformation Academy website

The complete static website for the Public Service Transformation Academy, published through GitHub Pages.

- Live site: https://antlerboy.github.io/PSTA/
- Running website feedback: https://github.com/antlerboy/PSTA/issues/2
- News index: https://antlerboy.github.io/PSTA/news/
- RSS feed: https://antlerboy.github.io/PSTA/news/feed.xml
- Deployment workflow: `.github/workflows/pages.yml`

## Editing routes

Use the single running feedback issue for rough observations and changes for a later iteration.

Use the **Publish a PSTA news item** issue form for approved news. A permitted submission creates the website item, updates RSS, refreshes the social and newsletter queues, and invokes the optional Buffer/newsletter webhook.

Detailed instructions:

- `docs/EDITING_AND_ACCESS.md`
- `docs/NEWS_AND_SOCIAL_PUBLISHING.md`
- `content/news/README.md`

## Latest news and social media

The home-page `Latest news and social media` panel is editorial rather than simply chronological. Keep exactly three strong current items in `content/latest.json`, drawing from PSTA news, PSTA social media, current programmes, and genuinely useful PSTA tools or resources. Prefer relevance to live PSTA work over raw recency, and replace items when they stop being timely.

## Build structure

The Pages workflow reconstructs the complete multi-page site from `site-full-text/`, applies files in `overrides/`, runs the public-copy and partner audit, builds news, adds the curated latest panel and Easter eggs, checks the result, and publishes the `deploy/` directory.

The build enforces the public naming rules, the corrected partner structure, the official logo, the footer company details, and a minimum complete-site page count. A failure blocks publication rather than silently reverting to a mini site.

Internal links currently use the GitHub project path `/PSTA/`. Rebuild or replace that prefix before moving the same files to a root custom domain.
