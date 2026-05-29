"""Shared utilities for credit-underwriting tool implementations."""

import json
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

_validation_rules: dict | None = None
_canonical_schema: dict | None = None


def load_validation_rules() -> dict:
    """Load and cache the loan validation rules configuration."""
    global _validation_rules
    if _validation_rules is None:
        with open(_SCHEMA_DIR / "validation_rules.json") as f:
            _validation_rules = json.load(f)
    return _validation_rules


def load_canonical_schema() -> dict:
    """Load and cache the canonical loan application schema."""
    global _canonical_schema
    if _canonical_schema is None:
        with open(_SCHEMA_DIR / "canonical_loan_application_v1.json") as f:
            _canonical_schema = json.load(f)
    return _canonical_schema


def compute_z_score(value: float, mean: float, std: float) -> float | None:
    """Compute z-score for a value given mean and standard deviation."""
    if std is None or std == 0:
        return None
    return (value - mean) / std


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    """Divide two numbers, returning None on a zero/None denominator."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def amortized_annual_debt_service(
    principal: float, annual_rate: float, term_months: int
) -> float:
    """Annual debt service for a fully-amortizing loan.

    Uses the standard amortization payment formula on a monthly basis, then
    annualizes. Falls back to straight-line principal if the rate is zero.
    """
    if term_months <= 0:
        return 0.0
    if annual_rate <= 0:
        return principal / (term_months / 12)
    monthly_rate = annual_rate / 12
    monthly_payment = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** term_months
        / ((1 + monthly_rate) ** term_months - 1)
    )
    return monthly_payment * 12


def format_pct(pct: float | None) -> str:
    """Format a percentage (already in percent units) for display."""
    if pct is None:
        return "N/A"
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def format_ratio(ratio: float | None, suffix: str = "x") -> str:
    """Format a coverage/leverage ratio for display (e.g. 1.42x)."""
    if ratio is None:
        return "N/A"
    return f"{ratio:.2f}{suffix}"


def format_currency(amount: float | None, currency: str = "USD") -> str:
    """Format currency amount for display."""
    if amount is None:
        return "N/A"
    if abs(amount) >= 1_000_000_000:
        return f"${amount / 1_000_000_000:,.2f}B"
    if abs(amount) >= 1_000_000:
        return f"${amount / 1_000_000:,.2f}M"
    if abs(amount) >= 1_000:
        return f"${amount / 1_000:,.2f}K"
    return f"${amount:,.2f}"


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
