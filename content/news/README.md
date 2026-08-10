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
draft: false
---

Full story in Markdown.
```

The easier route is the repository's ‘Publish a PSTA news item’ issue form. Opening a completed form creates this file automatically, rebuilds the website and RSS feed, adds the item to the social and newsletter queues, and sends it to the optional distribution webhook.
