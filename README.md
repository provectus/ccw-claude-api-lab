# Claude API Lab — Prior Authorization Review Agent

Reference implementation for the **Claude API Lab** workshop (Module 2.2, healthcare
variant). An agentic demo that reviews an outpatient prior-authorization (PA) request
end-to-end: Claude drives a tool-use loop that parses the request, validates it, checks it
against the payer's medical-necessity policy, and recommends a determination — no hardcoded
step sequence, the model decides which tool to call next.

> This is the **`healthcare-solution`** branch — the finished reference / answer key. The
> **`healthcare`** branch is the fill-in-the-blank starter learners clone; its tool bodies,
> system prompt, and schemas are stubbed TODOs. The workshop content lives in the
> [`cc-workshop`](https://github.com/provectus) platform.

Built by [Provectus](https://provectus.com/).

## Architecture

```
React 19 Frontend  ◄──SSE──►  FastAPI Backend  ◄──tool use──►  Claude Sonnet 4.6
```

The agent loop in `backend/app/services/agent_runner.py` calls Claude, dispatches each
`tool_use` block, appends `tool_result`s, and loops until `stop_reason == "end_turn"`
(capped at 25 iterations). The result of `recommend_decision` becomes the pipeline assessment.

## The four tools

Registered in `backend/app/tools/registry.py`:

1. **`parse_pa_request`** — folder (`request.json` + optional `clinical_notes.txt`) → canonical `PARequest`.
2. **`validate_clinical_criteria`** — structural/eligibility checks (CPT/ICD-10/NPI formats, one primary dx, covered plan, place of service, required clinical fields) → `{valid, errors, warnings}`.
3. **`check_payer_policy`** — evaluates the documented clinical facts against the per-CPT medical-necessity policy → per-criterion breakdown + `meets_policy`.
4. **`recommend_decision`** — the final determination (approve / deny / pend_for_info) with rationale, required documentation, and validity period. Its output becomes the pipeline assessment.

System prompt: `backend/app/prompts/clinical_reviewer.md`. Schemas:
`canonical_pa_request_v1.json`, `criteria_rules.json`, `payer_policies_v1.json`.

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

Three PA requests under `sample-data/`, surfaced via `GET /api/pipeline/scenarios`:

| Request | CPT | Expected outcome |
|---------|-----|------------------|
| `lumbar_mri` | 72148 | **approve** — meets all 3 policy criteria (8 wks conservative tx, PT, prior imaging) |
| `knee_arthroscopy` | 29881 | **pend_for_info** — meets 2 of 4 (only 3 wks conservative tx, no PT documented) |
| `incomplete_request` | 70553 | **validation fails** — no primary diagnosis, missing clinical fields → pend |

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
  not retailored to PA review (tracked as follow-up; not on the core path).
