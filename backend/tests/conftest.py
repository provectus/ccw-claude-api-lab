"""Shared test fixtures for prior-authorization tool tests."""

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
def sample_pa_request():
    """A complete, valid canonical PARequest for tool tests (mirrors lumbar_mri)."""
    return {
        "request_id": "PA-TEST-0001",
        "patient": {
            "patient_id": "PT-1", "age": 54, "sex": "F",
            "member_id": "MBR-1", "plan_type": "PPO",
        },
        "procedure": {
            "cpt_code": "72148",
            "description": "MRI lumbar spine without contrast",
            "place_of_service": "22",
            "requested_units": 1,
        },
        "diagnoses": [
            {"icd10_code": "M54.50", "description": "Low back pain", "primary": True},
            {"icd10_code": "M51.36", "description": "Disc degeneration", "primary": False},
        ],
        "ordering_provider": {"npi": "1487654321", "name": "Dr. Ruiz", "specialty": "Orthopedics"},
        "clinical": {
            "indication": "Chronic low back pain unresponsive to conservative care",
            "conservative_tx_weeks": 8,
            "physical_therapy_completed": True,
            "prior_imaging": True,
            "mechanical_symptoms": False,
            "neuro_deficit": False,
            "notes": "8 weeks conservative care, completed PT, x-ray done.",
        },
        "supporting_docs": ["pt_records", "xray_report"],
    }
