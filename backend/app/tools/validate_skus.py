"""Tool 2: Validate each canonical product against the catalog rules."""

import re

from app.config import Settings
from app.tools._common import gtin_check_digit_valid, load_catalog_rules, safe_json_serialize

NAME = "validate_skus"

DEFINITION = {
    "name": NAME,
    "description": (
        "Validate each parsed product against the catalog rules: SKU format, a 13-digit GTIN "
        "with a valid mod-10 check digit, a positive in-range price in a supported currency, and "
        "all required fields present. Returns per-row issues plus valid/invalid counts. A row "
        "with any error is rejected from a clean import. Run after parse_supplier_feed."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "products": {
                "type": "array",
                "description": "Canonical product rows from parse_supplier_feed",
                "items": {"type": "object"},
            },
        },
        "required": ["products"],
    },
}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Apply catalog_rules.json to each product.

    TODO (Step 7 — Build Tool 2):
      1. Load the rules: `rules = load_catalog_rules()`.
      2. For each product, collect errors: missing required fields, SKU failing the
         format regex, GTIN failing `gtin_check_digit_valid()` (the helper is imported),
         missing/out-of-range price amount, unsupported currency.
      3. Collect per-row issues as {index, sku, errors} for any product with errors.
      4. Return safe_json_serialize({total, valid_count, invalid_count, issues, all_valid}).

    See tests/test_catalog_tools.py::TestValidateSkus for the contract.
    """
    raise NotImplementedError("TODO (Step 7): implement validate_skus")
