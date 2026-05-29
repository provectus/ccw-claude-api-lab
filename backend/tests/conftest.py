"""Shared test fixtures for contract-review tool tests."""

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
def sample_contract_text():
    """Vendor-favorable MSA text (mirrors vendorco_msa) for deterministic extraction tests."""
    src = _SAMPLE_DATA_DIR / "vendorco_msa.txt"
    if src.exists():
        return src.read_text()
    # Fallback inline copy so tests don't depend on the .txt being present.
    return (
        "MASTER SERVICES AGREEMENT\n\n"
        "This Master Services Agreement is entered into by and between VendorCo LLC and "
        "Customer as of the Effective Date, March 15, 2026.\n\n"
        "2. TERM AND TERMINATION\n"
        "The initial term is 24 months. Thereafter, this Agreement shall automatically renew "
        "for successive 24-month periods unless either party provides written notice of "
        "non-renewal at least 90 days prior to the end of the then-current term. Vendor may "
        "terminate for convenience upon 30 days notice; Customer has no right to terminate for "
        "convenience.\n\n"
        "5. INDEMNIFICATION\n"
        "Customer shall indemnify, defend, and hold harmless Vendor from any and all claims. "
        "Vendor provides no reciprocal indemnification.\n\n"
        "6. LIMITATION OF LIABILITY\n"
        "Vendor's total aggregate liability shall not exceed the fees paid in the three (3) "
        "months preceding the claim. In no event shall Vendor be liable for consequential damages.\n\n"
        "7. GOVERNING LAW\n"
        "This Agreement shall be governed by the laws of the State of New York.\n"
    )
