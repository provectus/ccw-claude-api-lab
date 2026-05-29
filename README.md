# Claude API Lab — SaaS Contract Review Agent

Reference implementation for the **Claude API Lab** workshop (Module 2.2, legal variant). An
agentic demo that reviews an inbound SaaS Master Service Agreement on behalf of the customer:
Claude drives a tool-use loop that reads the contract PDF, extracts the key clauses, flags the
risks, and writes a review memo — no hardcoded step sequence, the model decides which tool to
call next.

> This is the **`legal-solution`** branch — the finished reference / answer key for the
> **`legal`** starter branch (whose tool bodies, prompt, and schemas are stubbed TODOs). The
> workshop content lives in the [`cc-workshop`](https://github.com/provectus) platform.

Built by [Provectus](https://provectus.com/).

## Architecture

```
React 19 Frontend  ◄──SSE──►  FastAPI Backend  ◄──tool use──►  Claude Sonnet 4.6
```

The agent loop in `backend/app/services/agent_runner.py` calls Claude, dispatches each
`tool_use` block, appends `tool_result`s, and loops until `stop_reason == "end_turn"`
(capped at 25 iterations). The result of `generate_review_memo` becomes the pipeline assessment.

## The four tools

Registered in `backend/app/tools/registry.py`:

1. **`parse_contract_pdf`** — PDF → text. Default uses **Claude's native PDF support** (Messages API `document` block — text + per-page vision, [ZDR-eligible](https://platform.claude.com/docs/en/build-with-claude/pdf-support)). Optional `method="docling"` (local) or `method="llamaparse"` (cloud) fallbacks.
2. **`extract_clauses`** — text → canonical contract (parties, term, auto-renewal, liability cap, indemnification, IP, termination, governing law) via deterministic heading/keyword parsing.
3. **`evaluate_clause_risk`** — contract → risk flags from the customer's perspective (auto-renewal traps, weak/missing liability cap, one-sided indemnity, no customer termination, missing clauses).
4. **`generate_review_memo`** — the final memo (approve / negotiate / reject) with redlines. Its output becomes the pipeline assessment.

System prompt: `backend/app/prompts/contract_reviewer.md`. Schemas:
`canonical_contract_v1.json`, `clause_patterns.json`, `risk_rules.json`.

### A note on native PDF + ZDR

`parse_contract_pdf` sends the PDF to Claude as a `document` block. This feature is
**ZDR-eligible** — but Zero Data Retention is an **org-level arrangement**, not automatic; a
plain API key is not ZDR. Limits: 32 MB / request, ~100 pages on 200k-context models (contracts
are far smaller). The optional Docling fallback runs locally (ZDR-safe by construction);
LlamaParse is a cloud service. Both are opt-in extras (`uv pip install -e ".[parsers]"`).

## Quick start

### Backend (Python 3.12)
```bash
cd backend
uv venv --python 3.12 .venv && source .venv/bin/activate   # or python3.12 -m venv .venv
uv pip install -e ".[dev]"          # add ".[dev,parsers]" to enable the optional parsers
cp ../.env.example ../.env          # add ANTHROPIC_API_KEY
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

Two SaaS MSAs (as PDFs) under `sample-data/`, surfaced via `GET /api/pipeline/scenarios`
(the `.txt` sources are kept alongside for transparency):

| Contract | Expected outcome |
|----------|------------------|
| `acme_saas_msa.pdf` | **approve** — market-standard: mutual indemnity, fees-based cap, customer termination |
| `vendorco_msa.pdf` | **negotiate** — auto-renews on 90-day notice (trap), one-sided indemnity, no customer termination, no confidentiality clause |

## Tests

```bash
cd backend
.venv/bin/python -m pytest                    # unit + route tests (parse_contract_pdf's Claude call is mocked)
.venv/bin/python -m pytest -m integration     # full agentic loop (needs ANTHROPIC_API_KEY)
```

## Status notes

- The **backend** domain layer (tools, schemas, prompt, agent loop, sample data, tests) is the
  workshop's teaching core and is fully implemented and tested here.
- `parse_contract_pdf` is the one model-calling tool (native PDF); its unit test mocks the
  Anthropic client, so the suite stays offline. The other three tools are deterministic.
- The **frontend** streams the agent's reasoning and tool calls generically; its
  domain-specific visualization components are inherited from the upstream finance demo and are
  not retailored to contract review (tracked as follow-up; not on the core path).
