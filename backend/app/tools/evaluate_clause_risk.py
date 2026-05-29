"""Tool 3: Flag contract risk from the customer's perspective (deterministic)."""

from app.config import Settings
from app.tools._common import load_risk_rules, safe_json_serialize

NAME = "evaluate_clause_risk"

DEFINITION = {
    "name": NAME,
    "description": (
        "Evaluate a canonical contract for risk from the CUSTOMER's perspective and return a "
        "list of flags with severities (low / medium / high): the auto-renewal trap (auto-renews "
        "with a long notice window), a missing or weak liability cap, one-sided indemnification, "
        "no customer right to terminate for convenience, and any missing required clauses. "
        "Returns the flags plus an overall risk rating. Run after extract_clauses."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "contract": {"type": "object", "description": "Canonical contract from extract_clauses"},
        },
        "required": ["contract"],
    },
}

_RANK = {"low": 1, "medium": 2, "high": 3}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Apply the deterministic risk rules to the canonical contract.

    TODO (Step 8 — Build Tool 3):
      Reviewing from the CUSTOMER's perspective, build a list of flags
      {clause, severity, message} using `load_risk_rules()`:
        - auto_renewal present with notice_days ≥ threshold → high (the trap); else medium.
        - liability_cap not present → high; present but excludes_consequential → low note.
        - indemnification present but not mutual → medium; absent → medium.
        - termination without customer_for_convenience → medium.
        - any `required_clauses` not present (check raw_clauses / the field) → medium.
      Then return safe_json_serialize({flags, high_count, medium_count, low_count,
      overall_risk}) where overall_risk is the highest severity present (use _RANK).

    See tests/test_legal_tools.py::TestEvaluateClauseRisk for the contract.
    """
    raise NotImplementedError("TODO (Step 8): implement evaluate_clause_risk")
