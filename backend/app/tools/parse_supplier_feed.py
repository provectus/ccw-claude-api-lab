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
    """Read supplier_meta.json + feed.csv and map rows to canonical products.

    TODO (Step 6 — Build Tool 1):
      1. Resolve `input_data["folder_path"]`; confirm supplier_meta.json + feed.csv exist.
      2. Load supplier_meta.json (column_map, supplier, default_currency); read feed.csv
         with `pd.read_csv(feed_path, dtype=str).fillna("")`.
      3. For each row, apply `column_map` (canonical field → supplier column) to build a
         product with `_CORE_FIELDS` plus a `price` {amount: float|None, currency}.
         Warn for mapped columns missing from the feed and unparseable prices.
      4. Return safe_json_serialize({supplier, products, row_count, parse_warnings,
         source_folder}).

    See tests/test_catalog_tools.py::TestParseSupplierFeed for the contract; the reference
    implementation is on the `retail-solution` branch.
    """
    raise NotImplementedError("TODO (Step 6): implement parse_supplier_feed")
