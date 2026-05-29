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
    """Validate and assemble the final determination. Deterministic — no model call."""
    decision = input_data.get("decision")
    validation_notes: list[str] = []

    if decision not in _DECISIONS:
        return {"error": f"decision must be one of {sorted(_DECISIONS)}, got {decision!r}"}

    confidence = input_data.get("confidence", 0.0)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0
    if confidence < 0 or confidence > 1:
        validation_notes.append(f"confidence {confidence} clamped to [0, 1]")
        confidence = max(0.0, min(1.0, confidence))

    required_docs = input_data.get("required_documentation") or []
    if decision == "pend_for_info" and not required_docs:
        validation_notes.append("pend_for_info returned with no required_documentation listed")

    validity = input_data.get("authorization_validity_days", 0)
    if decision != "approve" and validity:
        validation_notes.append("authorization_validity_days is only meaningful for an approval")

    return safe_json_serialize({
        "decision": decision,
        "rationale": input_data.get("rationale", ""),
        "required_documentation": required_docs,
        "authorization_validity_days": validity if decision == "approve" else 0,
        "confidence": round(confidence, 2),
        "validation_notes": validation_notes,
    })
