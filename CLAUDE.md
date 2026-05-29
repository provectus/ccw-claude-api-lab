# ccw-claude-api-lab

Reference app for the **Claude API Lab** workshop (Module 2.2): an agentic commercial
loan-underwriting demo. Claude drives a tool-use loop over four tools (parse → validate →
compute ratios → assess) against the Anthropic Messages API. FastAPI backend + React 19
frontend wired over SSE.

## Overview

See [README.md](README.md) for setup, the tool list, and sample data.

**This is the `finance` STARTER branch.** The four tool `execute()` bodies are
`NotImplementedError` TODOs, and `prompts/credit_analyst.md` + the two `schemas/*.json`
files are fill-in-the-blank skeletons (search `TODO` / `_TODO_step_4`). `NAME`/`DEFINITION`,
the agent loop, registry, `_common` helpers, sample data, and tests are all in place. The
finished reference is on the **`finance-solution`** branch. Scaffolding lifted from the
`finance-demo` (NAV Review Analyst) architecture, domain layer rewritten for loan underwriting.

## File Structure

```bash
eza -TL 3 --icons --git-ignore
```

## Dev Commands

```bash
# Backend (Python 3.12)
cd backend
uv venv --python 3.12 .venv && uv pip install -e ".[dev]"
.venv/bin/python -m pytest                 # 80 unit/route tests; 1 integration test skips without API key
.venv/bin/uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev   # :3000

# Both via Docker
docker compose up --build
```

## Architecture Notes

- **Agent loop**: `backend/app/services/agent_runner.py` — loops `messages.create` until
  `stop_reason == "end_turn"` (max 25 iterations). Loads `prompts/credit_analyst.md`.
  Captures the `assess_creditworthiness` result as `pipeline.assessment`.
- **Tool contract**: each module in `backend/app/tools/` exports `NAME`, `DEFINITION`
  (Anthropic tool schema), and `async execute(input_data, settings) -> dict`. Register by
  adding the module to `_TOOL_MODULES` in `tools/registry.py` (explicit, not auto-discovered).
- **Tool executor**: `services/tool_executor.py` runs live, then falls back to
  `backend/data/fallbacks/<tool>.json` if present and `FALLBACK_ENABLED` (no fallback files
  shipped here → live errors surface as `source: "error"`).
- **Schema-driven**: `schemas/canonical_loan_application_v1.json` (the data shape) +
  `schemas/validation_rules.json` (policy bounds). `_common.py` has numeric/format helpers
  (`amortized_annual_debt_service`, `safe_div`, `safe_json_serialize`, …).
- **SSE pipeline**: `api/routes/pipeline.py` — `/run`, `/{id}/stream`, `/{id}/assessment`,
  `/scenarios` (the three `sample-data/` packages). `sample_data_dir` resolves from config.

## Status / Gotchas

- **Starter branch:** `pytest` is intentionally partly red out of the box — `test_loan_tools.py`
  and the validation-rules tests fail until the learner implements Steps 4–9. The plumbing
  tests (agent loop, routes, store, uploads, `_common` helpers) pass. That red/green split is
  the workshop's progress meter, not breakage.
- The app boots and streams immediately; tool calls return `NotImplementedError` errors until
  implemented (tool_executor surfaces them as `source: "error"`).
- The **frontend** still carries the upstream finance-demo's NAV visualization components —
  generic streaming works, domain viz does not yet match loan underwriting (follow-up).
  `frontend/e2e/*.spec.ts` are inherited NAV Playwright tests, not part of backend `pytest`.
- Three years of financials is a hard validation rule; `charlie_retail` (2 years)
  intentionally exercises the error path.

## Cross-Project

- Pairs with the `cc-workshop` platform (workshop JSON templates).
- Architecture mirrors `provectus/finance-demo` and `provectus/claude-api-demo`.
