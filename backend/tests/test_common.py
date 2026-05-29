"""Tests for shared contract-review utilities."""

import numpy as np

from app.tools._common import (
    extract_section,
    first_int,
    load_clause_patterns,
    load_risk_rules,
    safe_json_serialize,
)

_SAMPLE = (
    "AGREEMENT\n\n"
    "2. TERM AND TERMINATION\n"
    "The initial term is 24 months and renews automatically unless cancelled 90 days prior.\n\n"
    "7. LIMITATION OF LIABILITY\n"
    "Liability shall not exceed fees paid in the prior 3 months.\n\n"
    "8. GOVERNING LAW\n"
    "Governed by the laws of the State of New York.\n"
)


class TestExtractSection:
    def test_finds_liability(self):
        body = extract_section(_SAMPLE, ["LIMITATION OF LIABILITY", "LIABILITY"])
        assert body is not None and "not exceed" in body

    def test_finds_term(self):
        body = extract_section(_SAMPLE, ["TERM"])
        assert body is not None and "24 months" in body

    def test_missing_returns_none(self):
        assert extract_section(_SAMPLE, ["FORCE MAJEURE"]) is None

    def test_empty_text(self):
        assert extract_section("", ["TERM"]) is None


class TestFirstInt:
    def test_basic(self):
        assert first_int("at least 90 days") == 90

    def test_comma(self):
        assert first_int("up to 1,500 units") == 1500

    def test_none(self):
        assert first_int("no digits here") is None
        assert first_int(None) is None


class TestSafeJsonSerialize:
    def test_numpy_int(self):
        result = safe_json_serialize(np.int64(42))
        assert result == 42 and isinstance(result, int)

    def test_nested(self):
        assert safe_json_serialize({"a": np.int64(1), "b": [np.bool_(True)]}) == {"a": 1, "b": [True]}

    def test_passthrough(self):
        assert safe_json_serialize("hi") == "hi"
        assert safe_json_serialize(None) is None


class TestSchemaLoaders:
    def test_clause_patterns(self):
        patterns = load_clause_patterns()["clauses"]
        assert "liability_cap" in patterns
        assert "auto_renewal" in patterns

    def test_risk_rules(self):
        rules = load_risk_rules()
        assert rules["auto_renewal_notice_days_threshold"] == 30
        assert "liability_cap" in rules["required_clauses"]
