# BPP Free Tools

Public free tools and downloadable resources from [Business Plans Plus](https://www.buildwithbpp.com).

| Path | What it is |
|---|---|
| `/scorecard` | Owner-Dependency Scorecard — 10-question interactive quiz |
| `/calculator` | Cost-of-Owner-Dependence Calculator |
| `/foundation-score` | Foundation Readiness Score — 10-question quiz for new businesses |
| `/ai-readiness` | AI Employee Readiness Assessment — which AI assistant to hire first |
| `/system-finder` | Business System Finder — 7-question qualifier |
| `/guides` | Run-Without-You Guide gate — name + email, then the PDF (general or commercial cleaning) |
| `/downloads/` | Free guides and templates (PDF/DOCX) |

## Capture + delivery

Every tool POSTs to one shared HubSpot form, "Lead magnet - all tools" (portal `242172275`, v3 Forms API), from its `CONFIG` block. Each submission sets `lm_magnet` (the slug, same as the Webflow waitlist Product field), `lm_magnet_name`, and `lm_result_summary` (a plain-text copy of the result). A HubSpot workflow enrolls the contact in a one-email sequence that sends that summary. The HubSpot v3 API returns 200 even when it drops a field that isn't on the form, so after any change, submit a test and check every property on the contact record.

## Partner ref links (`?ref=`)

Any tool URL can carry `?ref=<code>`, for example `/scorecard/?ref=smith-cpa`. A code is lowercase letters, digits and hyphens, 40 characters max; anything else is ignored. The code is kept for the browser session, so it follows the visitor from tool to tool, and every HubSpot submission adds it as one extra field, `lm_ref`. Nothing else in the payload changes, and with no code the payload is exactly what it was before. The page shows "Shared by <name>" only for codes listed in `assets/partners.js`; add the partner there before handing out their link.

**Before this ships:** a `lm_ref` contact property (single-line text) must exist in HubSpot and be added to the "Lead magnet - all tools" form. Until then HubSpot drops the code without an error (see above), so partner attribution is lost. After adding it, send one test with `?ref=` and check `lm_ref` on the contact record.

Served via GitHub Pages. Source of truth for content edits lives in the BPP workspace (`1. Internal Operations/2. Marketing & Sales/Free Resources/`); copy changed files here and push to deploy.

**This repo is public. Nothing internal goes in here, ever.**
