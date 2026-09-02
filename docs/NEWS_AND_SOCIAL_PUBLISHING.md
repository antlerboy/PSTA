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

GitHub cannot publish directly to every social account without account credentials and platform permissions. The repository therefore sends one clean JSON payload to an automation service, which can then route the item into Buffer.

Use Zapier, Make, n8n, Power Automate, or a small internal webhook. The receiving automation should:

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

Without this secret, website publishing still works. The social and newsletter queues remain available in the repository for manual use.

## Newsletter workflow

Each published item marked for the newsletter is added to:

`editorial/newsletter-queue.csv`

That queue contains the publication date, title, summary, public URL, author, and status. A newsletter editor can import or copy these rows into the existing email platform. The same webhook payload includes a `newsletter` flag, so the automation can also create a draft campaign item in Mailchimp, Brevo, MailerLite, or another connected service.

The recommended control is to create drafts, not to send newsletters automatically. Website publication and outbound email are different acts with different risks.

## Direct editing

People comfortable with Markdown may add a file directly to `content/news/`. Use the format documented in `content/news/README.md`. A push to `main` rebuilds the site and triggers the distribution workflow.

## Public routes

- News index: `https://www.publicservicetransformation.org/news/`
- RSS feed: `https://www.publicservicetransformation.org/news/feed.xml`
- Social queue: `editorial/social-queue.json`
- Newsletter queue: `editorial/newsletter-queue.csv`
