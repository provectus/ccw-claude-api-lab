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
    """Validate and assemble the final review memo. Deterministic — no model call."""
    recommendation = input_data.get("recommendation")
    validation_notes: list[str] = []

    if recommendation not in _RECOMMENDATIONS:
        return {"error": f"recommendation must be one of {sorted(_RECOMMENDATIONS)}, got {recommendation!r}"}

    overall_risk = input_data.get("overall_risk")
    if overall_risk not in _RISK_LEVELS:
        validation_notes.append(f"overall_risk {overall_risk!r} is not one of {sorted(_RISK_LEVELS)}")

    confidence = input_data.get("confidence", 0.0)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0
    if confidence < 0 or confidence > 1:
        validation_notes.append(f"confidence {confidence} clamped to [0, 1]")
        confidence = max(0.0, min(1.0, confidence))

    redlines = input_data.get("recommended_redlines") or []
    if recommendation in ("negotiate", "reject") and not redlines:
        validation_notes.append(f"{recommendation} returned with no recommended_redlines")

    if overall_risk == "high" and recommendation == "approve":
        validation_notes.append("high overall_risk with an 'approve' recommendation — reconsider")

    return safe_json_serialize({
        "recommendation": recommendation,
        "overall_risk": overall_risk,
        "summary": input_data.get("summary", ""),
        "flagged_clauses": input_data.get("flagged_clauses") or [],
        "recommended_redlines": redlines,
        "confidence": round(confidence, 2),
        "validation_notes": validation_notes,
    })
