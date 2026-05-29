"""Tests for shared credit-underwriting utilities."""

import numpy as np

from app.tools._common import (
    amortized_annual_debt_service,
    compute_z_score,
    format_currency,
    format_pct,
    format_ratio,
    load_validation_rules,
    safe_div,
    safe_json_serialize,
)


class TestZScore:
    def test_normal_z_score(self):
        assert compute_z_score(3.0, 1.0, 1.0) == 2.0

    def test_zero_std_returns_none(self):
        assert compute_z_score(3.0, 1.0, 0) is None

    def test_none_std_returns_none(self):
        assert compute_z_score(3.0, 1.0, None) is None


class TestSafeDiv:
    def test_normal(self):
        assert safe_div(10, 4) == 2.5

    def test_zero_denominator(self):
        assert safe_div(10, 0) is None

    def test_none_operands(self):
        assert safe_div(None, 4) is None
        assert safe_div(10, None) is None


class TestAmortizedDebtService:
    def test_positive_rate(self):
        # $750K at 8.5% over 60 months -> ~$184.6K/yr
        annual = amortized_annual_debt_service(750000, 0.085, 60)
        assert 180000 < annual < 190000

    def test_zero_rate_is_straight_line(self):
        # $120K at 0% over 24 months -> $60K/yr
        assert amortized_annual_debt_service(120000, 0.0, 24) == 60000

    def test_zero_term(self):
        assert amortized_annual_debt_service(100000, 0.085, 0) == 0.0


class TestFormatting:
    def test_format_pct_positive(self):
        assert format_pct(13.2) == "+13.20%"

    def test_format_pct_negative(self):
        assert format_pct(-6.7) == "-6.70%"

    def test_format_pct_none(self):
        assert format_pct(None) == "N/A"

    def test_format_ratio(self):
        assert format_ratio(1.345) == "1.34x"

    def test_format_ratio_none(self):
        assert format_ratio(None) == "N/A"

    def test_format_currency_millions(self):
        assert "M" in format_currency(1_200_000)

    def test_format_currency_none(self):
        assert format_currency(None) == "N/A"


class TestSafeJsonSerialize:
    def test_numpy_int(self):
        result = safe_json_serialize(np.int64(42))
        assert result == 42 and isinstance(result, int)

    def test_numpy_nan_becomes_none(self):
        assert safe_json_serialize(np.nan) is None

    def test_nested_dict(self):
        data = {"a": np.int64(1), "b": [np.float64(2.0), np.nan]}
        assert safe_json_serialize(data) == {"a": 1, "b": [2.0, None]}

    def test_passthrough(self):
        assert safe_json_serialize("hello") == "hello"
        assert safe_json_serialize(None) is None


class TestValidationRules:
    def test_loads_rules(self):
        rules = load_validation_rules()
        assert "requested_amount" in rules
        assert "requested_term_months" in rules
        assert "financials" in rules

    def test_amount_bounds(self):
        rules = load_validation_rules()
        amt = rules["requested_amount"]
        assert amt["min"] < amt["max"]

    def test_required_years(self):
        rules = load_validation_rules()
        assert rules["financials"]["required_years"] == 3
