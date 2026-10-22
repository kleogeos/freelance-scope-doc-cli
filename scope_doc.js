#!/usr/bin/env node
// Generate a free public pitch and a paid confidential scope document from one JSON file.
// Zero dependencies, runs via npx straight from GitHub.
const fs = require("fs");

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

const BASE_STYLE = `
body{font-family:-apple-system,Arial,sans-serif;max-width:680px;margin:40px auto;color:#1a1a1a}
h1{font-size:22px}
h2{font-size:15px;text-transform:uppercase;color:#666;margin-top:28px;margin-bottom:4px}
.meta{color:#666;font-size:14px}
ul{margin-top:4px}
.banner{padding:10px 14px;border-radius:6px;font-size:13px;margin-bottom:20px}
.watermark{color:#999;font-size:12px;margin-top:48px;border-top:1px solid #ddd;padding-top:12px}
@media print{body{margin:0}}
`;

function renderPublic(data) {
  const client = esc(data.client);
  const sender = esc(data.from);
  const date = esc(data.date);
  const summary = esc(data.project_summary);
  const outcome = esc(data.outcome);
  const highlights = (data.approach_highlights || []).map((h) => `<li>${esc(h)}</li>`).join("\n");
  const fee = data.scope_fee;
  const feeNote = esc(data.scope_fee_credit_note);

  let cta = "";
  if (fee) {
    cta = `<h2>Next step</h2>
<p>The detailed technical scope, implementation plan, and timeline are prepared as a separate
paid document (scope fee: <strong>$${Number(fee).toFixed(2)}</strong>${feeNote ? " — " + feeNote : ""}).
This keeps the free pitch focused on outcomes, and gives you a concrete, paid deliverable
instead of free consulting handed out during the pitch.</p>`;
  }

  return `<!doctype html><html><head><meta charset="utf-8">
<title>${client} — Proposal overview</title>
<style>${BASE_STYLE}</style></head><body>
<h1>${client} — Proposal overview</h1>
<p class="meta">From: ${sender} &middot; Date: ${date}</p>

${summary ? `<h2>Summary</h2><p>${summary}</p>` : ""}
${outcome ? `<h2>Expected outcome</h2><p>${outcome}</p>` : ""}
${highlights ? `<h2>Approach</h2><ul>${highlights}</ul>` : ""}
${cta}
</body></html>`;
}

function renderPaid(data) {
  const client = esc(data.client);
  const sender = esc(data.from);
  const date = esc(data.date);
  const scopeItems = (data.detailed_scope || []).map((s) => `<li>${esc(s)}</li>`).join("\n");
  const deliverables = (data.deliverables || []).map((d) => `<li>${esc(d)}</li>`).join("\n");
  const timeline = esc(data.timeline);

  return `<!doctype html><html><head><meta charset="utf-8">
<title>${client} — Confidential scope document</title>
<style>${BASE_STYLE}</style></head><body>
<div class="banner" style="background:#fff3cd;color:#664d03">CONFIDENTIAL — prepared exclusively
for ${client}. Not for redistribution.</div>
<h1>${client} — Detailed scope</h1>
<p class="meta">Prepared by: ${sender} &middot; Date: ${date}</p>

${scopeItems ? `<h2>Detailed scope</h2><ul>${scopeItems}</ul>` : ""}
${deliverables ? `<h2>Deliverables</h2><ul>${deliverables}</ul>` : ""}
${timeline ? `<h2>Timeline</h2><p>${timeline}</p>` : ""}

<p class="watermark">This document was prepared exclusively for ${client} on ${date} as a paid
scoping deliverable. It is not a license to redistribute, resell, or hand off the contained
architecture/plan to a third party without the author's consent.</p>
</body></html>`;
}

function main() {
  const args = process.argv.slice(2);
  if (args.length === 0 || args.includes("-h") || args.includes("--help")) {
    console.error("Usage: scope_doc.js <input.json> [--public FILE] [--paid FILE] [--public-only]");
    process.exit(args.length === 0 ? 1 : 0);
  }

  const input = args[0];
  let publicOut = "public-pitch.html";
  let paidOut = "paid-scope.html";
  let publicOnly = false;
  for (let i = 1; i < args.length; i++) {
    if (args[i] === "--public") publicOut = args[++i];
    else if (args[i] === "--paid") paidOut = args[++i];
    else if (args[i] === "--public-only") publicOnly = true;
  }

  let raw;
  try {
    raw = fs.readFileSync(input, "utf8");
  } catch {
    console.error(`Error: file not found: ${input}`);
    process.exit(1);
  }

  let data;
  try {
    data = JSON.parse(raw);
  } catch (e) {
    console.error(`Error: invalid JSON in ${input}: ${e.message}`);
    process.exit(1);
  }

  if (!data.client) {
    console.error("Error: JSON must include 'client'");
    process.exit(1);
  }

  fs.writeFileSync(publicOut, renderPublic(data));
  console.error(`wrote ${publicOut}`);

  if (!publicOnly) {
    fs.writeFileSync(paidOut, renderPaid(data));
    console.error(`wrote ${paidOut}`);
  }
}

main();
