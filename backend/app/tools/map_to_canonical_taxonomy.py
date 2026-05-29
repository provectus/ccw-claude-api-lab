"""Tool 3: Fuzzy-map each product's supplier category to the canonical taxonomy."""

from app.config import Settings
from app.tools._common import best_taxonomy_match, load_taxonomy, safe_json_serialize

NAME = "map_to_canonical_taxonomy"

DEFINITION = {
    "name": NAME,
    "description": (
        "Map each product's free-text supplier category to the closest canonical taxonomy path "
        "using fuzzy string matching. Each result gets a best-match path, a 0–100 score, and a "
        "status: 'mapped' (score ≥ confident threshold), 'needs_review' (≥ review threshold), or "
        "'unmapped' (below). Returns per-row results plus bucket counts. Run after validate_skus."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "products": {
                "type": "array",
                "description": "Canonical product rows (each with a supplier_category)",
                "items": {"type": "object"},
            },
        },
        "required": ["products"],
    },
}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Fuzzy-match supplier_category → canonical taxonomy path for each product.

    TODO (Step 8 — Build Tool 3):
      1. Load the taxonomy: `tax = load_taxonomy()` → `paths`, `confident_threshold`,
         `review_threshold`.
      2. For each product, fuzzy-match its `supplier_category` with
         `best_taxonomy_match(raw, paths)` → (best_path, score). Bucket by status:
         score ≥ confident → 'mapped'; ≥ review → 'needs_review'; else 'unmapped'
         (set canonical_category to None when unmapped).
      3. Return safe_json_serialize({results[{index, sku, supplier_category,
         canonical_category, score, status}], mapped_count, needs_review_count,
         unmapped_count, total}).

    See tests/test_catalog_tools.py::TestMapToCanonicalTaxonomy for the contract.
    """
    raise NotImplementedError("TODO (Step 8): implement map_to_canonical_taxonomy")
