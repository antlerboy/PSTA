# Website review: 30 September 2026

Benjamin requested a full website update, including queued news.

## Publishing queue

- Issue #9: Mike Chitty's 'The Neighbourhood That Had No Plan'. Published as a short attributed reading note, explicitly identifying the source as a fictional story.
- Issue #10: Cormac Russell's 'Associations & Institutions'. Published as an attributed reading note linking to the original LinkedIn post.
- Issue #2, comment 5911978309: the LGIU's 'Rewiring the state: unlocking local government's role'. Published as a report note, distinguishing policy proposals from implemented changes.
- Replaced the three homepage selections with these items. Earlier news remains in the news index and RSS.

## Whole-site review

- Reconciled the open feedback threads and issue #5 against the generated site. The November-May cohort, Great Portland Street address, compact footer, partner logos and statuses, Terry Rich, the 24-module curriculum, tool access wording, community placement, and ten-step spelling are retained.
- Corrected the remaining 1,500 graduate figure on About to the approved 2,500 Academy and programme figure.
- Replaced surviving migration commentary on Insights with useful links for readers.
- Replaced speculative partnership-development copy on the Basis profile with its existing accredited programme routes; removed a redundant text logo fallback.
- Clarified the community enquiry, consolidated duplicate Academy team invitations, and corrected punctuation in public copy.
- Updated the Academy announcement and newsletter queue at source to November 2026-May 2027. Retained the existing URL for incoming links. Induction is 10 November; other dates still require David's confirmation.
- Updated the privacy description to reflect the deployed visit counter. Its script sends the page path, omits credentials and query strings, and respects Do Not Track. The notice no longer claims that a visit collects no information.

## Distribution boundary

The three additions are website-only, with empty channels and newsletter set to no. The corrected Academy announcement retains its existing editorial queue selection and sets `distribute: no`, which the webhook now honours. This update does not request social posts or newsletter sends.

## Verification

- Complete production assembly and structural audit passed: 92 HTML files, 58 indexable pages, all internal links and referenced local assets valid.
- All three articles appear in the homepage selection, news index, RSS, and sitemap.
- Desktop news-card layout and a 390-pixel mobile article were inspected; mobile navigation expands correctly.
- Twenty public non-social destinations were checked: nineteen returned HTTP 200; Basis returned HTTP 403 to the automated client. The existing Basis URL is retained.
- A mocked webhook check confirmed that no news change in this release initiates distribution.
- The running feedback issues remain open for future observations. Issues #9 and #10 should be closed only after live publication is verified.
