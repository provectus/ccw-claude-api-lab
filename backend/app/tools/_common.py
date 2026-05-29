"""Shared utilities for product-catalog normalization tool implementations."""

import json
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

_catalog_rules: dict | None = None
_taxonomy: dict | None = None
_canonical_schema: dict | None = None


def load_catalog_rules() -> dict:
    """Load and cache the SKU/GTIN/price validation rules."""
    global _catalog_rules
    if _catalog_rules is None:
        with open(_SCHEMA_DIR / "catalog_rules.json") as f:
            _catalog_rules = json.load(f)
    return _catalog_rules


def load_taxonomy() -> dict:
    """Load and cache the canonical category taxonomy."""
    global _taxonomy
    if _taxonomy is None:
        with open(_SCHEMA_DIR / "taxonomy_v1.json") as f:
            _taxonomy = json.load(f)
    return _taxonomy


def load_canonical_schema() -> dict:
    """Load and cache the canonical product schema."""
    global _canonical_schema
    if _canonical_schema is None:
        with open(_SCHEMA_DIR / "canonical_product_v1.json") as f:
            _canonical_schema = json.load(f)
    return _canonical_schema


def gtin_check_digit_valid(gtin: str) -> bool:
    """Validate a 13-digit GTIN/EAN-13 using the standard mod-10 check digit.

    Returns False for anything that is not exactly 13 digits or whose final
    digit does not match the computed check digit.
    """
    if not isinstance(gtin, str) or len(gtin) != 13 or not gtin.isdigit():
        return False
    digits = [int(c) for c in gtin]
    # Positions 1..12 (1-indexed): odd ×1, even ×3.
    total = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12]))
    check = (10 - (total % 10)) % 10
    return check == digits[12]


def best_taxonomy_match(
    raw_category: str, canonical_paths: list[str]
) -> tuple[str | None, float]:
    """Fuzzy-match a free-text supplier category to the best canonical path.

    Returns (best_path, score 0..100). Returns (None, 0.0) on empty input.
    """
    if not raw_category or not canonical_paths:
        return None, 0.0
    match = process.extractOne(
        raw_category, canonical_paths, scorer=fuzz.WRatio
    )
    if match is None:
        return None, 0.0
    path, score, _ = match
    return path, float(score)


def safe_json_serialize(obj):
    """Convert numpy/pandas types to JSON-serializable Python types."""
    if isinstance(obj, dict):
        return {k: safe_json_serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [safe_json_serialize(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        if np.isnan(v) or np.isinf(v):
            return None
        return v
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, (pd.Series,)):
        return obj.tolist()
    if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    return obj
