"""Tool 4: Produce the final contract review memo (the agent's verdict)."""

from app.config import Settings
from app.tools._common import safe_json_serialize

NAME = "generate_review_memo"

_RECOMMENDATIONS = {"approve", "negotiate", "reject"}
_RISK_LEVELS = {"low", "medium", "high"}

DEFINITION = {
    "name": NAME,
    "description": (
        "Produce the final contract review memo. This is the LAST tool in the workflow — its "
        "output is the agent's verdict. You supply the structured memo: an overall recommendation "
        "(approve / negotiate / reject), an overall risk level, an executive summary, the flagged "
        "clauses (carried from evaluate_clause_risk), the redlines you'd request, and a confidence. "
        "The tool validates the structure and returns the memo. Cite the specific risk flags in your summary."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "recommendation": {
                "type": "string",
                "enum": ["approve", "negotiate", "reject"],
                "description": "Overall recommendation.",
            },
            "overall_risk": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Overall risk level.",
            },
            "summary": {"type": "string", "description": "Executive summary citing the key risks."},
            "flagged_clauses": {
                "type": "array",
                "items": {"type": "object"},
                "description": "The risk flags from evaluate_clause_risk (clause/severity/message).",
            },
            "recommended_redlines": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific changes to request before signing.",
            },
            "confidence": {"type": "number", "description": "Confidence in the review, 0.0–1.0."},
        },
        "required": ["recommendation", "overall_risk", "summary", "confidence"],
    },
}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Validate and assemble the final review memo. Deterministic — no model call.

    TODO (Step 9 — Build Tool 4):
      This is the agent's FINAL tool — its return becomes the pipeline assessment.
      1. Reject an out-of-enum `recommendation` (not in _RECOMMENDATIONS) with {"error": ...}.
      2. Note an out-of-enum `overall_risk` (not in _RISK_LEVELS) in validation_notes.
      3. Coerce + clamp `confidence` into [0, 1], noting any clamp.
      4. Flag a negotiate/reject with no `recommended_redlines`, and a high-risk `approve`.
      5. Return safe_json_serialize({recommendation, overall_risk, summary, flagged_clauses,
         recommended_redlines, confidence, validation_notes}).

    See tests/test_legal_tools.py::TestGenerateReviewMemo for the contract.
    """
    raise NotImplementedError("TODO (Step 9): implement generate_review_memo")
