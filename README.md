# Claude API Lab — Product Catalog Normalization Agent

Reference implementation for the **Claude API Lab** workshop (Module 2.2, retail variant). An
agentic demo that onboards a supplier product feed into a canonical catalog: Claude drives a
tool-use loop that parses the feed, validates SKUs/GTINs, maps free-text categories to the
canonical taxonomy, and produces an import report — no hardcoded step sequence, the model
decides which tool to call next.

> This is the **`retail-solution`** branch — the finished reference / answer key for the
> **`retail`** starter branch (whose tool bodies, prompt, and schemas are stubbed TODOs). The
> workshop content lives in the [`cc-workshop`](https://github.com/provectus) platform.

Built by [Provectus](https://provectus.com/).

## Architecture

```
React 19 Frontend  ◄──SSE──►  FastAPI Backend  ◄──tool use──►  Claude Sonnet 4.6
```

The agent loop in `backend/app/services/agent_runner.py` calls Claude, dispatches each
`tool_use` block, appends `tool_result`s, and loops until `stop_reason == "end_turn"`
(capped at 25 iterations). The result of `generate_import_report` becomes the pipeline assessment.

## The four tools

Registered in `backend/app/tools/registry.py`:

1. **`parse_supplier_feed`** — folder (`feed.csv` + `supplier_meta.json` column map) → canonical product rows.
2. **`validate_skus`** — SKU format, **GTIN mod-10 check digit**, price, required fields → per-row issues.
3. **`map_to_canonical_taxonomy`** — **fuzzy-matches** (rapidfuzz) each supplier category to the canonical taxonomy → mapped / needs_review / unmapped.
4. **`generate_import_report`** — the final report (import_clean / import_with_review / hold) with ready/review/rejected counts. Its output becomes the pipeline assessment.

System prompt: `backend/app/prompts/catalog_steward.md`. Schemas:
`canonical_product_v1.json`, `catalog_rules.json`, `taxonomy_v1.json`.

## Quick start

### Backend (Python 3.12)
```bash
cd backend
uv venv --python 3.12 .venv && source .venv/bin/activate   # or python3.12 -m venv .venv
uv pip install -e ".[dev]"
cp ../.env.example ../.env       # add ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend && npm install && npm run dev   # http://localhost:3000
```

### Docker (both)
```bash
cp .env.example .env && docker compose up --build
```

## Sample data

Two supplier feeds under `sample-data/`, surfaced via `GET /api/pipeline/scenarios`:

| Feed | Expected outcome |
|------|------------------|
| `northwind_feed` | **import_clean** — 3 valid products, all categories map confidently |
| `globalmart_feed` | **import_with_review / hold** — 1 bad GTIN + 1 missing price (rejected), 2 low-confidence categories (review) |

## Tests

```bash
cd backend
.venv/bin/python -m pytest                    # unit + route tests
.venv/bin/python -m pytest -m integration     # full agentic loop (needs ANTHROPIC_API_KEY)
```

## Status notes

- The **backend** domain layer (tools, schemas, prompt, agent loop, sample data, tests) is the
  workshop's teaching core and is fully implemented and tested here.
- The **frontend** streams the agent's reasoning and tool calls generically; its
  domain-specific visualization components are inherited from the upstream finance demo and are
  not retailored to catalog normalization (tracked as follow-up; not on the core path).
