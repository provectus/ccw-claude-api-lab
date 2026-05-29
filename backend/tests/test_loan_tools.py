"""Tests for the four loan-underwriting tools."""

import copy

from app.tools import (
    assess_creditworthiness,
    compute_credit_ratios,
    parse_loan_package,
    validate_loan_application,
)


class TestParseLoanPackage:
    async def test_parses_acme(self, settings, sample_data_dir):
        result = await parse_loan_package.execute(
            {"folder_path": str(sample_data_dir / "acme_widgets")}, settings
        )
        assert "error" not in result
        app = result["application"]
        assert app["borrower_id"] == "ACME-0001"
        assert app["requested_amount"] == 750000
        assert result["years_parsed"] == 3
        assert app["collateral"]["appraised_value"] == 1100000
        assert result["parse_warnings"] == []

    async def test_missing_folder(self, settings, tmp_path):
        result = await parse_loan_package.execute(
            {"folder_path": str(tmp_path / "nope")}, settings
        )
        assert "error" in result

    async def test_charlie_has_two_years(self, settings, sample_data_dir):
        result = await parse_loan_package.execute(
            {"folder_path": str(sample_data_dir / "charlie_retail")}, settings
        )
        assert result["years_parsed"] == 2


class TestValidateLoanApplication:
    async def test_valid_application(self, settings, sample_loan_application):
        result = await validate_loan_application.execute(
            {"application": sample_loan_application}, settings
        )
        assert result["valid"] is True
        assert result["errors"] == []

    async def test_amount_out_of_bounds(self, settings, sample_loan_application):
        app = copy.deepcopy(sample_loan_application)
        app["requested_amount"] = 10_000_000
        result = await validate_loan_application.execute({"application": app}, settings)
        assert result["valid"] is False
        assert any("requested_amount" in e for e in result["errors"])

    async def test_bad_term(self, settings, sample_loan_application):
        app = copy.deepcopy(sample_loan_application)
        app["requested_term_months"] = 37
        result = await validate_loan_application.execute({"application": app}, settings)
        assert result["valid"] is False

    async def test_missing_year_fails(self, settings, sample_loan_application):
        app = copy.deepcopy(sample_loan_application)
        app["financials"] = app["financials"][:2]
        result = await validate_loan_application.execute({"application": app}, settings)
        assert result["valid"] is False
        assert any("years" in e.lower() for e in result["errors"])

    async def test_unbalanced_sheet_fails(self, settings, sample_loan_application):
        app = copy.deepcopy(sample_loan_application)
        app["financials"][-1]["total_assets"] = 9_999_999
        result = await validate_loan_application.execute({"application": app}, settings)
        assert result["valid"] is False
        assert any("balance sheet" in e.lower() for e in result["errors"])

    async def test_bad_naics(self, settings, sample_loan_application):
        app = copy.deepcopy(sample_loan_application)
        app["industry_naics"] = "33"
        result = await validate_loan_application.execute({"application": app}, settings)
        assert result["valid"] is False


class TestComputeCreditRatios:
    async def test_computes_ratios(self, settings, sample_loan_application):
        result = await compute_credit_ratios.execute(
            {"application": sample_loan_application}, settings
        )
        assert "error" not in result
        # DSCR = 520000 / ~184.6K ≈ 2.8x
        assert result["dscr"] > 2.0
        # current ratio = 1.4M / 0.7M = 2.0x
        assert result["current_ratio"] == 2.0
        # D/E = 1.15M / 1.65M ≈ 0.70x
        assert abs(result["debt_to_equity"] - 0.70) < 0.02
        # revenue grew -> positive CAGR
        assert result["revenue_cagr_3y_pct"] > 0
        # LTV = 750K / 1.1M ≈ 68%
        assert 67 < result["ltv_pct"] < 69

    async def test_no_collateral_no_ltv(self, settings, sample_loan_application):
        app = copy.deepcopy(sample_loan_application)
        app.pop("collateral")
        result = await compute_credit_ratios.execute({"application": app}, settings)
        assert result["ltv_pct"] is None

    async def test_empty_financials(self, settings):
        result = await compute_credit_ratios.execute(
            {"application": {"financials": []}}, settings
        )
        assert "error" in result


class TestAssessCreditworthiness:
    async def test_valid_assessment(self, settings):
        result = await assess_creditworthiness.execute(
            {
                "recommendation": "approve",
                "suggested_rate_bps": 825,
                "suggested_term_months": 60,
                "top_risks": ["customer concentration"],
                "confidence": 0.88,
                "reasoning": "DSCR of 2.8x and LTV of 68% support approval.",
            },
            settings,
        )
        assert result["recommendation"] == "approve"
        assert result["confidence"] == 0.88
        assert result["validation_notes"] == []

    async def test_bad_recommendation(self, settings):
        result = await assess_creditworthiness.execute(
            {
                "recommendation": "maybe",
                "suggested_rate_bps": 825,
                "suggested_term_months": 60,
                "top_risks": [],
                "confidence": 0.5,
                "reasoning": "x",
            },
            settings,
        )
        assert "error" in result

    async def test_confidence_clamped(self, settings):
        result = await assess_creditworthiness.execute(
            {
                "recommendation": "decline",
                "suggested_rate_bps": 0,
                "suggested_term_months": 60,
                "top_risks": ["insolvent"],
                "confidence": 1.7,
                "reasoning": "Negative equity.",
            },
            settings,
        )
        assert result["confidence"] == 1.0
        assert any("clamped" in n for n in result["validation_notes"])

    async def test_conditions_warning(self, settings):
        result = await assess_creditworthiness.execute(
            {
                "recommendation": "approve_with_conditions",
                "suggested_rate_bps": 950,
                "suggested_term_months": 36,
                "top_risks": ["declining revenue"],
                "confidence": 0.6,
                "reasoning": "Marginal DSCR.",
            },
            settings,
        )
        assert any("conditions" in n.lower() for n in result["validation_notes"])
