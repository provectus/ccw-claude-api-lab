"""Shared test fixtures for loan-underwriting tool tests."""

from pathlib import Path

import pytest

from app.config import Settings

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SAMPLE_DATA_DIR = _REPO_ROOT / "sample-data"


@pytest.fixture
def settings(tmp_path):
    processed = tmp_path / "processed"
    processed.mkdir()
    return Settings(
        anthropic_api_key="test-key",
        processed_dir=processed,
        upload_dir=tmp_path / "uploads",
        fallback_dir=tmp_path / "fallbacks",
        sample_data_dir=_SAMPLE_DATA_DIR,
    )


@pytest.fixture
def sample_data_dir():
    """Path to the repo-root sample-data directory."""
    return _SAMPLE_DATA_DIR


@pytest.fixture
def sample_loan_application():
    """A complete, valid canonical LoanApplication for tool tests."""
    return {
        "borrower_id": "TEST-0001",
        "business_name": "Test Manufacturing Co",
        "industry_naics": "333249",
        "requested_amount": 750000,
        "requested_term_months": 60,
        "purpose": "equipment",
        "collateral": {"type": "equipment", "appraised_value": 1100000},
        "financials": [
            {
                "fiscal_year": 2022, "revenue": 3200000, "cogs": 1920000,
                "opex": 900000, "ebitda": 380000, "net_income": 250000,
                "total_assets": 2300000, "total_liabilities": 1050000, "equity": 1250000,
                "cash": 250000, "accounts_receivable": 430000, "inventory": 400000,
                "current_assets": 1150000, "current_liabilities": 620000,
            },
            {
                "fiscal_year": 2023, "revenue": 3650000, "cogs": 2150000,
                "opex": 980000, "ebitda": 450000, "net_income": 330000,
                "total_assets": 2550000, "total_liabilities": 1100000, "equity": 1450000,
                "cash": 300000, "accounts_receivable": 470000, "inventory": 440000,
                "current_assets": 1270000, "current_liabilities": 660000,
            },
            {
                "fiscal_year": 2024, "revenue": 4100000, "cogs": 2380000,
                "opex": 1050000, "ebitda": 520000, "net_income": 430000,
                "total_assets": 2800000, "total_liabilities": 1150000, "equity": 1650000,
                "cash": 350000, "accounts_receivable": 520000, "inventory": 480000,
                "current_assets": 1400000, "current_liabilities": 700000,
            },
        ],
    }
