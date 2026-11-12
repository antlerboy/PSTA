# Commissioning Compass and practice resources

The PSTA website provides the March 2026 Commissioning Compass assessment, the sixteen-question smartCompass reflection, and the June 2026 v2 beta matrix. Each edition identifies its source and version. Source questions, factors, score bands, and the original AI prompt retain their wording.

The workspaces support separate perspectives, evidence, actions, review dates, optional device saving, editable JSON, Word notes, and formatted print/PDF. Device saving is local to the browser; there is no live co-editing or automatic merging of separate records. The beta does not submit answers to the PSTA or an AI service. Input pages do not load analytics or third-party scripts.

The beta working paper has a reading edition at `/tools/compass-v2-beta/source/`, with section navigation, linked references, a desktop matrix, and per-lens layouts for mobile and print. `scripts/compass_paper.py` checks the complete rendered source text against the retained original, allowing whitespace changes only. The original text file remains available unchanged.

Word notes are genuine DOCX packages containing the current responses, evidence, actions, review drafts, and dated snapshots. Ordinary notes no longer download as Markdown; the separate smartCompass AI reflection file still does. Print reports use semantic headings and escaped text. Report-only print rules are scoped so that ordinary paper and landing pages remain printable. Existing record versions and local-storage keys are retained. Unsaved changes prompt before navigation, and a change from another tab stops automatic saving to avoid overwriting that tab's record. Editable imports allow records up to 20 MiB; adding a snapshot cannot silently exceed that reopening limit.

The public smartCompass reflection download begins with a chat task and includes the published June 2025 descriptions of the eight Compass aspects, with source hashes and public links, followed by one selected perspective’s current answers and evidence. It excludes other perspectives, actions, and review history. The user checks the file, then uploads it or pastes its text into an authorised AI service. The historical automation prompt is a separate reference, not part of the primary file. The website does not generate AI analysis, connect an email account, or send email.

The learning guide covers 49 topics. It includes the original course teaching, both worked tables, all 17 original images, nine Word worksheets, three PDFs, and a blank copy of the 2023 Excel workbook. Contact details and introductory guidance use current public routes. The approach chapters also include the full June 2023 pre-reading. Definitions include accessible text from the June 2025 teaching template. Source dates, references, and acknowledgements are retained. The 2017 asset-based commissioning article retains its original publication date and text.

The PSTA offers one-off case clinics or a short series on request, with a concrete 90-minute agenda. The request captures the case, team, preferred format, dates, and requirements. Scope, facilitator, dates, format, and fee are agreed before booking. A host guide, participant brief, and case record are also available. Enquiry preparation opens a draft in the visitor’s email app and never sends it automatically.

RedQuadrant owns the shared Leading Transformation record. The PSTA publishes a checked copy, with modules, fees, support, and accreditation drawn from it. The build checks the curriculum against the shared record.

Run `npm run test:compass`, `npm run check:programme`, and `npm run build` for source, record, programme, and site checks. The browser checks cover saving, record portability, reviews, downloads, privacy on input pages, and mobile layout.
