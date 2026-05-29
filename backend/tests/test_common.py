"""Tests for shared catalog-normalization utilities."""

import numpy as np

from app.tools._common import (
    best_taxonomy_match,
    gtin_check_digit_valid,
    load_catalog_rules,
    load_taxonomy,
    safe_json_serialize,
)


class TestGtinCheckDigit:
    def test_valid_gtins(self):
        assert gtin_check_digit_valid("4006381333931") is True
        assert gtin_check_digit_valid("0012345678905") is True
        assert gtin_check_digit_valid("8859090000009") is True

    def test_invalid_check_digit(self):
        assert gtin_check_digit_valid("4006381333930") is False

    def test_wrong_length(self):
        assert gtin_check_digit_valid("400638133393") is False
        assert gtin_check_digit_valid("40063813339311") is False

    def test_non_digit(self):
        assert gtin_check_digit_valid("40063813339AB") is False
        assert gtin_check_digit_valid("") is False


class TestTaxonomyMatch:
    def test_exact_match(self):
        paths = load_taxonomy()["paths"]
        best, score = best_taxonomy_match("Apparel > Footwear", paths)
        assert best == "Apparel > Footwear"
        assert score >= 95

    def test_gibberish_low_score(self):
        paths = load_taxonomy()["paths"]
        _, score = best_taxonomy_match("zzzz qqqq xyzzy", paths)
        assert score < 65

    def test_empty_input(self):
        assert best_taxonomy_match("", ["Apparel > Footwear"]) == (None, 0.0)


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
    def test_catalog_rules(self):
        rules = load_catalog_rules()
        assert rules["gtin"]["length"] == 13
        assert "USD" in rules["price"]["allowed_currencies"]
        assert "sku" in rules["required_fields"]

    def test_taxonomy(self):
        tax = load_taxonomy()
        assert "Apparel > Footwear" in tax["paths"]
        assert tax["confident_threshold"] > tax["review_threshold"]
