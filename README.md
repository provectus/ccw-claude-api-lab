# Claude API Lab — SaaS Contract Review (STARTER branch)

> **You are on the `legal` starter branch.** The structure, tool *schemas*, agent loop, sample
> data, and tests are in place, but the tool logic, system prompt, and data schemas are
> **fill-in-the-blank**. You implement them step by step. The finished reference is on the
> **`legal-solution`** branch — peek if you get stuck.

Build a tool-using agent that reviews an inbound SaaS Master Service Agreement on behalf of the
customer: Claude drives a tool-use loop that reads the contract PDF, extracts the key clauses,
flags the risks, and writes a review memo. Built for the **Claude API Lab** workshop (Module 2.2,
legal variant).

Built by [Provectus](https://provectus.com/).

## What you'll implement

| Step | Where | What |
|------|-------|------|
| 4 — Schema | `backend/app/schemas/{canonical_contract_v1,clause_patterns,risk_rules}.json` | Fill in the contract shape, clause heading patterns, and risk thresholds (`_TODO_step_4`). |
| 5 — Prompt | `backend/app/prompts/contract_reviewer.md` | Flesh out persona, workflow, what to watch for, output contract. |
| 6 — Tool 1 | `backend/app/tools/parse_contract_pdf.py` | PDF → text via Claude's **native PDF support** (the `_extract_with_claude` helper shows the `document` block). |
| 7 — Tool 2 | `backend/app/tools/extract_clauses.py` | Text → canonical clauses (deterministic heading/keyword parsing). |
| 8 — Tool 3 | `backend/app/tools/evaluate_clause_risk.py` | Flag customer-side risk. |
| 9 — Tool 4 | `backend/app/tools/generate_review_memo.py` | The final review memo. |
| 10 — Loop | `backend/app/services/agent_runner.py` | Already wired — read it to understand the loop. |

Each tool keeps its `NAME` and `DEFINITION`; only the `execute()` body is a
`NotImplementedError` TODO. The registry already lists all four. `parse_contract_pdf` ships the
`_extract_with_claude` / `_extract_with_docling` / `_extract_with_llamaparse` helpers — your job
in Step 6 is to wire `execute()` to dispatch to them.

## Native PDF + ZDR (Step 6 context)

The default `method="claude"` sends the PDF to Claude as a `document` content block
([native PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support)) —
text + per-page vision. The feature is **ZDR-eligible**, but Zero Data Retention is an org-level
arrangement, not automatic. Optional local/cloud fallbacks (Docling, LlamaParse) are available
via `method=` and the `[parsers]` extra (`uv pip install -e ".[dev,parsers]"`).

## Your progress meter: the tests

```bash
cd backend
uv venv --python 3.12 .venv && uv pip install -e ".[dev]"
.venv/bin/python -m pytest
```

Out of the box, the **plumbing** tests pass, while `tests/test_legal_tools.py` and the
schema-loader tests **fail** — that's your worklist. `tests/test_legal_tools.py` is the exact
contract for each tool (the `parse_contract_pdf` test mocks the Anthropic client, so it runs offline).

## Run it

```bash
cd backend
cp ../.env.example ../.env        # add ANTHROPIC_API_KEY
.venv/bin/uvicorn app.main:app --reload --port 8000
cd ../frontend && npm install && npm run dev      # http://localhost:3000
# or both: docker compose up --build
```

## Sample data

Two SaaS MSAs (PDFs) under `sample-data/`, surfaced via `GET /api/pipeline/scenarios`:

| Contract | Expected outcome (once implemented) |
|----------|-------------------------------------|
| `acme_saas_msa.pdf` | **approve** — market-standard terms |
| `vendorco_msa.pdf` | **negotiate** — 90-day auto-renewal trap, one-sided indemnity, no customer termination |
