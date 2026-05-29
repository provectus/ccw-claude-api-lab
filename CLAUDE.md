# ccw-claude-api-lab — retail

Reference app for the **Claude API Lab** workshop (Module 2.2, retail variant): an agentic
**product-catalog normalization** demo. Claude drives a tool-use loop over four tools (parse →
validate → map taxonomy → report) against the Anthropic Messages API. FastAPI backend +
React 19 frontend over SSE.

## Overview

See [README.md](README.md) for setup, the tool list, and sample data.

**This is the `retail-solution` branch — the finished reference / answer key.** The **`retail`**
starter branch stubs the four tool `execute()` bodies, the system prompt, and the schemas as
fill-in-the-blank TODOs. Plumbing is shared with `main` (loan), `finance`, and `healthcare`;
only the domain layer differs.

## Dev Commands

```bash
cd backend
uv venv --python 3.12 .venv && uv pip install -e ".[dev]"
.venv/bin/python -m pytest                 # 68 unit/route tests; 1 integration test skips without API key
.venv/bin/uvicorn app.main:app --reload --port 8000
cd ../frontend && npm install && npm run dev   # :3000
```

## Architecture Notes

- **Agent loop**: `services/agent_runner.py:run_agent()` — loops until `stop_reason == "end_turn"`
  (max 25). Loads `prompts/catalog_steward.md`; captures the `generate_import_report` result as
  `pipeline.assessment`.
- **Tool contract**: each module in `tools/` exports `NAME`, `DEFINITION`, and
  `async execute(input_data, settings) -> dict`. Register via `_TOOL_MODULES` in `tools/registry.py`.
- **Schema-driven**: `schemas/canonical_product_v1.json` (data shape), `schemas/catalog_rules.json`
  (SKU/GTIN/price rules), `schemas/taxonomy_v1.json` (canonical category paths + fuzzy thresholds).
  `_common.py` has `gtin_check_digit_valid` (EAN-13 mod-10), `best_taxonomy_match` (rapidfuzz
  WRatio wrapper), loaders, `safe_json_serialize`.
- **SSE pipeline**: `api/routes/pipeline.py` — `/run`, `/{id}/stream`, `/{id}/assessment`,
  `/scenarios` (the two `sample-data/` feeds).

## Status / Gotchas

- Backend domain layer is complete and tested; the **frontend** still carries the upstream
  finance-demo's NAV visualization components (generic streaming works; domain viz does not).
  `frontend/e2e/*.spec.ts` are inherited NAV Playwright tests, not part of backend `pytest`.
- A product is "ready" only if `validate_skus` passes it AND `map_to_canonical_taxonomy` maps it
  confidently — the agent reconciles the two signals by row index / SKU.
- `globalmart_feed` intentionally carries a bad GTIN check digit + a missing price (rejects) and
  noisy categories (review) to exercise every bucket.
- The pipeline run-request field is still named `fund_metadata` (a generic "request metadata"
  holdover shared across all branches' plumbing).

## Cross-Project

- Pairs with the `cc-workshop` platform (`claude-api-lab-retail.json`).
- Architecture mirrors `provectus/finance-demo` and the `main`/`finance`/`healthcare` branches.
