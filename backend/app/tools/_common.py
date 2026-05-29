"""Shared utilities for prior-authorization review tool implementations."""

import json
import operator
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

_criteria_rules: dict | None = None
_payer_policies: dict | None = None
_canonical_schema: dict | None = None


def load_criteria_rules() -> dict:
    """Load and cache the clinical/structural validation rules."""
    global _criteria_rules
    if _criteria_rules is None:
        with open(_SCHEMA_DIR / "criteria_rules.json") as f:
            _criteria_rules = json.load(f)
    return _criteria_rules


def load_payer_policies() -> dict:
    """Load and cache the per-CPT payer medical-necessity policies."""
    global _payer_policies
    if _payer_policies is None:
        with open(_SCHEMA_DIR / "payer_policies_v1.json") as f:
            _payer_policies = json.load(f)
    return _payer_policies


def load_canonical_schema() -> dict:
    """Load and cache the canonical PA request schema."""
    global _canonical_schema
    if _canonical_schema is None:
        with open(_SCHEMA_DIR / "canonical_pa_request_v1.json") as f:
            _canonical_schema = json.load(f)
    return _canonical_schema


def get_path(obj: dict, dotted: str):
    """Resolve a dotted path (e.g. 'clinical.conservative_tx_weeks') against a dict.

    Returns None if any segment is missing.
    """
    cur = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


_OPERATORS = {
    ">=": operator.ge,
    ">": operator.gt,
    "<=": operator.le,
    "<": operator.lt,
    "==": operator.eq,
    "!=": operator.ne,
}


def eval_criterion(actual, op: str, expected) -> bool:
    """Evaluate `actual <op> expected`. Returns False on missing data or bad op."""
    if actual is None or op not in _OPERATORS:
        return False
    try:
        return bool(_OPERATORS[op](actual, expected))
    except TypeError:
        return False


def format_pct(pct: float | None) -> str:
    """Format a percentage (already in percent units) for display."""
    if pct is None:
        return "N/A"
    return f"{pct:.0f}%"


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
