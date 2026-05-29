"""Tests for the four prior-authorization tools."""

import copy

from app.tools import (
    check_payer_policy,
    parse_pa_request,
    recommend_decision,
    validate_clinical_criteria,
)


class TestParsePARequest:
    async def test_parses_lumbar(self, settings, sample_data_dir):
        result = await parse_pa_request.execute(
            {"folder_path": str(sample_data_dir / "lumbar_mri")}, settings
        )
        assert "error" not in result
        assert result["cpt_code"] == "72148"
        assert result["diagnosis_count"] == 2
        # clinical_notes.txt should be merged into clinical.notes
        assert result["request"]["clinical"]["notes"]
        assert result["parse_warnings"] == []

    async def test_missing_folder(self, settings, tmp_path):
        result = await parse_pa_request.execute(
            {"folder_path": str(tmp_path / "nope")}, settings
        )
        assert "error" in result

    async def test_incomplete_parses_but_flags(self, settings, sample_data_dir):
        result = await parse_pa_request.execute(
            {"folder_path": str(sample_data_dir / "incomplete_request")}, settings
        )
        assert result["diagnosis_count"] == 1
        # no clinical_notes.txt present -> a warning
        assert any("clinical_notes" in w for w in result["parse_warnings"])


class TestValidateClinicalCriteria:
    async def test_valid_request(self, settings, sample_pa_request):
        result = await validate_clinical_criteria.execute(
            {"request": sample_pa_request}, settings
        )
        assert result["valid"] is True
        assert result["errors"] == []

    async def test_bad_cpt(self, settings, sample_pa_request):
        req = copy.deepcopy(sample_pa_request)
        req["procedure"]["cpt_code"] = "ABC"
        result = await validate_clinical_criteria.execute({"request": req}, settings)
        assert result["valid"] is False
        assert any("cpt" in e.lower() for e in result["errors"])

    async def test_no_primary_diagnosis(self, settings, sample_pa_request):
        req = copy.deepcopy(sample_pa_request)
        for dx in req["diagnoses"]:
            dx["primary"] = False
        result = await validate_clinical_criteria.execute({"request": req}, settings)
        assert result["valid"] is False
        assert any("primary" in e.lower() for e in result["errors"])

    async def test_bad_npi(self, settings, sample_pa_request):
        req = copy.deepcopy(sample_pa_request)
        req["ordering_provider"]["npi"] = "123"
        result = await validate_clinical_criteria.execute({"request": req}, settings)
        assert result["valid"] is False

    async def test_missing_clinical_field(self, settings, sample_pa_request):
        req = copy.deepcopy(sample_pa_request)
        del req["clinical"]["conservative_tx_weeks"]
        result = await validate_clinical_criteria.execute({"request": req}, settings)
        assert result["valid"] is False
        assert any("conservative_tx_weeks" in e for e in result["errors"])

    async def test_incomplete_sample_fails(self, settings, sample_data_dir):
        parsed = await parse_pa_request.execute(
            {"folder_path": str(sample_data_dir / "incomplete_request")}, settings
        )
        result = await validate_clinical_criteria.execute(
            {"request": parsed["request"]}, settings
        )
        assert result["valid"] is False


class TestCheckPayerPolicy:
    async def test_meets_policy(self, settings, sample_pa_request):
        result = await check_payer_policy.execute({"request": sample_pa_request}, settings)
        assert result["policy_found"] is True
        assert result["meets_policy"] is True
        assert result["criteria_met"] == result["criteria_total"]
        assert result["unmet_criteria"] == []

    async def test_unmet_policy(self, settings, sample_pa_request):
        req = copy.deepcopy(sample_pa_request)
        req["procedure"]["cpt_code"] = "29881"  # knee: needs PT + mechanical + 6wk
        req["clinical"]["conservative_tx_weeks"] = 3
        req["clinical"]["physical_therapy_completed"] = False
        req["clinical"]["mechanical_symptoms"] = True
        result = await check_payer_policy.execute({"request": req}, settings)
        assert result["policy_found"] is True
        assert result["meets_policy"] is False
        assert len(result["unmet_criteria"]) >= 1

    async def test_no_policy(self, settings, sample_pa_request):
        req = copy.deepcopy(sample_pa_request)
        req["procedure"]["cpt_code"] = "99999"
        result = await check_payer_policy.execute({"request": req}, settings)
        assert result["policy_found"] is False
        assert result["meets_policy"] is False


class TestRecommendDecision:
    async def test_valid_approve(self, settings):
        result = await recommend_decision.execute(
            {
                "decision": "approve",
                "rationale": "All 72148 criteria met.",
                "authorization_validity_days": 90,
                "confidence": 0.92,
            },
            settings,
        )
        assert result["decision"] == "approve"
        assert result["authorization_validity_days"] == 90
        assert result["validation_notes"] == []

    async def test_bad_decision(self, settings):
        result = await recommend_decision.execute(
            {"decision": "maybe", "rationale": "x", "confidence": 0.5}, settings
        )
        assert "error" in result

    async def test_pend_without_docs_warns(self, settings):
        result = await recommend_decision.execute(
            {"decision": "pend_for_info", "rationale": "missing PT records", "confidence": 0.6},
            settings,
        )
        assert any("required_documentation" in n for n in result["validation_notes"])

    async def test_confidence_clamped(self, settings):
        result = await recommend_decision.execute(
            {"decision": "deny", "rationale": "fails policy", "confidence": 1.4}, settings
        )
        assert result["confidence"] == 1.0
        # deny -> validity forced to 0
        assert result["authorization_validity_days"] == 0
