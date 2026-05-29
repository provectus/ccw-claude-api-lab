"""Tool 4: Produce the final catalog-import report (the agent's verdict)."""

from app.config import Settings
from app.tools._common import safe_json_serialize

NAME = "generate_import_report"

_RECOMMENDATIONS = {"import_clean", "import_with_review", "hold"}

DEFINITION = {
    "name": NAME,
    "description": (
        "Produce the final catalog-import report. This is the LAST tool in the workflow — its "
        "output is the agent's verdict. You supply the structured report: an overall "
        "recommendation (import_clean / import_with_review / hold), the ready / needs_review / "
        "rejected counts, a summary, the top issues to fix, and a confidence. The tool validates "
        "the structure and returns the report. Base the counts on validate_skus (rejected) and "
        "map_to_canonical_taxonomy (needs_review), and cite the main issues in the summary."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "recommendation": {
                "type": "string",
                "enum": ["import_clean", "import_with_review", "hold"],
                "description": "Overall disposition for this supplier feed.",
            },
            "ready_count": {"type": "integer", "description": "Products ready to import as-is."},
            "needs_review_count": {"type": "integer", "description": "Products importable after human review (e.g. low-confidence category)."},
            "rejected_count": {"type": "integer", "description": "Products that failed validation and must be fixed."},
            "summary": {"type": "string", "description": "Narrative summary of feed quality and what to do next."},
            "top_issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Ranked list of the most common/important issues to fix.",
            },
            "confidence": {"type": "number", "description": "Confidence in the report, 0.0–1.0."},
        },
        "required": ["recommendation", "ready_count", "needs_review_count", "rejected_count", "summary", "confidence"],
    },
}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Validate and assemble the final import report. Deterministic — no model call."""
    recommendation = input_data.get("recommendation")
    validation_notes: list[str] = []

    if recommendation not in _RECOMMENDATIONS:
        return {"error": f"recommendation must be one of {sorted(_RECOMMENDATIONS)}, got {recommendation!r}"}

    confidence = input_data.get("confidence", 0.0)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0
    if confidence < 0 or confidence > 1:
        validation_notes.append(f"confidence {confidence} clamped to [0, 1]")
        confidence = max(0.0, min(1.0, confidence))

    ready = int(input_data.get("ready_count", 0) or 0)
    review = int(input_data.get("needs_review_count", 0) or 0)
    rejected = int(input_data.get("rejected_count", 0) or 0)

    if recommendation == "import_clean" and (review or rejected):
        validation_notes.append(
            "import_clean recommended despite non-zero needs_review/rejected counts"
        )

    return safe_json_serialize({
        "recommendation": recommendation,
        "ready_count": ready,
        "needs_review_count": review,
        "rejected_count": rejected,
        "total_evaluated": ready + review + rejected,
        "summary": input_data.get("summary", ""),
        "top_issues": input_data.get("top_issues") or [],
        "confidence": round(confidence, 2),
        "validation_notes": validation_notes,
    })
