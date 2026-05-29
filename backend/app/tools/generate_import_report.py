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
    """Validate and assemble the final import report. Deterministic — no model call.

    TODO (Step 9 — Build Tool 4):
      This is the agent's FINAL tool — its return becomes the pipeline assessment.
      1. Reject an out-of-enum `recommendation` (not in _RECOMMENDATIONS) with {"error": ...}.
      2. Coerce + clamp `confidence` into [0, 1], noting any clamp.
      3. Read ready/needs_review/rejected counts (ints); flag an `import_clean`
         recommendation that has non-zero review/rejected counts.
      4. Return safe_json_serialize({recommendation, ready_count, needs_review_count,
         rejected_count, total_evaluated, summary, top_issues, confidence, validation_notes}).

    See tests/test_catalog_tools.py::TestGenerateImportReport for the contract.
    """
    raise NotImplementedError("TODO (Step 9): implement generate_import_report")
