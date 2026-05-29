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
    """Fuzzy-match supplier_category → canonical taxonomy path for each product."""
    products = input_data.get("products") or []
    taxonomy = load_taxonomy()
    paths = taxonomy["paths"]
    confident = taxonomy["confident_threshold"]
    review = taxonomy["review_threshold"]

    results = []
    mapped = needs_review = unmapped = 0
    for idx, p in enumerate(products):
        raw = str(p.get("supplier_category", ""))
        best, score = best_taxonomy_match(raw, paths)
        if score >= confident:
            status = "mapped"
            mapped += 1
        elif score >= review:
            status = "needs_review"
            needs_review += 1
        else:
            status = "unmapped"
            unmapped += 1
            best = None
        results.append({
            "index": idx,
            "sku": p.get("sku") or None,
            "supplier_category": raw,
            "canonical_category": best,
            "score": round(score, 1),
            "status": status,
        })

    return safe_json_serialize({
        "results": results,
        "mapped_count": mapped,
        "needs_review_count": needs_review,
        "unmapped_count": unmapped,
        "total": len(products),
    })
