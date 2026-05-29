"""Tests for the four catalog-normalization tools."""

import copy

from app.tools import (
    generate_import_report,
    map_to_canonical_taxonomy,
    parse_supplier_feed,
    validate_skus,
)


class TestParseSupplierFeed:
    async def test_parses_northwind(self, settings, sample_data_dir):
        result = await parse_supplier_feed.execute(
            {"folder_path": str(sample_data_dir / "northwind_feed")}, settings
        )
        assert "error" not in result
        assert result["supplier"] == "Northwind Trading"
        assert result["row_count"] == 3
        first = result["products"][0]
        # column_map applied: item_no -> sku, unit_price -> price.amount
        assert first["sku"] == "NW-1001"
        assert first["price"]["amount"] == 89.99
        assert first["supplier_category"] == "Footwear"

    async def test_missing_folder(self, settings, tmp_path):
        result = await parse_supplier_feed.execute(
            {"folder_path": str(tmp_path / "nope")}, settings
        )
        assert "error" in result

    async def test_globalmart_missing_price(self, settings, sample_data_dir):
        result = await parse_supplier_feed.execute(
            {"folder_path": str(sample_data_dir / "globalmart_feed")}, settings
        )
        assert result["row_count"] == 4
        # GM-9003 has an empty price cell
        lamp = next(p for p in result["products"] if p["sku"] == "GM-9003")
        assert lamp["price"]["amount"] is None


class TestValidateSkus:
    async def test_all_valid(self, settings, sample_products):
        result = await validate_skus.execute({"products": sample_products}, settings)
        assert result["all_valid"] is True
        assert result["valid_count"] == 2

    async def test_bad_gtin(self, settings, sample_products):
        products = copy.deepcopy(sample_products)
        products[0]["gtin"] = "4006381333930"  # bad check digit
        result = await validate_skus.execute({"products": products}, settings)
        assert result["all_valid"] is False
        assert any("gtin" in e.lower() for i in result["issues"] for e in i["errors"])

    async def test_missing_price(self, settings, sample_products):
        products = copy.deepcopy(sample_products)
        products[1]["price"] = {"amount": None, "currency": "USD"}
        result = await validate_skus.execute({"products": products}, settings)
        assert result["invalid_count"] == 1

    async def test_unsupported_currency(self, settings, sample_products):
        products = copy.deepcopy(sample_products)
        products[0]["price"] = {"amount": 10.0, "currency": "JPY"}
        result = await validate_skus.execute({"products": products}, settings)
        assert result["all_valid"] is False

    async def test_globalmart_has_rejects(self, settings, sample_data_dir):
        parsed = await parse_supplier_feed.execute(
            {"folder_path": str(sample_data_dir / "globalmart_feed")}, settings
        )
        result = await validate_skus.execute({"products": parsed["products"]}, settings)
        # bad GTIN check digit + missing price = at least 2 rejects
        assert result["invalid_count"] >= 2


class TestMapToCanonicalTaxonomy:
    async def test_exact_categories_map(self, settings, sample_products):
        result = await map_to_canonical_taxonomy.execute({"products": sample_products}, settings)
        assert result["mapped_count"] == 2
        assert result["results"][0]["canonical_category"] == "Apparel > Footwear"
        assert result["results"][0]["status"] == "mapped"

    async def test_gibberish_unmapped(self, settings, sample_products):
        products = copy.deepcopy(sample_products)
        products[0]["supplier_category"] = "zzzz qqqq xyzzy"
        result = await map_to_canonical_taxonomy.execute({"products": products}, settings)
        statuses = {r["sku"]: r["status"] for r in result["results"]}
        assert statuses["NW-1001"] in ("needs_review", "unmapped")


class TestGenerateImportReport:
    async def test_valid_report(self, settings):
        result = await generate_import_report.execute(
            {
                "recommendation": "import_with_review",
                "ready_count": 5,
                "needs_review_count": 3,
                "rejected_count": 2,
                "summary": "Mostly clean; 3 categories need review, 2 bad barcodes.",
                "top_issues": ["invalid GTIN check digits", "low-confidence categories"],
                "confidence": 0.8,
            },
            settings,
        )
        assert result["recommendation"] == "import_with_review"
        assert result["total_evaluated"] == 10
        assert result["validation_notes"] == []

    async def test_bad_recommendation(self, settings):
        result = await generate_import_report.execute(
            {"recommendation": "ship_it", "ready_count": 1, "needs_review_count": 0,
             "rejected_count": 0, "summary": "x", "confidence": 0.5},
            settings,
        )
        assert "error" in result

    async def test_import_clean_inconsistency_warns(self, settings):
        result = await generate_import_report.execute(
            {"recommendation": "import_clean", "ready_count": 5, "needs_review_count": 0,
             "rejected_count": 3, "summary": "x", "confidence": 0.9},
            settings,
        )
        assert any("import_clean" in n for n in result["validation_notes"])

    async def test_confidence_clamped(self, settings):
        result = await generate_import_report.execute(
            {"recommendation": "hold", "ready_count": 0, "needs_review_count": 0,
             "rejected_count": 4, "summary": "all broken", "confidence": 1.9},
            settings,
        )
        assert result["confidence"] == 1.0
