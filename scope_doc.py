#!/usr/bin/env python3
"""Generate a free public pitch and a paid confidential scope document from one JSON file.
Zero dependencies."""
import argparse
import html
import json
import sys


def esc(s):
    return html.escape(str(s))


def base_style():
    return """
body{font-family:-apple-system,Arial,sans-serif;max-width:680px;margin:40px auto;color:#1a1a1a}
h1{font-size:22px}
h2{font-size:15px;text-transform:uppercase;color:#666;margin-top:28px;margin-bottom:4px}
.meta{color:#666;font-size:14px}
ul{margin-top:4px}
.banner{padding:10px 14px;border-radius:6px;font-size:13px;margin-bottom:20px}
.watermark{color:#999;font-size:12px;margin-top:48px;border-top:1px solid #ddd;padding-top:12px}
@media print{body{margin:0}}
"""


def render_public(data):
    client = esc(data.get("client", ""))
    sender = esc(data.get("from", ""))
    date = esc(data.get("date", ""))
    summary = esc(data.get("project_summary", ""))
    outcome = esc(data.get("outcome", ""))
    highlights = "\n".join(f"<li>{esc(h)}</li>" for h in data.get("approach_highlights", []))
    fee = data.get("scope_fee")
    fee_note = esc(data.get("scope_fee_credit_note", ""))

    cta = ""
    if fee:
        cta = f"""<h2>Next step</h2>
<p>The detailed technical scope, implementation plan, and timeline are prepared as a separate
paid document (scope fee: <strong>${fee:,.2f}</strong>{" — " + fee_note if fee_note else ""}).
This keeps the free pitch focused on outcomes, and gives you a concrete, paid deliverable
instead of free consulting handed out during the pitch.</p>"""

    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>{client} — Proposal overview</title>
<style>{base_style()}</style></head><body>
<h1>{client} — Proposal overview</h1>
<p class="meta">From: {sender} &middot; Date: {date}</p>

{"<h2>Summary</h2><p>" + summary + "</p>" if summary else ""}
{"<h2>Expected outcome</h2><p>" + outcome + "</p>" if outcome else ""}
{"<h2>Approach</h2><ul>" + highlights + "</ul>" if highlights else ""}
{cta}
</body></html>"""


def render_paid(data):
    client = esc(data.get("client", ""))
    sender = esc(data.get("from", ""))
    date = esc(data.get("date", ""))
    scope_items = "\n".join(f"<li>{esc(s)}</li>" for s in data.get("detailed_scope", []))
    deliverables = "\n".join(f"<li>{esc(d)}</li>" for d in data.get("deliverables", []))
    timeline = esc(data.get("timeline", ""))

    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>{client} — Confidential scope document</title>
<style>{base_style()}</style></head><body>
<div class="banner" style="background:#fff3cd;color:#664d03">CONFIDENTIAL — prepared exclusively
for {client}. Not for redistribution.</div>
<h1>{client} — Detailed scope</h1>
<p class="meta">Prepared by: {sender} &middot; Date: {date}</p>

{"<h2>Detailed scope</h2><ul>" + scope_items + "</ul>" if scope_items else ""}
{"<h2>Deliverables</h2><ul>" + deliverables + "</ul>" if deliverables else ""}
{"<h2>Timeline</h2><p>" + timeline + "</p>" if timeline else ""}

<p class="watermark">This document was prepared exclusively for {client} on {date} as a paid
scoping deliverable. It is not a license to redistribute, resell, or hand off the contained
architecture/plan to a third party without the author's consent.</p>
</body></html>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", help="JSON scope file (see example.json)")
    ap.add_argument("--public", default="public-pitch.html", help="output path for the free pitch")
    ap.add_argument("--paid", default="paid-scope.html", help="output path for the paid scope doc")
    ap.add_argument("--public-only", action="store_true", help="only write the free pitch")
    args = ap.parse_args()

    try:
        with open(args.input) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    if not data.get("client"):
        print("Error: JSON must include 'client'", file=sys.stderr)
        sys.exit(1)

    with open(args.public, "w") as f:
        f.write(render_public(data))
    print(f"wrote {args.public}", file=sys.stderr)

    if not args.public_only:
        with open(args.paid, "w") as f:
            f.write(render_paid(data))
        print(f"wrote {args.paid}", file=sys.stderr)


if __name__ == "__main__":
    main()
