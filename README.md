# freelance-scope-doc-cli

Generate a **free public pitch** and a **paid confidential scope document** from one JSON file.
Zero dependencies.

## Why

A common freelance failure mode: you send a client a single detailed proposal — full technical
breakdown, architecture, implementation plan — to win the work, and they take it and execute it
themselves or hand it to a cheaper freelancer. ([real](https://www.reddit.com/r/freelance/comments/1x3z60b/)
[examples](https://www.reddit.com/r/freelance/comments/1x7vsd6/) of this happening.)

The fix isn't to withhold information and hope the client trusts you anyway — it's to structure
the pitch in two separate documents from the start:

1. A **free public pitch** — what you'd do and why, the expected outcome, high-level approach.
   Enough to build confidence, nothing a competitor could execute from.
2. A **paid scope document** — the actual implementation plan, architecture, step-by-step scope,
   deliverables, and timeline. Marked confidential, prepared for one named client, paid for
   separately (a scope fee, typically credited toward the project if they move forward).

This tool generates both from one input file, so the split is the default, not an afterthought.

## Usage

Runs via Python or directly via `npx` (no install), same logic, same output:
```
npx github:kleogeos/freelance-scope-doc-cli scope.json
```

```
python3 scope_doc.py scope.json
# writes public-pitch.html and paid-scope.html

python3 scope_doc.py scope.json --public-only
# writes only public-pitch.html (e.g. for the free discovery-call follow-up)
```

See [example.json](example.json) for the input shape.

## Fields

| Field | Goes in | Notes |
|---|---|---|
| `client`, `from`, `date` | both | required: `client` |
| `project_summary`, `outcome`, `approach_highlights` | public pitch | safe to hand out free |
| `scope_fee`, `scope_fee_credit_note` | public pitch | shown as the CTA to the paid doc |
| `detailed_scope`, `deliverables`, `timeline` | paid doc only | never appears in the public pitch |

The paid document carries a "prepared exclusively for `<client>` on `<date>`" line — not
enforceable on its own, but it turns a generic PDF into something with the client's name on it,
which is useful context if a dispute ever needs a paper trail.

## Testing

```
python3 test.py
```

Covers: HTML-escaping of user input (XSS), confidential fields never leaking into the public
doc, `--public-only` mode, and the three input-validation error paths.

## License

MIT

---

Part of the [Freelancer Toolbox](https://kleogeos.github.io/freelancer-tools/) — zero-dependency
CLI tools for freelance admin (invoicing, contracts, NDAs, time tracking, and more).
