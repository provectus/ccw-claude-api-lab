"""Tests for the four contract-review tools."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.tools import (
    evaluate_clause_risk,
    extract_clauses,
    generate_review_memo,
    parse_contract_pdf,
)


class TestParseContractPdf:
    @patch("app.tools.parse_contract_pdf.anthropic.AsyncAnthropic")
    async def test_claude_native(self, mock_cls, settings, sample_data_dir):
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = SimpleNamespace(
            content=[SimpleNamespace(type="text", text="CONTRACT TEXT HERE")]
        )
        result = await parse_contract_pdf.execute(
            {"file_path": str(sample_data_dir / "acme_saas_msa.pdf")}, settings
        )
        assert "error" not in result
        assert result["method"] == "claude"
        assert result["text"] == "CONTRACT TEXT HERE"

    async def test_missing_file(self, settings, tmp_path):
        result = await parse_contract_pdf.execute(
            {"file_path": str(tmp_path / "nope.pdf")}, settings
        )
        assert "error" in result

    async def test_docling_not_installed(self, settings, sample_data_dir):
        # Docling is an optional dep; absent → clean error, not a crash.
        result = await parse_contract_pdf.execute(
            {"file_path": str(sample_data_dir / "acme_saas_msa.pdf"), "method": "docling"},
            settings,
        )
        assert "error" in result and "docling" in result["error"].lower()


class TestExtractClauses:
    async def test_extracts_vendor_contract(self, settings, sample_contract_text):
        result = await extract_clauses.execute({"text": sample_contract_text}, settings)
        c = result["contract"]
        assert any("VendorCo" in p for p in c["parties"])
        assert c["term_months"] == 24
        assert c["auto_renewal"]["present"] is True
        assert c["auto_renewal"]["notice_days"] == 90
        assert c["indemnification"]["present"] is True
        assert c["indemnification"]["mutual"] is False
        assert c["termination"]["customer_for_convenience"] is False
        assert c["liability_cap"]["present"] is True

    async def test_empty_text(self, settings):
        result = await extract_clauses.execute({"text": "  "}, settings)
        assert "error" in result


class TestEvaluateClauseRisk:
    def _vendor_contract(self):
        return {
            "auto_renewal": {"present": True, "notice_days": 90},
            "liability_cap": {"present": True, "excludes_consequential": True},
            "indemnification": {"present": True, "mutual": False},
            "termination": {"customer_for_convenience": False},
            "raw_clauses": {"liability_cap": "x", "indemnification": "x", "termination": "x"},
        }

    async def test_high_risk_contract(self, settings):
        result = await evaluate_clause_risk.execute({"contract": self._vendor_contract()}, settings)
        assert result["overall_risk"] == "high"
        assert result["high_count"] >= 1
        clauses = {f["clause"] for f in result["flags"]}
        assert "auto_renewal" in clauses
        assert "indemnification" in clauses
        # confidentiality is a required clause and is absent here
        assert "confidentiality" in clauses

    async def test_clean_contract(self, settings):
        clean = {
            "auto_renewal": {"present": False, "notice_days": None},
            "liability_cap": {"present": True, "excludes_consequential": False},
            "indemnification": {"present": True, "mutual": True},
            "termination": {"customer_for_convenience": True},
            "raw_clauses": {
                "liability_cap": "x", "indemnification": "x",
                "termination": "x", "confidentiality": "x",
            },
        }
        result = await evaluate_clause_risk.execute({"contract": clean}, settings)
        assert result["high_count"] == 0
        assert result["overall_risk"] in ("none", "low")


class TestGenerateReviewMemo:
    async def test_valid_memo(self, settings):
        result = await generate_review_memo.execute(
            {
                "recommendation": "negotiate",
                "overall_risk": "high",
                "summary": "Auto-renewal trap and one-sided indemnity.",
                "flagged_clauses": [{"clause": "auto_renewal", "severity": "high", "message": "x"}],
                "recommended_redlines": ["Cut auto-renewal notice to 30 days"],
                "confidence": 0.85,
            },
            settings,
        )
        assert result["recommendation"] == "negotiate"
        assert result["validation_notes"] == []

    async def test_bad_recommendation(self, settings):
        result = await generate_review_memo.execute(
            {"recommendation": "sign_it", "overall_risk": "low", "summary": "x", "confidence": 0.5},
            settings,
        )
        assert "error" in result

    async def test_negotiate_without_redlines_warns(self, settings):
        result = await generate_review_memo.execute(
            {"recommendation": "negotiate", "overall_risk": "medium", "summary": "x", "confidence": 0.6},
            settings,
        )
        assert any("redline" in n.lower() for n in result["validation_notes"])

    async def test_high_risk_approve_warns(self, settings):
        result = await generate_review_memo.execute(
            {"recommendation": "approve", "overall_risk": "high", "summary": "x", "confidence": 0.5},
            settings,
        )
        assert any("approve" in n.lower() for n in result["validation_notes"])
