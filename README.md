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
- `docs/COMPASS_AND_PRACTICE.md`

## Latest news and social media

The home-page `Latest from the PSTA` panel is editorial rather than simply chronological. Keep exactly three strong current items in `content/latest.json`, drawing from the PSTA's news and social media, current programmes, and genuinely useful tools or resources. Give every item a distinct `topic`; the build rejects repeated topics and repeated links. Prefer relevance to live PSTA work over raw recency, and replace items when they stop being timely.

## Build structure

The Pages workflow reconstructs the complete multi-page site from `site-full-text/`, applies files in `overrides/`, runs the public-copy and partner pass, builds news, adds the curated latest panel and Easter eggs, applies the production-domain launch pass, audits the result, and publishes the `deploy/` directory.

The build enforces the public naming rules, partner structure, official logo, footer company details, production paths, search indexing, metadata, accessibility structure, legacy redirects, and internal-link integrity. A failure blocks publication rather than silently reverting to an incomplete or broken site.

Source material can retain the historical GitHub project prefix. The final launch pass converts it to root-domain paths and writes the production `CNAME`, `robots.txt`, and sitemap.


## Keeping the three editorial selections current

`content/latest.json` contains exactly three primary selections, in editorial order. Choose current, distinct topics for relevance; do not automatically take the three newest feed entries. `content/latest-fallbacks.json` holds at least three approved evergreen alternatives. The build rejects repeated topics or links within either list, unsafe URLs, incomplete items, and missing expiry decisions.

Each item has `topic`, `source`, `title`, `summary`, `href`, `link_label`, and `reviewed_on` (`YYYY-MM-DD`). A dated promotion must have an exclusive `expires_at` timestamp with an explicit timezone, for example `2026-11-09T15:00:00+00:00`. Use the event end or the point at which the promotional wording ceases to be valid. A resource that remains useful after a particular date instead has `evergreen: true`. An optional `valid_from` timestamp prevents a primary item appearing early. Fall-back items must be evergreen and immediately available.

Both the build and the browser select three valid items, using primary order first and then approved alternatives while excluding duplicate topics and links. The browser rechecks on loading, returning to the tab, and the next expiry boundary, so a dated promotion rolls off without waiting for another commit or deployment. Static HTML also contains three selections made at build time.

The public `/assets/data/latest.json` manifest records `selection_as_of`, `source_commit`, `selected`, `candidates`, `expired_topics`, `fallback_topics`, `review_due_topics`, and `next_transition_at`. `review_needed` becomes true when the build uses a replacement, an item has expired, or the primary selection has gone fourteen days without editorial review. A successful rebuild is not evidence of a new editorial review: only update `reviewed_on` when checking the actual content and links.

The existing 06:00 UK editorial automation should inspect the manifest and source files, check approved news, events, resources, and social material, and update the primary choices when warranted. It must compare expiry timestamps with the current time even if an old manifest says `review_needed: false`, because the public manifest records build-time state. Keep one panel of three distinct topics. Preserve useful evergreen items when they remain the better choice. The existing Friday check covers stale dates, promotions, and broken links; no second publishing schedule is needed.

Run `python3 -m unittest discover -s tests -p test_curated_latest.py` before publishing. The tests cover date boundaries, explicit timezones, future items, duplicate topics and links, missing expiry decisions, evergreen replacement capacity, escaped markup, and matching browser/build selections.
