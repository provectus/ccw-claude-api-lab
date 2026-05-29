"""Shared test fixtures for product-catalog normalization tool tests."""

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
def sample_products():
    """Two valid canonical products with exact-canonical categories (deterministic)."""
    return [
        {
            "sku": "NW-1001",
            "gtin": "4006381333931",
            "brand": "Trailblaze",
            "title": "Trailblaze Hiking Boot",
            "supplier_category": "Apparel > Footwear",
            "price": {"amount": 89.99, "currency": "USD"},
        },
        {
            "sku": "NW-1003",
            "gtin": "8859090000009",
            "brand": "SoundWave",
            "title": "SoundWave Wireless Earbuds",
            "supplier_category": "Electronics > Audio",
            "price": {"amount": 59.99, "currency": "USD"},
        },
    ]
