# ccw-claude-api-lab — legal

Reference app for the **Claude API Lab** workshop (Module 2.2, legal variant): an agentic
**SaaS contract review** demo. Claude drives a tool-use loop over four tools (parse PDF →
extract clauses → evaluate risk → memo) against the Anthropic Messages API. FastAPI backend +
React 19 frontend over SSE.

## Overview

See [README.md](README.md) for setup, the tool list, and sample data.

**This is the `legal` STARTER branch.** The four tool `execute()` bodies are
`NotImplementedError` TODOs, and `prompts/contract_reviewer.md` + the three `schemas/*.json`
files are fill-in-the-blank skeletons (search `TODO` / `_TODO_step_4`). `NAME`/`DEFINITION`, the
agent loop, registry, `_common` helpers, the `parse_contract_pdf._extract_*` helpers, sample
data, and tests are in place. The finished reference is on the **`legal-solution`** branch.
Plumbing is shared with `main` (loan), `finance`, `healthcare`, and `retail`; only the domain
layer differs.

## Dev Commands

```bash
cd backend
uv venv --python 3.12 .venv && uv pip install -e ".[dev]"   # ".[dev,parsers]" enables Docling/LlamaParse
.venv/bin/python -m pytest                 # 64 unit/route tests; 1 integration test skips without API key
.venv/bin/uvicorn app.main:app --reload --port 8000
cd ../frontend && npm install && npm run dev   # :3000
```

## Architecture Notes

- **Agent loop**: `services/agent_runner.py:run_agent()` — loops until `stop_reason == "end_turn"`
  (max 25). Loads `prompts/contract_reviewer.md`; captures the `generate_review_memo` result as
  `pipeline.assessment`.
- **Native PDF**: `parse_contract_pdf` sends the PDF to Claude as a `document` content block
  (native PDF support — text + per-page vision, ZDR-**eligible** but ZDR is an org-level
  arrangement, not automatic). It is the **one model-calling tool**; `method="docling"` /
  `"llamaparse"` are optional, lazily-imported fallbacks (`[parsers]` extra). The other three
  tools are deterministic.
- **Tool contract**: each module in `tools/` exports `NAME`, `DEFINITION`, and
  `async execute(input_data, settings) -> dict`. Register via `_TOOL_MODULES` in `tools/registry.py`.
- **Schema-driven**: `schemas/canonical_contract_v1.json` (clause structure),
  `schemas/clause_patterns.json` (heading keywords for `extract_clauses`),
  `schemas/risk_rules.json` (thresholds + required clauses for `evaluate_clause_risk`).
  `_common.py` has `pdf_to_base64`, `extract_section` (heading-delimited section grab),
  `first_int`, `safe_json_serialize`.
- **SSE pipeline**: `api/routes/pipeline.py` — `/run`, `/{id}/stream`, `/{id}/assessment`,
  `/scenarios` (the two `sample-data/` MSAs).

## Status / Gotchas

- **Starter branch:** `pytest` is intentionally partly red out of the box — `test_legal_tools.py`
  and the schema-loader tests fail until the learner implements Steps 4–9. The plumbing tests pass.
  That red/green split is the workshop's progress meter, not breakage.
- The app boots and streams immediately; tool calls return `NotImplementedError` until implemented.
- `parse_contract_pdf`'s unit test mocks `anthropic.AsyncAnthropic`, so `pytest` stays offline;
  a real run / the integration test needs `ANTHROPIC_API_KEY`.
- `extract_clauses` is heuristic (regex over headings) — the sample MSAs use clean numbered
  headings so extraction is deterministic; `vendorco_msa` omits a confidentiality clause and
  carries a 90-day auto-renewal trap to drive the high-risk path.
- Sample PDFs were generated from the `.txt` sources via `cupsfilter`; both are committed.
- The **frontend** still carries the upstream finance-demo's NAV visualization components
  (generic streaming works; domain viz does not). `frontend/e2e/*.spec.ts` are inherited NAV
  Playwright tests, not part of backend `pytest`.
- The pipeline run-request field is still named `fund_metadata` (a generic "request metadata"
  holdover shared across all branches' plumbing).

## Cross-Project

- Pairs with the `cc-workshop` platform (`claude-api-lab-legal.json`).
- Architecture mirrors `provectus/finance-demo` and the `main`/`finance`/`healthcare`/`retail` branches.
