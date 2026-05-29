# Claude API Lab — Loan Underwriting (STARTER branch)

> **You are on the `finance` starter branch.** This is the hands-on workshop scaffold:
> the structure, tool *schemas*, agent loop, sample data, and tests are all in place, but
> the tool logic, system prompt, and schemas are **fill-in-the-blank**. You implement them
> step by step. The finished reference lives on the **`finance-solution`** branch — peek if you get stuck.

Build a tool-using agent that underwrites a small-business loan: Claude drives a tool-use
loop that parses a borrower package, validates it, computes credit ratios, and produces a
structured creditworthiness assessment. Built for the **Claude API Lab** workshop (Module 2.2).

Built by [Provectus](https://provectus.com/).

## What you'll implement

| Step | Where | What |
|------|-------|------|
| 4 — Schema | `backend/app/schemas/canonical_loan_application_v1.json`, `validation_rules.json` | Fill in the canonical fields + policy rule values (look for `_TODO_step_4`). |
| 5 — Prompt | `backend/app/prompts/credit_analyst.md` | Flesh out the persona, workflow, criteria, and output contract (look for `TODO`). |
| 6 — Tool 1 | `backend/app/tools/parse_loan_package.py` | Folder → canonical `LoanApplication`. |
| 7 — Tool 2 | `backend/app/tools/validate_loan_application.py` | Apply the validation rules. |
| 8 — Tool 3 | `backend/app/tools/compute_credit_ratios.py` | DSCR, current ratio, D/E, margin trend, CAGR, LTV. |
| 9 — Tool 4 | `backend/app/tools/assess_creditworthiness.py` | The final structured verdict. |
| 10 — Loop | `backend/app/services/agent_runner.py` | Already wired — read it to understand the loop. |

Each tool keeps its `NAME` and `DEFINITION` (so Claude already sees the tool schemas);
only the `execute()` body is a `NotImplementedError` TODO. The tool registry
(`backend/app/tools/registry.py`) already lists all four.

## Your progress meter: the tests

```bash
cd backend
uv venv --python 3.12 .venv && uv pip install -e ".[dev]"   # or python3.12 -m venv + pip
.venv/bin/python -m pytest
```

Out of the box, the **plumbing** tests (agent loop, SSE routes, store, uploads, helpers)
pass, while `tests/test_loan_tools.py` and the validation-rules tests **fail** — that's your
worklist. Make them green step by step. `tests/test_loan_tools.py` is the exact contract for
each tool.

## Run it

```bash
# Backend
cd backend
cp ../.env.example ../.env        # add your ANTHROPIC_API_KEY
.venv/bin/uvicorn app.main:app --reload --port 8000    # API docs at /api/docs

# Frontend
cd frontend && npm install && npm run dev               # http://localhost:3000

# Or both via Docker
docker compose up --build
```

The app boots immediately; until you implement the tools, a pipeline run will stream the
agent's reasoning and then surface tool errors (`NotImplementedError`). As you complete each
step, the corresponding tool starts returning real results.

## Sample data

Three loan packages under `sample-data/`, surfaced as demo scenarios via
`GET /api/pipeline/scenarios`:

| Package | Expected outcome (once implemented) |
|---------|-------------------------------------|
| `acme_widgets` | Clean **approve** — strong coverage, growing revenue |
| `bravo_logistics` | **approve_with_conditions** — thin DSCR, declining revenue |
| `charlie_retail` | **Validation error path** — only 2 of 3 required years present |

## Architecture

```
React 19 Frontend  ◄──SSE──►  FastAPI Backend  ◄──tool use──►  Claude Sonnet 4.6
```

The agent loop in `backend/app/services/agent_runner.py` calls Claude, dispatches each
`tool_use` block, appends `tool_result`s, and loops until `stop_reason == "end_turn"`
(capped at 25 iterations). The result of `assess_creditworthiness` becomes the pipeline
assessment.
