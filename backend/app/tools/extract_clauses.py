"""Tool 2: Extract canonical clauses from contract text (deterministic)."""

import re

from app.config import Settings
from app.tools._common import (
    extract_section,
    load_clause_patterns,
    safe_json_serialize,
)

NAME = "extract_clauses"

DEFINITION = {
    "name": NAME,
    "description": (
        "Extract the key clauses from contract text into the canonical contract structure: "
        "parties, term, auto-renewal (and its notice window), payment terms, limitation of "
        "liability, indemnification, IP assignment, termination, and governing law. Returns the "
        "structured contract plus which clauses were found vs. missing. Run after parse_contract_pdf."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Full contract text from parse_contract_pdf"},
        },
        "required": ["text"],
    },
}


def _contains(text: str | None, pattern: str) -> bool:
    return bool(text) and re.search(pattern, text, re.IGNORECASE) is not None


async def execute(input_data: dict, settings: Settings) -> dict:
    """Heuristically extract canonical clauses from the contract text.

    TODO (Step 7 — Build Tool 2):
      1. Read `input_data["text"]`; return {"error": ...} if empty.
      2. Load clause heading patterns with `load_clause_patterns()` and grab each clause's
         section with `extract_section(text, keywords)` (helper in _common).
      3. Derive the canonical fields: parties, term_months, auto_renewal {present, notice_days},
         payment_terms, liability_cap {present, basis, excludes_consequential}, indemnification
         {present, mutual}, ip_assignment, termination {customer_for_convenience, notice_days},
         governing_law. Use regex over the extracted sections.
      4. Return safe_json_serialize({contract, clauses_found, missing_clauses}).

    See tests/test_legal_tools.py::TestExtractClauses for the contract.
    """
    text = input_data.get("text") or ""
    if not text.strip():
        return {"error": "No contract text provided"}

    raise NotImplementedError("TODO (Step 7): implement extract_clauses")
