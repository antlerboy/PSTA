# Compass and practice resources

The self-hosted editions are built from `content/compass/` and share the browser application in `assets/compass/`. The release pass is `scripts/apply_useful_practice.py`. The website is static: no visitor answers are submitted to a server by these workspaces.

## Source editions

| Edition | Preserved content | Scope |
| --- | --- | --- |
| Original Commissioning Compass, 24 March 2026 sheets | Eight aspects, 79 assessment questions, 89 factors, initial and final question scores /100, initial and revised aspect scores, four original score bands | Transcribed from the unfilled master. Factor choices are limited to three constraints and three enablers per aspect and perspective. Factors have no numerical scores in this edition. |
| smartCompass local reflection edition | Two context prompts and sixteen reflective questions, in published Forms order | Contact fields are omitted. The existing AI email service remains separate. |
| Compass v2.0 beta, 13 June 2026 | Eight lenses and the forty original matrix prompts | No numerical grade is calculated. |
| SCOA archive source | Undated predecessor sheet: eight aspects, 71 questions, and 88 factors | Kept under `content/compass/archive/` and as preserved source text. It is excluded from the active workspaces and public chooser until compared with an authorised current export. No later score-band labels or three-factor limit are added. |

`content/compass/sources/` holds the source text and sanitised question definitions. Each tool record contains the SHA-256 of the source used. The earlier generic scoring transcription is retained as an archive source; the March 2026 unfilled master is authoritative for the original workspace. Completed participant files, private correspondence, account configuration, and credentials are excluded.

The workspaces preserve different perspectives and evidence rather than averaging scores. The four review questions are from the v2.0 beta and are labelled as additions when used with earlier editions. A review keeps an independent snapshot of current answers and decisions. A later edit does not change that snapshot.

## Visitor records

Saving is opt-in. `Save on this device` writes the record into browser storage for that edition and then keeps it updated. `Remove device copy` removes that storage item. JSON downloads can be reopened in the same edition; a record for another edition is rejected. Readable notes include current answers, decisions, review drafts, and review snapshots. Print uses the complete record rather than only the open accordion.

Workspace and enquiry pages omit the page-visit counter and third-party scripts. They do not put answers into URLs. Enquiry preparation opens a draft in the visitor's email app only when they choose it; it never sends a message automatically. A downloaded file remains under the visitor's control.

## AI handoff

Only the `Draft prompt v3BT` section was recovered from the PSTA's existing smartCompass instructions summary. Its wording is preserved, with a final newline normalised. It contains historical public links, output requirements, prototype language, and public team contacts. The summary document, private source URL, run outputs, credentials, and operational identifiers are not published.

The local handoff downloads the original prompt and the current record. It does not call an AI service or claim that the existing email automation has been migrated. The operator should check placeholders, the intended recipient, and the material before using an authorised AI account. The original Forms email service remains an explicit separate option.

The complete Teachable teaching chapters, videos, cases, approaches, and downloads still require an authorised course export and inventory comparison. The self-hosted scoring sheets and recovered documents must not be described as a complete course migration. The live Power Automate configuration and credentials have not been recovered or moved.

The live public course catalogue was checked on 5 November 2026. It lists ten sections and 49 lessons, all marked non-preview. The catalogue-only inventory is in `content/compass/archive/teachable-course-inventory-2026-11-05.json`. None of those lesson bodies has been exported and checked against the website. The remaining course archive comprises seven introduction lessons; eight sections each containing a definition, cases/equality/equity considerations, key questions, factors, and an approach lesson; and two resources/acknowledgement lessons. Although assessment questions and factors were recovered separately, this does not establish that their course lesson bodies and attachments have been archived.

The eight approach lessons are Place-based wellbeing; Leadership of place for whole system change; Unlocking potential; Citizen-centred commissioning; Values-based/disruptive commissioning; Strategic procurement of services against needs; Contestability and Market management; and Delivery model design. Counts and filenames of embedded videos or attached downloads cannot be determined from the catalogue alone.

## Programme facts

RedQuadrant owns the shared Leading Transformation record at `https://redquadrant.com/records/leading-transformation.json`. The PSTA keeps a checked copy in `content/programmes/leading-transformation.json`, publishes that copy under `/records/`, and labels its version on the programme page. The build fails if its modules differ from `content/curriculum-2026.json`. The programme fee, support, accreditation, and enquiry block is rendered from the record, rather than maintaining a separate copy of those facts.

Run `python scripts/check_programme_record.py --upstream <URL-or-file>` to compare with the owning record before refreshing the checked copy. Review programme-specific fees and support as well as the module list.

## Community resources

The host guide, case-holder brief, and evidence-conscious case record are in `assets/practice/`. They provide a proposed three-month operating design rather than an event timetable. Dates, convenor, participants, access needs, and any fee must be agreed for an actual group. No participant or outcome is invented, and nothing is published automatically from a clinic.

## Build and checks

- `python scripts/build_site.py` reconstructs and audits the complete site using the pass order in the release workflow. It replaces only this repository's `deploy/` directory.
- `node --test scripts/test_compass.cjs` checks preserved source hashes, original question wording, edition distinctions, numerical ranges, review snapshots, and record import/export.
- `node scripts/test_compass_browser.cjs` checks the rendered application. It requires Playwright; `PLAYWRIGHT_MODULE` can point to an installed module, and `BROWSER_EXECUTABLE` can select an installed Chromium browser. Screenshots and test downloads go beside the checkout in `psta-qa/`.
- The browser checks cover local saving/removal, zero and finalised scores, factor limits, multiple perspectives, review drafts, immutable review snapshots, JSON round trips, wrong-edition rejection, the source-exact AI handoff, print, mobile width, local enquiry preparation, and third-party-request absence on input pages.

## Reading material recovered on 6 November 2026

The reading pages reproduce teaching text for 38 of the original course's 49 catalogue topics: six introductory topics, plus definitions, question sets, factor sets, and approaches for all eight aspects. They use selected text from the June 2025 teaching template. The eight approach pages also include the full June 2023 adult social care pre-reading, including its examples and references. Each page identifies its source date. The March 2026 assessment remains a separate edition.

The reading extracts retain source wording and hyperlinks. The complete source deck is not published: internal template instructions, speaker notes, contact details, blank slides, and draft appendices are excluded. One inspected diagram is retained with its original visible credit. Approved extracts and the diagram have recorded hashes checked by `scripts/test_compass_reading.cjs`.

No Teachable lesson body has yet been compared in full. Eleven catalogue lessons lack an equivalent local source chapter: the developing-tool introduction, eight case-study/equality lessons, and two final resource lessons. The earlier examples in the approach pre-reading do not establish the contents of the later case-study/equality lessons. The course's media/download counts are still unknown. The sources/status page states this and retains the original course links. There are no empty lesson pages.

The shared programme record also now matches the canonical record's organisation naming. Its modules, fees, and programme facts are unchanged.

The original smartCompass form is retained as a separate route. Its present processing and email delivery have not been verified; the landing page states this. The local workspace only prepares the original prompt and answers for an authorised AI account.

One internal reference in the 2023 pre-reading led to a missing 2017 article. Its 15 published paragraphs were recovered from the February 2026 WordPress content archive and restored at the original path, with the original date stated. No draft post, unrelated export content, comments, or private metadata is published.
