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
    """Apply catalog_rules.json to each product."""
    products = input_data.get("products") or []
    rules = load_catalog_rules()
    issues = []

    for idx, p in enumerate(products):
        errors: list[str] = []

        # Required fields present (price handled separately).
        for field in rules["required_fields"]:
            if field == "price":
                continue
            if not p.get(field):
                errors.append(f"missing {field}")

        sku = str(p.get("sku", ""))
        if sku and not re.match(rules["sku"]["pattern"], sku):
            errors.append(f"sku '{sku}' fails format rule")

        gtin = str(p.get("gtin", ""))
        if rules["gtin"]["require_valid_check_digit"] and not gtin_check_digit_valid(gtin):
            errors.append(f"gtin '{gtin}' is not a valid 13-digit GTIN")

        price = p.get("price") or {}
        amount = price.get("amount")
        p_rule = rules["price"]
        if amount is None:
            errors.append("price.amount is missing")
        elif not (p_rule["min"] <= amount <= p_rule["max"]):
            errors.append(f"price.amount {amount} outside [{p_rule['min']}, {p_rule['max']}]")
        if price.get("currency") not in p_rule["allowed_currencies"]:
            errors.append(f"price.currency '{price.get('currency')}' not supported")

        if errors:
            issues.append({"index": idx, "sku": sku or None, "errors": errors})

    invalid = len(issues)
    total = len(products)
    return safe_json_serialize({
        "total": total,
        "valid_count": total - invalid,
        "invalid_count": invalid,
        "issues": issues,
        "all_valid": invalid == 0,
    })
