"""Tool 4: Produce the final creditworthiness assessment (the agent's verdict)."""

from app.config import Settings
from app.tools._common import safe_json_serialize

NAME = "assess_creditworthiness"

_RECOMMENDATIONS = {"approve", "approve_with_conditions", "decline"}
_ALLOWED_TERMS = {12, 24, 36, 48, 60, 84, 120}

DEFINITION = {
    "name": NAME,
    "description": (
        "Produce the final creditworthiness assessment for the loan application. This is the "
        "LAST tool in the workflow — its output is the agent's verdict. You supply the full "
        "structured decision: recommendation, indicative pricing and term, top risks, "
        "confidence, and reasoning that cites the computed ratios. The tool validates the "
        "structure (enum values, confidence range, allowed term) and returns the assessment. "
        "Always cite specific ratio values (DSCR, current ratio, debt-to-equity, LTV) in your reasoning."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "recommendation": {
                "type": "string",
                "enum": ["approve", "approve_with_conditions", "decline"],
                "description": "Underwriting decision.",
            },
            "suggested_rate_bps": {
                "type": "integer",
                "description": "Indicative all-in rate in basis points (e.g. 850 = 8.50%).",
            },
            "suggested_term_months": {
                "type": "integer",
                "description": "Recommended term in months (one of 12, 24, 36, 48, 60, 84, 120).",
            },
            "top_risks": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Ranked list of the key credit risks.",
            },
            "conditions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Conditions of approval (required when recommendation is approve_with_conditions).",
            },
            "confidence": {
                "type": "number",
                "description": "Confidence in the recommendation, 0.0–1.0.",
            },
            "reasoning": {
                "type": "string",
                "description": "Narrative justification citing specific ratio values.",
            },
        },
        "required": [
            "recommendation",
            "suggested_rate_bps",
            "suggested_term_months",
            "top_risks",
            "confidence",
            "reasoning",
        ],
    },
}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Validate and assemble the final assessment. Deterministic — no model call.

    TODO (Step 9 — Build Tool 4):
      This is the agent's FINAL tool — its return becomes the pipeline assessment.
      1. Reject an out-of-enum `recommendation` with {"error": ...}.
      2. Coerce + clamp `confidence` into [0, 1], noting any clamp.
      3. Flag a non-standard `suggested_term_months` (not in _ALLOWED_TERMS) and an
         `approve_with_conditions` result that lists no `conditions`.
      4. Return safe_json_serialize({recommendation, suggested_rate_bps,
         suggested_term_months, top_risks, conditions, confidence, reasoning,
         validation_notes}).

    See tests/test_loan_tools.py::TestAssessCreditworthiness for the contract.
    """
    raise NotImplementedError("TODO (Step 9): implement assess_creditworthiness")
