"""Tests for shared prior-authorization utilities."""

import numpy as np

from app.tools._common import (
    eval_criterion,
    format_pct,
    get_path,
    load_criteria_rules,
    load_payer_policies,
    safe_json_serialize,
)


class TestGetPath:
    def test_nested(self):
        obj = {"clinical": {"conservative_tx_weeks": 8}}
        assert get_path(obj, "clinical.conservative_tx_weeks") == 8

    def test_missing(self):
        assert get_path({"a": {}}, "a.b.c") is None

    def test_non_dict_segment(self):
        assert get_path({"a": 5}, "a.b") is None


class TestEvalCriterion:
    def test_gte_true(self):
        assert eval_criterion(8, ">=", 6) is True

    def test_gte_false(self):
        assert eval_criterion(3, ">=", 6) is False

    def test_eq_bool(self):
        assert eval_criterion(True, "==", True) is True

    def test_none_actual_is_false(self):
        assert eval_criterion(None, ">=", 6) is False

    def test_bad_operator_is_false(self):
        assert eval_criterion(8, "~", 6) is False

    def test_type_mismatch_is_false(self):
        assert eval_criterion("eight", ">=", 6) is False


class TestFormatting:
    def test_pct(self):
        assert format_pct(75.0) == "75%"

    def test_pct_none(self):
        assert format_pct(None) == "N/A"


class TestSafeJsonSerialize:
    def test_numpy_int(self):
        result = safe_json_serialize(np.int64(42))
        assert result == 42 and isinstance(result, int)

    def test_numpy_nan_becomes_none(self):
        assert safe_json_serialize(np.nan) is None

    def test_nested(self):
        assert safe_json_serialize({"a": np.int64(1), "b": [np.bool_(True)]}) == {"a": 1, "b": [True]}

    def test_passthrough(self):
        assert safe_json_serialize("hi") == "hi"
        assert safe_json_serialize(None) is None


class TestSchemaLoaders:
    def test_criteria_rules(self):
        rules = load_criteria_rules()
        assert "cpt_code" in rules
        assert rules["diagnoses"]["require_primary"] is True
        assert "conservative_tx_weeks" in rules["clinical"]["required_fields"]

    def test_payer_policies(self):
        policies = load_payer_policies()["policies"]
        assert "72148" in policies
        assert all("criteria" in p for p in policies.values())
