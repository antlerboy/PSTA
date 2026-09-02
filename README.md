# Public Service Transformation Academy website

The complete static website for the Public Service Transformation Academy, published through GitHub Pages.

- Live site: https://www.publicservicetransformation.org/
- Running website feedback: https://github.com/antlerboy/PSTA/issues/2
- News index: https://www.publicservicetransformation.org/news/
- RSS feed: https://www.publicservicetransformation.org/news/feed.xml
- Deployment workflow: `.github/workflows/pages.yml`

## Editing routes

Use the single running feedback issue for rough observations and changes for a later iteration.

Use the **Publish a PSTA news item** issue form for approved news. A permitted submission creates the website item, updates RSS, refreshes the social and newsletter queues, and invokes the optional Buffer/newsletter webhook.

Detailed instructions:

- `docs/EDITING_AND_ACCESS.md`
- `docs/NEWS_AND_SOCIAL_PUBLISHING.md`
- `content/news/README.md`

## Latest news and social media

The home-page `Latest from the PSTA` panel is editorial rather than simply chronological. Keep exactly three strong current items in `content/latest.json`, drawing from the PSTA's news and social media, current programmes, and genuinely useful tools or resources. Give every item a distinct `topic`; the build rejects repeated topics and repeated links. Prefer relevance to live PSTA work over raw recency, and replace items when they stop being timely.

## Build structure

The Pages workflow reconstructs the complete multi-page site from `site-full-text/`, applies files in `overrides/`, runs the public-copy and partner pass, builds news, adds the curated latest panel and Easter eggs, applies the production-domain launch pass, audits the result, and publishes the `deploy/` directory.

The build enforces the public naming rules, partner structure, official logo, footer company details, production paths, search indexing, metadata, accessibility structure, legacy redirects, and internal-link integrity. A failure blocks publication rather than silently reverting to an incomplete or broken site.

Source material can retain the historical GitHub project prefix. The final launch pass converts it to root-domain paths and writes the production `CNAME`, `robots.txt`, and sitemap.
