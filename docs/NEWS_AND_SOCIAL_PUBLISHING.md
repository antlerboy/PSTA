# Publishing PSTA news, social posts, and newsletter items

The repository now has one low-friction route for approved news. It is designed so David does not need to edit HTML, run a site generator, or understand Git.

## Publish one item

1. Open the repository's **Issues** tab.
2. Select **New issue**.
3. Choose **Publish a PSTA news item**.
4. Add the public headline, short summary, full story, publication date, and optional link.
5. Tick the social channels and choose whether the item belongs in the newsletter queue.
6. Submit the issue.

The automation checks that the submitter has write access to the repository. It then:

- creates a dated Markdown source file in `content/news/`;
- rebuilds the website;
- publishes an individual news page;
- updates the news index and RSS feed;
- adds the item to `editorial/social-queue.json`;
- adds it to `editorial/newsletter-queue.csv` when requested;
- sends the structured item to the optional distribution webhook; and
- comments on the issue with the public URL before closing it.

Rough ideas and feedback should still go into the single running website feedback issue. The publishing form is for copy that is ready to go public.

## Buffer and the social channels

The repository produces editorial queues. A queue entry is a request for distribution, not evidence that a social post has been created. The build regenerates these files and sets their status to `queued`; it does not know Buffer's delivery state.

### Cloud polling through the connected Buffer account

The existing daily Buffer management task can read the repository through the GitHub connector and create posts through the authenticated Buffer connector. This route does not require an open browser, the user's computer, a new API key, or a separate paid automation service.

Read `editorial/social-queue.json` from `antlerboy/PSTA` on `main`. The GitHub `fetch_file` operation returns the JSON in `structuredContent.content`. The file is also available at:

`https://github.com/antlerboy/PSTA/blob/main/editorial/social-queue.json`

Each item has `date`, `title`, `url`, `post`, `channels`, `source`, and `status`. For example, the published Glasgow item uses:

```json
{
  "date": "2026-10-12",
  "title": "Understanding family poverty in Glasgow: beyond the numbers",
  "url": "https://www.publicservicetransformation.org/news/understanding-family-poverty-glasgow/",
  "post": "Glasgow’s seventh annual family-poverty report does more than count hardship. It combines open data, lived experience, and service expertise to show how poverty moves through family life—and to help councils and partners decide what to do.",
  "channels": ["The PSTA LinkedIn", "RedQuadrant LinkedIn", "Quadrant Resourcing LinkedIn"],
  "source": "content/news/2026-10-12-understanding-family-poverty-glasgow.md",
  "status": "queued"
}
```

The consumer must:

1. Read the source file as well as the queue entry. Honour `draft: true`, `distribute: no`, empty channel selections, and expired event dates. An item on the public website or RSS feed is not automatically a request to distribute it.
2. Resolve each selected channel label against the connected organisation's channel list. Do not silently send a brand item to a personal account or an unselected brand.
3. Check the durable distribution ledger and Buffer drafts, approvals, scheduled posts, errors, and sent posts before creating anything. Include posts imported from the native network. Compare the canonical source URL and channel ID, and check titles, text, and primary links: an older share may contain a shortened link or an earlier URL.
4. Use the canonical source URL plus Buffer channel ID as the stable delivery key. Record the source revision, created post ID, actual returned status, queue time, and any publication URL in the external ledger. Do not edit the generated queue's `status` as the only delivery record; the next build will overwrite it.
5. For approved, current brand content, add a post to an existing queue slot. Stage a draft where the copy, timing, or approval is unresolved. Do not publish immediately or backfill the historical queue as one batch. If a create call returns an uncertain result, reconcile the channel before retrying.
6. Record source coverage and any skipped or failed items. Browser-only comment work must not prevent the API-based queue work from completing.

The latest successful task run and its returned Buffer post IDs establish whether this route is operating. A green website build or webhook workflow alone does not.

### Optional push webhook

The webhook is an alternative trigger for a receiving service such as Zapier, Make, n8n, Power Automate, or an internal endpoint. It is not required by the cloud polling route. The receiving automation should:

1. receive the `psta_news_published` payload;
2. loop through `items`;
3. read `social_post`, `website_url`, and `channels`;
4. map the selected channel names to the relevant Buffer profiles;
5. create queued or draft Buffer posts rather than publishing immediately, unless the team deliberately chooses otherwise; and
6. optionally notify David that the social drafts are ready.

Once the receiving webhook exists, add its URL as the repository Actions secret:

`NEWS_DISTRIBUTION_WEBHOOK_URL`

The secret is added at:

`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Without this secret, website publishing still works. The optional webhook step reports `skipped_no_webhook`, adds a visible Actions warning and summary, and makes no external delivery. The queues remain available for cloud polling or manual editorial use. A webhook HTTP success confirms receipt by that endpoint; the receiver must still record the actual Buffer post IDs and statuses. If both routes are used, they must share the same delivery ledger to avoid duplicates.

## Newsletter workflow

Each published item marked for the newsletter is added to:

`editorial/newsletter-queue.csv`

That queue contains the publication date, title, summary, public URL, author, target newsletter audience(s), and status. A newsletter editor can import or copy these rows into the existing email platform. The same webhook payload includes a `newsletter` flag, so the automation can also create a draft campaign item in Mailchimp, Brevo, MailerLite, or another connected service.

The recommended control is to create drafts, not to send newsletters automatically. Website publication and outbound email are different acts with different risks.

## Direct editing

People comfortable with Markdown may add a file directly to `content/news/`. Use the format documented in `content/news/README.md`. A push to `main` rebuilds the site and triggers the distribution workflow.

## Public routes

- News index: `https://www.publicservicetransformation.org/news/`
- RSS feed: `https://www.publicservicetransformation.org/news/feed.xml`
- Social queue: `editorial/social-queue.json`
- Newsletter queue: `editorial/newsletter-queue.csv`

## Newsletter routing

A news item marked `newsletter: yes` is queued for both the PSTA and RedQuadrant newsletters by default. Add `newsletter_targets` in front matter if an item should go to only one audience. Keep these as editorial queues: do not auto-send a newsletter from a website update.
