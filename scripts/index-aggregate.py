#!/usr/bin/env python3
"""Aggregates free-tool results from a HubSpot contacts CSV export (scaffold for a
quarterly owner-dependence index).

    python3 scripts/index-aggregate.py contacts.csv                  # internal stats, every tool
    python3 scripts/index-aggregate.py contacts.csv --since 2026-10-01 --until 2026-12-31
    python3 scripts/index-aggregate.py contacts.csv --publish        # only tools with 50+ completions
    python3 scripts/index-aggregate.py --self-test                   # runs on the synthetic fixture

Export these contact properties (columns may use the internal names below or HubSpot's
labels, e.g. "Owner Dependency Score"; matching ignores case, spaces and underscores):
createdate, email, lm_ref, plus each tool's fields in TOOLS.

How to read it:
- A contact counts as a completion for a tool when that tool's key field is filled.
  HubSpot keeps only the latest value, so a retake replaces the earlier result and a
  contact counts once per tool. lm_magnet and lm_fit only show the most recent tool,
  so they are not used for counting.
- createdate is when the contact was created, not when the tool was taken. Date
  filters are a proxy for "completed in this period".
- Internal test contacts (email at buildwithbpp.com by default) are dropped.
Only aggregates are printed; no names or emails.
"""
import argparse
import csv
import pathlib
import re
import statistics
import sys

MIN_PUBLISH = 50  # hard floor: no tool's numbers are publishable under 50 completions

# Bands mirror the thresholds in each tool's page JS.
def scorecard_band(v):
    return "Highly Owner-Dependent (60%+)" if v >= 60 else "Partially Owner-Dependent (35-59%)" if v >= 35 else "Running on Systems (under 35%)"

def foundation_band(v):
    return "Ready to Build (70%+)" if v >= 70 else "Almost Ready (40-69%)" if v >= 40 else "Foundation First (under 40%)"

def cost_band(v):
    return "$100K+ a year" if v >= 100000 else "$30K to $99.9K a year" if v >= 30000 else "Under $30K a year"

TOOLS = [
    {"slug": "owner-dependency-scorecard", "name": "Owner-Dependency Scorecard", "key": "owner_dependency_score",
     "numeric": True, "unit": "%", "band": scorecard_band, "lower_is_better": True,
     "dists": ["weakest_pillar_1"]},
    {"slug": "cost-of-owner-dependence-calculator", "name": "Cost of Owner Dependence Calculator", "key": "calc_annual_cost",
     "numeric": True, "unit": "$", "band": cost_band, "dists": []},
    {"slug": "foundation-readiness-score", "name": "Foundation Readiness Score", "key": "foundation_readiness_score",
     "numeric": True, "unit": "%", "band": foundation_band, "dists": ["weakest_foundation_1"]},
    {"slug": "ai-employee-readiness-assessment", "name": "AI Employee Readiness Assessment", "key": "ai_first_hire",
     "numeric": False, "dists": ["ai_first_hire", "ai_readiness_level"]},
    {"slug": "business-system-finder", "name": "Business System Finder", "key": "recommended_system",
     "numeric": False, "dists": ["recommended_system", "business_stage"]},
    {"slug": "run-without-you-guide", "name": "Run-Without-You Guide", "key": "lm_guide_requested",
     "numeric": False, "dists": ["lm_guide_requested"]},
]

FIXTURE = pathlib.Path(__file__).resolve().parent / "fixtures" / "synthetic-hubspot-contacts.csv"


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        lines = [l for l in f if not l.startswith("#")]  # fixture comment lines
    reader = csv.DictReader(lines)
    by_norm = {norm(h): h for h in reader.fieldnames or []}
    rows = []
    for r in reader:
        rows.append({k: (r.get(by_norm[k]) or "").strip() for k in by_norm})
    return rows, set(by_norm)


def num(s):
    try:
        return float(s.replace("$", "").replace(",", "").replace("%", ""))
    except ValueError:
        return None


def aggregate(rows, cols, since=None, until=None, exclude=("buildwithbpp.com",)):
    if "createdate" not in cols and (since or until):
        sys.exit("--since/--until need a createdate column")
    kept, dropped = [], 0
    for r in rows:
        email = r.get("email", "").lower()
        if any(email.endswith("@" + d) for d in exclude):
            dropped += 1
            continue
        day = r.get("createdate", "")[:10]
        if (since and day < since) or (until and day > until):
            continue
        kept.append(r)
    out = {"_dropped_internal": dropped, "_rows": len(kept), "tools": {}}
    for t in TOOLS:
        key = norm(t["key"])
        res = {"name": t["name"], "n": 0, "missing_column": key not in cols}
        done = [r for r in kept if r.get(key)]
        res["n"] = len(done)
        if t["numeric"]:
            vals = [v for v in (num(r[key]) for r in done) if v is not None]
            res["n"] = len(vals)
            if vals:
                res["median"] = statistics.median(vals)
                res["bands"] = count([t["band"](v) for v in vals])
        for d in t["dists"]:
            res.setdefault("dists", {})[d] = count([r.get(norm(d)) for r in done if r.get(norm(d))])
        res["by_ref"] = count([r.get("lmref") for r in done if r.get("lmref")])
        out["tools"][t["slug"]] = res
    return out


def count(items):
    c = {}
    for i in items:
        c[i] = c.get(i, 0) + 1
    return dict(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


def fmt_val(t, v):
    return "${:,.0f}".format(v) if t["unit"] == "$" else ("%g%%" % v)


def pct(k, n):
    return "%d%%" % round(100 * k / n) if n else "0%"


def report(agg, min_n, publish):
    lines = []
    if not publish:
        lines.append("Rows used: %d (internal test contacts dropped: %d)" % (agg["_rows"], agg["_dropped_internal"]))
    published = 0
    for t in TOOLS:
        r = agg["tools"][t["slug"]]
        ok = r["n"] >= min_n
        if publish and not ok:
            lines.append("WITHHELD  %s: %d completions, under the %d needed to publish" % (t["name"], r["n"], min_n))
            continue
        published += ok
        gate = "publishable" if ok else "NOT publishable (n < %d)" % min_n
        lines.append("")
        lines.append("%s  [%s]" % (t["name"], "n=%d, %s" % (r["n"], gate) if not publish else "n=%d" % r["n"]))
        if r["missing_column"]:
            lines.append("  column not in export: " + t["key"])
        if "median" in r:
            lines.append("  median: %s%s" % (fmt_val(t, r["median"]), " (lower is better)" if t.get("lower_is_better") else ""))
        for label, dist in [("bands", r.get("bands", {}))] + list(r.get("dists", {}).items()):
            if not dist:
                continue
            lines.append("  %s:" % label)
            for k, v in dist.items():
                lines.append("    %-40s %4d  %s" % (k, v, pct(v, r["n"])))
        if not publish and r["by_ref"]:
            lines.append("  by partner ref (lm_ref): " + ", ".join("%s %d" % kv for kv in r["by_ref"].items()))
    if publish and not published:
        lines.append("")
        lines.append("Nothing publishable: every tool is under %d completions." % min_n)
    return "\n".join(lines), published


def self_test():
    rows, cols = read_rows(FIXTURE)
    a = aggregate(rows, cols)
    t = a["tools"]
    checks = [
        ("internal rows dropped", a["_dropped_internal"], 2),
        ("scorecard n", t["owner-dependency-scorecard"]["n"], 55),
        ("scorecard median", t["owner-dependency-scorecard"]["median"], 47),
        ("scorecard bands", t["owner-dependency-scorecard"]["bands"],
         {"Partially Owner-Dependent (35-59%)": 25, "Highly Owner-Dependent (60%+)": 15, "Running on Systems (under 35%)": 15}),
        ("scorecard weakest pillar spread", sorted(t["owner-dependency-scorecard"]["dists"]["weakest_pillar_1"].values()), [11] * 5),
        ("calculator n", t["cost-of-owner-dependence-calculator"]["n"], 12),
        ("calculator median", t["cost-of-owner-dependence-calculator"]["median"], 65000),
        ("calculator bands", t["cost-of-owner-dependence-calculator"]["bands"],
         {"$30K to $99.9K a year": 7, "$100K+ a year": 3, "Under $30K a year": 2}),
        ("foundation n (exactly the floor)", t["foundation-readiness-score"]["n"], 50),
        ("foundation median", t["foundation-readiness-score"]["median"], 54.5),
        ("foundation bands", t["foundation-readiness-score"]["bands"],
         {"Almost Ready (40-69%)": 30, "Foundation First (under 40%)": 10, "Ready to Build (70%+)": 10}),
        ("ai n", t["ai-employee-readiness-assessment"]["n"], 8),
        ("ai first hire", t["ai-employee-readiness-assessment"]["dists"]["ai_first_hire"]["The Follow-Up Assistant"], 3),
        ("ai readiness", t["ai-employee-readiness-assessment"]["dists"]["ai_readiness_level"],
         {"Ready With Light Setup": 4, "Foundations First": 2, "Ready Now": 2}),
        ("system finder n", t["business-system-finder"]["n"], 6),
        ("guide versions", t["run-without-you-guide"]["dists"]["lm_guide_requested"], {"general": 3, "commercial-cleaning": 1}),
        ("partner ref count", t["owner-dependency-scorecard"]["by_ref"], {"example-cpa": 5}),
    ]
    q4 = aggregate(rows, cols, since="2026-10-01", until="2026-12-31")["tools"]
    checks += [
        ("Q4 window scorecard n", q4["owner-dependency-scorecard"]["n"], 50),
        ("Q4 window scorecard median", q4["owner-dependency-scorecard"]["median"], 49.5),
        ("Q4 window calculator n", q4["cost-of-owner-dependence-calculator"]["n"], 7),
    ]
    text, published = report(a, MIN_PUBLISH, publish=True)
    checks += [
        ("publish: tools cleared", published, 2),
        ("publish: calculator withheld", "WITHHELD  Cost of Owner Dependence Calculator: 12 completions" in text, True),
        ("publish: guide withheld", "WITHHELD  Run-Without-You Guide: 4 completions" in text, True),
        ("publish: scorecard shown", "Owner-Dependency Scorecard  [n=55]" in text, True),
        ("publish: no calculator median leaks", "65,000" in text, False),
    ]
    _, none_pub = report(a, 60, publish=True)
    checks.append(("publish at --min 60: nothing clears", none_pub, 0))
    # HubSpot label-style headers map to the same fields
    relabeled = [{norm(k.replace("_", " ").title()): v for k, v in r.items()} for r in rows]
    lab = aggregate(relabeled, {norm(c.replace("_", " ").title()) for c in cols})["tools"]
    checks.append(("label-style headers", lab["owner-dependency-scorecard"]["median"], 47))

    fails = 0
    for label, got, want in checks:
        ok = got == want
        fails += not ok
        print("%s  %s%s" % ("PASS" if ok else "FAIL", label, "" if ok else "  got %r want %r" % (got, want)))
    print("\nself-test on SYNTHETIC fixture: %s" % ("ALL PASS" if not fails else "%d FAILED" % fails))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("csv", nargs="?")
    ap.add_argument("--since", help="YYYY-MM-DD, by createdate")
    ap.add_argument("--until", help="YYYY-MM-DD, by createdate")
    ap.add_argument("--publish", action="store_true", help="print only tools with enough completions to publish")
    ap.add_argument("--min", type=int, default=MIN_PUBLISH, help="publish floor (can be raised, never below %d)" % MIN_PUBLISH)
    ap.add_argument("--exclude-domain", action="append", default=None, help="email domain to drop (default buildwithbpp.com)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if not a.csv:
        ap.error("give a CSV path, or --self-test")
    if a.min < MIN_PUBLISH:
        sys.exit("refusing --min %d: the publish floor is %d completions per tool" % (a.min, MIN_PUBLISH))
    rows, cols = read_rows(a.csv)
    agg = aggregate(rows, cols, a.since, a.until, tuple(a.exclude_domain or ["buildwithbpp.com"]))
    text, published = report(agg, a.min, a.publish)
    print(text)
    if a.publish and not published:
        sys.exit(2)


if __name__ == "__main__":
    main()
