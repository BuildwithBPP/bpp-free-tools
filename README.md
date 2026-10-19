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

Served via GitHub Pages. Source of truth for content edits lives in the BPP workspace (`1. Internal Operations/2. Marketing & Sales/Free Resources/`); copy changed files here and push to deploy.

**This repo is public. Nothing internal goes in here, ever.**
