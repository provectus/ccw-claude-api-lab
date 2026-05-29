"""Tool 4: Produce the final prior-authorization determination (the agent's verdict)."""

from app.config import Settings
from app.tools._common import safe_json_serialize

NAME = "recommend_decision"

_DECISIONS = {"approve", "deny", "pend_for_info"}

DEFINITION = {
    "name": NAME,
    "description": (
        "Produce the final prior-authorization determination. This is the LAST tool in the "
        "workflow — its output is the agent's verdict. You supply the structured decision: "
        "approve / deny / pend_for_info, a rationale citing the policy criteria, any required "
        "documentation (when pending), an authorization validity period, and a confidence. The "
        "tool validates the structure and returns the determination. Cite the specific unmet "
        "criteria from check_payer_policy in your rationale."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "decision": {
                "type": "string",
                "enum": ["approve", "deny", "pend_for_info"],
                "description": "The determination.",
            },
            "rationale": {
                "type": "string",
                "description": "Narrative citing the policy criteria and the documented clinical facts.",
            },
            "required_documentation": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Documentation the provider must submit (required when decision is pend_for_info).",
            },
            "authorization_validity_days": {
                "type": "integer",
                "description": "Validity window for an approval (e.g. 90). Use 0 for deny/pend.",
            },
            "confidence": {
                "type": "number",
                "description": "Confidence in the determination, 0.0–1.0.",
            },
        },
        "required": ["decision", "rationale", "confidence"],
    },
}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Validate and assemble the final determination. Deterministic — no model call.

    TODO (Step 9 — Build Tool 4):
      This is the agent's FINAL tool — its return becomes the pipeline assessment.
      1. Reject an out-of-enum `decision` (not in _DECISIONS) with {"error": ...}.
      2. Coerce + clamp `confidence` into [0, 1], noting any clamp.
      3. Flag a `pend_for_info` with no `required_documentation`; force
         `authorization_validity_days` to 0 unless the decision is `approve`.
      4. Return safe_json_serialize({decision, rationale, required_documentation,
         authorization_validity_days, confidence, validation_notes}).

    See tests/test_pa_tools.py::TestRecommendDecision for the contract.
    """
    raise NotImplementedError("TODO (Step 9): implement recommend_decision")
