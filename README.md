# Claude API Lab — Prior Authorization Review (STARTER branch)

> **You are on the `healthcare` starter branch.** The structure, tool *schemas*, agent loop,
> sample data, and tests are in place, but the tool logic, system prompt, and data schemas are
> **fill-in-the-blank**. You implement them step by step. The finished reference is on the
> **`healthcare-solution`** branch — peek if you get stuck.

Build a tool-using agent that reviews an outpatient prior-authorization request: Claude drives
a tool-use loop that parses the request, validates it, checks it against the payer's
medical-necessity policy, and recommends a determination. Built for the **Claude API Lab**
workshop (Module 2.2, healthcare variant).

Built by [Provectus](https://provectus.com/).

## What you'll implement

| Step | Where | What |
|------|-------|------|
| 4 — Schema | `backend/app/schemas/{canonical_pa_request_v1,criteria_rules,payer_policies_v1}.json` | Fill in the request shape, validation rules, and per-CPT policies (`_TODO_step_4`). |
| 5 — Prompt | `backend/app/prompts/clinical_reviewer.md` | Flesh out persona, workflow, determination categories, output contract. |
| 6 — Tool 1 | `backend/app/tools/parse_pa_request.py` | Folder → canonical `PARequest`. |
| 7 — Tool 2 | `backend/app/tools/validate_clinical_criteria.py` | Structural / eligibility validation. |
| 8 — Tool 3 | `backend/app/tools/check_payer_policy.py` | Evaluate clinical facts against the CPT policy. |
| 9 — Tool 4 | `backend/app/tools/recommend_decision.py` | The final determination. |
| 10 — Loop | `backend/app/services/agent_runner.py` | Already wired — read it to understand the loop. |

Each tool keeps its `NAME` and `DEFINITION`; only the `execute()` body is a
`NotImplementedError` TODO. The registry already lists all four.

## Your progress meter: the tests

```bash
cd backend
uv venv --python 3.12 .venv && uv pip install -e ".[dev]"
.venv/bin/python -m pytest
```

Out of the box, the **plumbing** tests (agent loop, SSE routes, store, uploads, `_common`
helpers) pass, while `tests/test_pa_tools.py` and the schema-loader tests **fail** — that's your
worklist. `tests/test_pa_tools.py` is the exact contract for each tool.

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

Three PA requests under `sample-data/`, surfaced via `GET /api/pipeline/scenarios`:

| Request | CPT | Expected outcome (once implemented) |
|---------|-----|-------------------------------------|
| `lumbar_mri` | 72148 | **approve** — meets all policy criteria |
| `knee_arthroscopy` | 29881 | **pend_for_info** — criteria unmet (short conservative tx, no PT) |
| `incomplete_request` | 70553 | **validation fails** — no primary dx, missing clinical fields |
