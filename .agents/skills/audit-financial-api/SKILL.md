---
name: audit-financial-api
description: Audit raw REST, JSON, JSONL, and captured realtime financial API responses for backend data-quality and contract problems. Use when Codex must inspect current finance or market payloads, detect inconsistent casing, invalid or retired ISO 4217 currencies, missing exchange rates, unsafe numeric representations, malformed dates, quote/candle invariant violations, duplicate normalized identifiers, or schema drift, then create a backend-ready Markdown, JSON, and optional PDF report.
---

# Audit Financial API

Audit the raw server response before application transforms can normalize or hide defects. Produce evidence that backend developers can act on without exposing secrets or full personal payloads.

## Workflow

1. Read repository instructions and the finance, realtime, security, and delivery rules that apply.
2. Locate the actual boundary:
   - Prefer the current local HTTP endpoint for REST.
   - Use an explicitly supplied URL only when the user authorized live access.
   - Use a captured `.json` or `.jsonl` file for WebSocket/realtime messages.
   - Do not infer API behavior only from UI state when a raw response can be captured.
3. Inspect schemas, adapters, fixtures, and route handlers. Record whether each contract describes upstream input, normalized internal data, or public response output.
4. Run `scripts/audit_financial_api.py` against the raw capture. Add `--profile svelte-portfolio` for this repository's `/api/portfolio` response and use repeated `--allow-code` arguments for explicitly supported non-ISO assets such as crypto tickers.
5. Review every finding against the source contract. Remove false positives only with written evidence; otherwise keep uncertainty and lower severity.
6. Write the structured JSON and Markdown reports. Keep endpoint URLs free of query strings, redact credentials, and include only small scalar evidence.
7. If PDF is useful, run `scripts/render_report_pdf.py`, render every page to PNG, and visually verify typography, tables, page numbers, clipping, and Cyrillic glyphs.
8. Deliver the report, raw-capture location if safe, exact commands, limitations, and the highest-priority backend actions.

## Commands

Audit a local endpoint:

```powershell
python scripts/audit_financial_api.py `
  --url http://127.0.0.1:5173/api/portfolio `
  --profile svelte-portfolio `
  --output-json reports/financial-api-audit.json `
  --output-md reports/financial-api-audit.md `
```

Audit a REST capture or JSONL realtime capture:

```powershell
python scripts/audit_financial_api.py `
  --input path/to/capture.jsonl `
  --profile realtime `
  --output-json reports/financial-api-audit.json `
  --output-md reports/financial-api-audit.md
```

Generate PDF:

```powershell
python scripts/render_report_pdf.py `
  reports/financial-api-audit.md `
  output/pdf/financial-api-audit.pdf
```

The auditor exits with `0` when no high/critical finding exists, `2` when a high/critical finding exists, and `1` for an operational failure.

## Validation Scope

Treat the following as core checks:

- HTTP status, JSON content type, payload size, and parseability.
- Leading/trailing whitespace, lowercase/mixed-case codes, normalized-key collisions, and inconsistent representations.
- Active ISO 4217 membership for currency fields and both legs of six-letter FX symbols.
- Decimal syntax, finite and positive rates, and numeric JSON values that can lose financial precision.
- Missing rates for currencies used by financial records; base-rate presence and equality to one.
- Canonical dates, timestamp units/ranges, staleness, and realtime sequence monotonicity.
- `ask >= bid` and `low <= open/close <= high`.
- Project-specific raw-input versus normalized-output schema drift.

Do not label every unknown three-letter asset a currency error. If the contract permits funds, metals, crypto, loyalty units, or internal assets, classify them with the documented allowlist.

## Current Repository Profile

When auditing Northstar Finance Terminal, read [references/svelte-finance-contract.md](references/svelte-finance-contract.md). Use [references/iso4217-current.txt](references/iso4217-current.txt) as the offline active-code snapshot. Refresh it from the official SIX ISO 4217 List One when the snapshot is stale or the audit concerns a recent currency change.

## Report Requirements

Lead with a release decision and severity counts. For each finding include:

- stable ID and severity;
- machine-readable code and JSON path;
- small observed value and explicit expectation;
- user/business risk;
- backend recommendation;
- reproduction note.

Separate confirmed defects from contract questions and coverage limitations. Never include authorization headers, cookies, API keys, query tokens, full upstream payloads, or personal financial records.
