# BPP Free Tools

Public free tools and downloadable resources from [Business Plans Plus](https://www.buildwithbpp.com).

| Path | What it is |
|---|---|
| `/scorecard` | Owner-Dependency Scorecard — 10-question interactive quiz. Score and band show with no form; the pillar breakdown and fix-first plan sit behind the email form |
| `/calculator` | Cost-of-Owner-Dependence Calculator |
| `/foundation-score` | Foundation Readiness Score — 10-question quiz for new businesses |
| `/ai-readiness` | AI Employee Readiness Assessment — which AI assistant to hire first |
| `/system-finder` | Business System Finder — 7-question qualifier |
| `/guides` | Run-Without-You Guide gate — name + email, then the PDF (general or commercial cleaning) |
| `/downloads/` | Free guides and templates (PDF/DOCX) |

## Capture + delivery

Every tool POSTs to one shared HubSpot form, "Lead magnet - all tools" (portal `242172275`, v3 Forms API), from its `CONFIG` block. Each submission sets `lm_magnet` (the slug, same as the Webflow waitlist Product field), `lm_magnet_name`, and `lm_result_summary` (a plain-text copy of the result). A HubSpot workflow enrolls the contact in a one-email sequence that sends that summary. The HubSpot v3 API returns 200 even when it drops a field that isn't on the form, so after any change, submit a test and check every property on the contact record.

## Crawl and share tags

Each tool page carries a static "How it works" section under the tool (questions, math, how to read the result, FAQ), so crawlers and AI tools that skip JavaScript can read it. Keep it in step with the JS: if a question, weight or band changes, change the explainer too.

The canonical link, og:url, og:image, twitter:card and JSON-LD live between `<!-- seo:begin -->` and `<!-- seo:end -->` in each page and are written by `scripts/build-seo.py`, which also writes `sitemap.xml` and `robots.txt`. The public host is one constant, `BASE_URL`, at the top of that script. To move hosts (for example to `https://tools.buildwithbpp.com/`), change that line and run `python3 scripts/build-seo.py`; `--check` exits 1 if anything is stale. The pages' own title, description and og:title/og:description stay hand-written in the HTML. Two links still name the github.io host in page JS (the Foundation Score's `SCORECARD_URL` and the System Finder's cross-tool links); GitHub's redirect covers them after a move, but update them then.

`robots.txt` and `sitemap.xml` sit at the repo root. They do nothing on `buildwithbpp.github.io/bpp-free-tools/`, because crawlers only read robots.txt at a host root and this repo is a project site under that host. They take effect once the tools move to their own subdomain.

Share images (1200x627, LinkedIn's size) are in `assets/og/`, one per tool, rendered by `scripts/make-og-images.py --fonts <folder>` from the brand palette. The fonts (Montserrat, Poppins; Google Fonts, OFL) are not kept in the repo.

## Partner ref links (`?ref=`)

Any tool URL can carry `?ref=<code>`, for example `/scorecard/?ref=smith-cpa`. A code is lowercase letters, digits and hyphens, 40 characters max; anything else is ignored. The code is kept for the browser session, so it follows the visitor from tool to tool, and every HubSpot submission adds it as one extra field, `lm_ref`. Nothing else in the payload changes, and with no code the payload is exactly what it was before. The page shows "Shared by <name>" only for codes listed in `assets/partners.js`; add the partner there before handing out their link.

**Before this ships:** a `lm_ref` contact property (single-line text) must exist in HubSpot and be added to the "Lead magnet - all tools" form. Until then HubSpot drops the code without an error (see above), so partner attribution is lost. After adding it, send one test with `?ref=` and check `lm_ref` on the contact record.

## Results index (scaffold)

`scripts/index-aggregate.py` reads a HubSpot contacts CSV export and prints counts, medians and band splits per tool, for a future quarterly owner-dependence index. Export `createdate`, `email`, `lm_ref` and the result fields each tool sends: `owner_dependency_score`, `weakest_pillar_1` (Scorecard); `calc_annual_cost` (Calculator); `foundation_readiness_score`, `weakest_foundation_1` (Foundation Score); `ai_first_hire`, `ai_readiness_level` (AI Readiness); `recommended_system`, `business_stage` (System Finder); `lm_guide_requested` (Guide). `--publish` prints only tools with 50 or more completions and exits 2 if none qualify; the floor can be raised, never lowered. Contacts at buildwithbpp.com are dropped as tests. HubSpot keeps only each contact's latest value, and `createdate` is when the contact was created, so treat date windows as a proxy. `python3 scripts/index-aggregate.py --self-test` runs it on `scripts/fixtures/synthetic-hubspot-contacts.csv`, which is made-up data.

Served via GitHub Pages. Source of truth for content edits lives in the BPP workspace (`1. Internal Operations/2. Marketing & Sales/Free Resources/`); copy changed files here and push to deploy.

**This repo is public. Nothing internal goes in here, ever.**
