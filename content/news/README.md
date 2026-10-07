# News source files

Each published news item is a Markdown file with a short front-matter block:

```text
---
title: "Public headline"
date: 2026-09-01
summary: "One or two public-facing sentences."
author: "The PSTA"
social: "Suggested social copy."
channels: "RedQuadrant LinkedIn, The PSTA LinkedIn"
newsletter: yes
newsletter_targets: "PSTA, RedQuadrant"
draft: false
---

Full story in Markdown.
```

For a website correction that must not trigger the outbound distribution webhook,
set `distribute: no`. This leaves the item published and preserves its existing
social/newsletter queue selection. New website-only items should use empty
`channels` and `newsletter: no`.

The easier route is the repository's ‘Publish a PSTA news item’ issue form. Opening a completed form creates this file automatically, rebuilds the website and RSS feed, adds the item to the social and newsletter queues, and sends it to the optional distribution webhook.

`newsletter_targets` is optional. If `newsletter: yes` is set without it, the item is queued for both the PSTA and RedQuadrant newsletters.
