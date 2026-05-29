"""Tool 1: Parse a supplier feed folder into canonical product rows."""

import json
from pathlib import Path

import pandas as pd

from app.config import Settings
from app.tools._common import safe_json_serialize

NAME = "parse_supplier_feed"

DEFINITION = {
    "name": NAME,
    "description": (
        "Parse a supplier feed folder into a list of canonical product rows. The folder "
        "contains `feed.csv` (the raw supplier rows, whose column names vary by supplier) and "
        "`supplier_meta.json` (the supplier name, a `column_map` from canonical field → the "
        "supplier's column name, and a default currency). Applies the column map to normalize "
        "each row into {sku, gtin, brand, title, supplier_category, price:{amount, currency}}. "
        "Returns the products plus parse warnings. Use this as the first step."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "folder_path": {
                "type": "string",
                "description": "Path to the supplier feed folder (feed.csv + supplier_meta.json)",
            },
        },
        "required": ["folder_path"],
    },
}

_CORE_FIELDS = ["sku", "gtin", "brand", "title", "supplier_category"]


async def execute(input_data: dict, settings: Settings) -> dict:
    """Read supplier_meta.json + feed.csv and map rows to canonical products."""
    folder = Path(input_data["folder_path"])
    if not folder.exists() or not folder.is_dir():
        return {"error": f"Supplier feed folder not found: {folder}"}

    meta_path = folder / "supplier_meta.json"
    feed_path = folder / "feed.csv"
    if not meta_path.exists():
        return {"error": f"Missing supplier_meta.json in {folder}"}
    if not feed_path.exists():
        return {"error": f"Missing feed.csv in {folder}"}

    meta = json.loads(meta_path.read_text())
    column_map = meta.get("column_map", {})
    default_currency = meta.get("default_currency", "USD")
    warnings: list[str] = []

    df = pd.read_csv(feed_path, dtype=str).fillna("")

    # Warn about any mapped column that isn't actually in the feed.
    for field, col in column_map.items():
        if col not in df.columns:
            warnings.append(f"column_map field '{field}' → '{col}' not found in feed.csv")

    products = []
    price_col = column_map.get("price_amount")
    currency_col = column_map.get("price_currency")
    for idx, row in df.iterrows():
        product: dict = {}
        for field in _CORE_FIELDS:
            col = column_map.get(field)
            product[field] = str(row[col]).strip() if col and col in df.columns else ""

        amount = None
        if price_col and price_col in df.columns:
            raw = str(row[price_col]).replace("$", "").replace(",", "").strip()
            try:
                amount = float(raw) if raw else None
            except ValueError:
                amount = None
                warnings.append(f"row {idx}: unparseable price '{row[price_col]}'")
        currency = (
            str(row[currency_col]).strip()
            if currency_col and currency_col in df.columns and row[currency_col]
            else default_currency
        )
        product["price"] = {"amount": amount, "currency": currency}
        products.append(product)

    return safe_json_serialize({
        "supplier": meta.get("supplier", folder.name),
        "products": products,
        "row_count": len(products),
        "parse_warnings": warnings,
        "source_folder": folder.name,
    })
