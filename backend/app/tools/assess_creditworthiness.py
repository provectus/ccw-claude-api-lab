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
    """Validate and assemble the final assessment. Deterministic — no model call."""
    recommendation = input_data.get("recommendation")
    validation_notes: list[str] = []

    if recommendation not in _RECOMMENDATIONS:
        return {
            "error": (
                f"recommendation must be one of {sorted(_RECOMMENDATIONS)}, "
                f"got {recommendation!r}"
            )
        }

    # Clamp confidence into [0, 1] rather than hard-failing.
    confidence = input_data.get("confidence", 0.0)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0
    if confidence < 0 or confidence > 1:
        validation_notes.append(f"confidence {confidence} clamped to [0, 1]")
        confidence = max(0.0, min(1.0, confidence))

    term = input_data.get("suggested_term_months")
    if term not in _ALLOWED_TERMS:
        validation_notes.append(
            f"suggested_term_months {term} is non-standard (expected one of {sorted(_ALLOWED_TERMS)})"
        )

    conditions = input_data.get("conditions") or []
    if recommendation == "approve_with_conditions" and not conditions:
        validation_notes.append(
            "approve_with_conditions returned with no conditions listed"
        )

    return safe_json_serialize({
        "recommendation": recommendation,
        "suggested_rate_bps": input_data.get("suggested_rate_bps"),
        "suggested_term_months": term,
        "top_risks": input_data.get("top_risks") or [],
        "conditions": conditions,
        "confidence": round(confidence, 2),
        "reasoning": input_data.get("reasoning", ""),
        "validation_notes": validation_notes,
    })
