# ccw-claude-api-lab — healthcare

Reference app for the **Claude API Lab** workshop (Module 2.2, healthcare variant): an
agentic outpatient **prior-authorization review** demo. Claude drives a tool-use loop over
four tools (parse → validate → check policy → decide) against the Anthropic Messages API.
FastAPI backend + React 19 frontend over SSE.

## Overview

See [README.md](README.md) for setup, the tool list, and sample data.

**This is the `healthcare-solution` branch — the finished reference / answer key.** The
**`healthcare`** starter branch stubs the four tool `execute()` bodies, the system prompt, and
the schemas as fill-in-the-blank TODOs. Architecture (plumbing) is shared with the `main`
(loan-underwriting) and `finance` branches; only the domain layer differs.

## Dev Commands

```bash
cd backend
uv venv --python 3.12 .venv && uv pip install -e ".[dev]"
.venv/bin/python -m pytest                 # 74 unit/route tests; 1 integration test skips without API key
.venv/bin/uvicorn app.main:app --reload --port 8000
cd ../frontend && npm install && npm run dev   # :3000
```

## Architecture Notes

- **Agent loop**: `services/agent_runner.py:run_agent()` — loops until `stop_reason == "end_turn"`
  (max 25). Loads `prompts/clinical_reviewer.md`; captures the `recommend_decision` result as
  `pipeline.assessment`.
- **Tool contract**: each module in `tools/` exports `NAME`, `DEFINITION`, and
  `async execute(input_data, settings) -> dict`. Register via `_TOOL_MODULES` in `tools/registry.py`.
- **Schema-driven**: `schemas/canonical_pa_request_v1.json` (data shape),
  `schemas/criteria_rules.json` (structural validation), `schemas/payer_policies_v1.json`
  (per-CPT medical-necessity criteria evaluated by `check_payer_policy`). `_common.py` has
  `get_path` (dotted-path getter), `eval_criterion` (operator eval), loaders, `safe_json_serialize`.
- **SSE pipeline**: `api/routes/pipeline.py` — `/run`, `/{id}/stream`, `/{id}/assessment`,
  `/scenarios` (the three `sample-data/` PA requests).

## Status / Gotchas

- Backend domain layer is complete and tested; the **frontend** still carries the upstream
  finance-demo's NAV visualization components (generic streaming works; domain viz does not).
- `frontend/e2e/*.spec.ts` are inherited NAV Playwright tests, not part of backend `pytest`.
- `check_payer_policy` is deterministic: `meets_policy` is true only when every criterion in
  the CPT's policy passes. `incomplete_request` (no primary dx, missing clinical fields)
  intentionally exercises the validation / pend-for-info path.
- The pipeline run-request field is still named `fund_metadata` (a generic "request metadata"
  holdover shared across all branches' plumbing).

## Cross-Project

- Pairs with the `cc-workshop` platform (`claude-api-lab-healthcare.json`).
- Architecture mirrors `provectus/finance-demo` and the `main`/`finance` branches.
