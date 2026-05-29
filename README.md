# Claude API Lab — Catalog Normalization (STARTER branch)

> **You are on the `retail` starter branch.** The structure, tool *schemas*, agent loop,
> sample data, and tests are in place, but the tool logic, system prompt, and data schemas are
> **fill-in-the-blank**. You implement them step by step. The finished reference is on the
> **`retail-solution`** branch — peek if you get stuck.

Build a tool-using agent that onboards a supplier product feed into a canonical catalog: Claude
drives a tool-use loop that parses the feed, validates SKUs/GTINs, maps free-text categories to
the canonical taxonomy, and produces an import report. Built for the **Claude API Lab** workshop
(Module 2.2, retail variant).

Built by [Provectus](https://provectus.com/).

## What you'll implement

| Step | Where | What |
|------|-------|------|
| 4 — Schema | `backend/app/schemas/{canonical_product_v1,catalog_rules,taxonomy_v1}.json` | Fill in the product shape, validation rules, and category taxonomy (`_TODO_step_4`). |
| 5 — Prompt | `backend/app/prompts/catalog_steward.md` | Flesh out persona, workflow, bucketing rules, output contract. |
| 6 — Tool 1 | `backend/app/tools/parse_supplier_feed.py` | Feed + column map → canonical products. |
| 7 — Tool 2 | `backend/app/tools/validate_skus.py` | SKU / GTIN check digit / price validation. |
| 8 — Tool 3 | `backend/app/tools/map_to_canonical_taxonomy.py` | Fuzzy-match categories to the taxonomy. |
| 9 — Tool 4 | `backend/app/tools/generate_import_report.py` | The final import report. |
| 10 — Loop | `backend/app/services/agent_runner.py` | Already wired — read it to understand the loop. |

Each tool keeps its `NAME` and `DEFINITION`; only the `execute()` body is a
`NotImplementedError` TODO. The registry already lists all four. The `_common.py` helpers
`gtin_check_digit_valid` and `best_taxonomy_match` (rapidfuzz) are provided for Steps 7–8.

## Your progress meter: the tests

```bash
cd backend
uv venv --python 3.12 .venv && uv pip install -e ".[dev]"
.venv/bin/python -m pytest
```

Out of the box, the **plumbing** tests (agent loop, SSE routes, store, uploads) pass, while
`tests/test_catalog_tools.py` and the schema-loader tests **fail** — that's your worklist.
`tests/test_catalog_tools.py` is the exact contract for each tool.

## Run it

```bash
cd backend
cp ../.env.example ../.env        # add ANTHROPIC_API_KEY
.venv/bin/uvicorn app.main:app --reload --port 8000
cd ../frontend && npm install && npm run dev      # http://localhost:3000
# or both: docker compose up --build
```

The app boots immediately; until you implement the tools, a pipeline run streams the agent's
reasoning then surfaces tool errors (`NotImplementedError`). Each step you finish makes the
corresponding tool real.

## Sample data

Two supplier feeds under `sample-data/`, surfaced via `GET /api/pipeline/scenarios`:

| Feed | Expected outcome (once implemented) |
|------|-------------------------------------|
| `northwind_feed` | **import_clean** — valid products, categories map confidently |
| `globalmart_feed` | **import_with_review / hold** — bad GTIN + missing price (reject), fuzzy categories (review) |
