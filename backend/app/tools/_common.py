"""Shared utilities for contract-review tool implementations."""

import base64
import json
import re
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

_clause_patterns: dict | None = None
_risk_rules: dict | None = None
_canonical_schema: dict | None = None


def load_clause_patterns() -> dict:
    """Load and cache the clause-extraction heading patterns."""
    global _clause_patterns
    if _clause_patterns is None:
        with open(_SCHEMA_DIR / "clause_patterns.json") as f:
            _clause_patterns = json.load(f)
    return _clause_patterns


def load_risk_rules() -> dict:
    """Load and cache the clause risk-evaluation rules."""
    global _risk_rules
    if _risk_rules is None:
        with open(_SCHEMA_DIR / "risk_rules.json") as f:
            _risk_rules = json.load(f)
    return _risk_rules


def load_canonical_schema() -> dict:
    """Load and cache the canonical contract schema."""
    global _canonical_schema
    if _canonical_schema is None:
        with open(_SCHEMA_DIR / "canonical_contract_v1.json") as f:
            _canonical_schema = json.load(f)
    return _canonical_schema


def pdf_to_base64(path: Path) -> str:
    """Read a PDF and return its standard base64 encoding (for the document block)."""
    return base64.standard_b64encode(path.read_bytes()).decode("utf-8")


def extract_section(text: str, keywords: list[str]) -> str | None:
    """Return the body of the first contract section whose heading matches a keyword.

    Sections are delimited by numbered/uppercase headings (e.g. "9. LIMITATION OF
    LIABILITY"). Returns the text from the matched heading up to the next heading,
    or None if no heading matches.
    """
    if not text:
        return None
    # Split on headings like "12.", "12. TERM", "ARTICLE 5", or ALL-CAPS lines.
    heading_re = re.compile(
        r"(?m)^\s*(?:\d+\.\s+[A-Z][^\n]+|ARTICLE\s+\d+[^\n]*|[A-Z][A-Z ,&/-]{4,}[A-Z])\s*$"
    )
    matches = list(heading_re.finditer(text))
    for i, m in enumerate(matches):
        heading = m.group(0)
        if any(re.search(kw, heading, re.IGNORECASE) for kw in keywords):
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            return text[start:end].strip()
    # Fallback: keyword anywhere → return the surrounding paragraph.
    for kw in keywords:
        m = re.search(kw, text, re.IGNORECASE)
        if m:
            para_start = text.rfind("\n\n", 0, m.start()) + 2
            para_end = text.find("\n\n", m.end())
            return text[para_start : para_end if para_end != -1 else len(text)].strip()
    return None


def first_int(text: str | None) -> int | None:
    """Return the first integer found in a string, or None."""
    if not text:
        return None
    m = re.search(r"\d[\d,]*", text)
    return int(m.group(0).replace(",", "")) if m else None


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
