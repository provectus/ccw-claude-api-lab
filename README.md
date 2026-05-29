# Claude API Lab — Commercial Loan Underwriting Agent

Reference implementation for the **Claude API Lab** workshop (Module 2.2). An agentic
demo that underwrites a small-business loan application end-to-end: Claude drives a
tool-use loop that parses a borrower package, validates it against credit policy,
computes credit ratios, and produces a structured creditworthiness assessment — no
hardcoded step sequence, the model decides which tool to call next.

> This is the **`finance-solution`** branch — the finished reference / answer key for the
> **`finance`** starter branch (whose `execute()` bodies, prompt, and schemas are stubbed
> TODOs). The workshop content lives in the
> [`cc-workshop`](https://github.com/provectus) platform.
>
> *(The `main` branch currently mirrors this loan-underwriting reference; longer-term it is
> slated to become a distinct domain — see the project plan.)*

Built by [Provectus](https://provectus.com/).

## Architecture

```
React 19 Frontend  ◄──SSE──►  FastAPI Backend  ◄──tool use──►  Claude Sonnet 4.6
```

| Layer | Stack |
|-------|-------|
| **Frontend** | React 19, TypeScript, Vite, MUI, Zustand (SSE streaming UI) |
| **Backend** | FastAPI, Pydantic, SSE (sse-starlette), pandas |
| **AI** | Claude Sonnet 4.6 via the Anthropic Messages API with tool use |

The agent loop lives in `backend/app/services/agent_runner.py`: call Claude → dispatch
each `tool_use` block → append `tool_result`s → loop until `stop_reason == "end_turn"`
(capped at 25 iterations).

## The four tools

Registered in `backend/app/tools/registry.py` (explicit list — add your module there):

1. **`parse_loan_package`** — folder (`profile.json` + `financials.csv`) → canonical `LoanApplication`.
2. **`validate_loan_application`** — applies `schemas/validation_rules.json` → `{valid, errors, warnings}`.
3. **`compute_credit_ratios`** — DSCR, current ratio, debt-to-equity, gross-margin trend, 3-yr revenue CAGR, LTV.
4. **`assess_creditworthiness`** — the final verdict (recommendation, pricing, risks, confidence, reasoning). Its output becomes the pipeline assessment.

System prompt: `backend/app/prompts/credit_analyst.md`. Canonical schema:
`backend/app/schemas/canonical_loan_application_v1.json`.

## Quick start

### Prerequisites
- Python 3.12+ and Node 20+
- An Anthropic API key

### Backend
```bash
cd backend
uv venv --python 3.12 .venv && source .venv/bin/activate   # or: python3.12 -m venv .venv
uv pip install -e ".[dev]"                                  # or: pip install -e ".[dev]"
cp ../.env.example ../.env       # add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```
API docs at http://localhost:8000/api/docs.

### Frontend
```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

### Docker (both services)
```bash
cp .env.example .env   # add ANTHROPIC_API_KEY
docker compose up --build
```

## Sample data

Three loan packages under `sample-data/`, surfaced as demo scenarios via
`GET /api/pipeline/scenarios`:

| Package | Expected outcome |
|---------|------------------|
| `acme_widgets` | Clean **approve** — DSCR ~2.8x, LTV ~68%, growing revenue |
| `bravo_logistics` | **approve_with_conditions** — DSCR ~1.19x, declining revenue, elevated leverage |
| `charlie_retail` | **Validation error path** — only 2 of 3 required years present |

## Tests

```bash
cd backend
.venv/bin/python -m pytest                    # unit + route tests
.venv/bin/python -m pytest -m integration     # full agentic loop (needs ANTHROPIC_API_KEY)
```

## Status notes

- The **backend** domain layer (tools, schema, prompt, agent loop, sample data, tests) is the
  workshop's teaching core and is fully implemented and tested here.
- The **frontend** streams the agent's reasoning and tool calls generically; its
  domain-specific visualization components are inherited from the upstream finance demo
  and are not yet retailored to loan underwriting (tracked as follow-up; not on the core path).
