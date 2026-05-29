"""Tests for agent_runner with mocked Anthropic API."""

import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.config import Settings
from app.services.agent_runner import run_agent, _build_initial_message
from app.services.pipeline_store import PipelineState


@pytest.fixture
def agent_settings(tmp_path):
    return Settings(
        anthropic_api_key="test-key",
        synthetic_dir=tmp_path / "synthetic",
        processed_dir=tmp_path / "processed",
        upload_dir=tmp_path / "uploads",
        fallback_dir=tmp_path / "fallbacks",
        fallback_enabled=False,
        pipeline_timeout_seconds=60,
    )


@pytest.fixture
def pipeline():
    return PipelineState(
        id="test-pipeline",
        status="pending",
        file_paths=["/data/lumbar_mri"],
        metadata={"request_id": "PA-TEST", "cpt_code": "72148"},
    )


def _make_text_block(text: str):
    return SimpleNamespace(type="text", text=text)


def _make_tool_use_block(name: str, tool_input: dict, block_id: str = "tu_1"):
    return SimpleNamespace(type="tool_use", name=name, input=tool_input, id=block_id)


def _make_response(content: list, stop_reason: str = "end_turn"):
    return SimpleNamespace(content=content, stop_reason=stop_reason)


class TestBuildInitialMessage:
    def test_includes_file_paths(self):
        msg = _build_initial_message(["/a.xlsx", "/b.pdf"], {})
        assert "/a.xlsx" in msg
        assert "/b.pdf" in msg

    def test_includes_metadata(self):
        msg = _build_initial_message([], {"request_id": "PA-123"})
        assert "PA-123" in msg

    def test_mentions_pa_review(self):
        msg = _build_initial_message(["/data/lumbar_mri"], {})
        assert "authorization" in msg.lower() or "review" in msg.lower()


class TestRunAgent:
    @patch("app.services.agent_runner.anthropic.AsyncAnthropic")
    async def test_text_only_response(self, mock_cls, agent_settings, pipeline):
        """Agent returns text only -> completes immediately."""
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _make_response(
            [_make_text_block("Analysis complete. No issues found.")],
            stop_reason="end_turn",
        )

        await run_agent(pipeline, agent_settings)

        assert pipeline.status == "completed"
        assert any(e["type"] == "reasoning" for e in pipeline.events)
        assert any(e["type"] == "complete" for e in pipeline.events)

    @patch("app.services.agent_runner.execute_tool_with_fallback")
    @patch("app.services.agent_runner.anthropic.AsyncAnthropic")
    async def test_single_tool_call(self, mock_cls, mock_exec, agent_settings, pipeline):
        """Agent makes one tool call then completes."""
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client

        mock_client.messages.create.side_effect = [
            _make_response(
                [
                    _make_text_block("Let me parse the PA request."),
                    _make_tool_use_block("parse_pa_request", {"folder_path": "/data/lumbar_mri"}),
                ],
                stop_reason="tool_use",
            ),
            _make_response(
                [_make_text_block("Request parsed successfully.")],
                stop_reason="end_turn",
            ),
        ]

        mock_exec.return_value = {
            "result": {"diagnosis_count": 2, "request": {}},
            "source": "live",
        }

        await run_agent(pipeline, agent_settings)

        assert pipeline.status == "completed"
        tool_starts = [e for e in pipeline.events if e["type"] == "tool_start"]
        tool_results = [e for e in pipeline.events if e["type"] == "tool_result"]
        assert len(tool_starts) == 1
        assert len(tool_results) == 1
        assert tool_results[0]["source"] == "live"

    @patch("app.services.agent_runner.anthropic.AsyncAnthropic")
    async def test_api_failure(self, mock_cls, agent_settings, pipeline):
        """API call raises exception -> pipeline fails gracefully."""
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API rate limit")

        await run_agent(pipeline, agent_settings)

        assert pipeline.status == "failed"
        assert "API rate limit" in pipeline.error
        assert any(e["type"] == "error" for e in pipeline.events)

    @patch("app.services.agent_runner.execute_tool_with_fallback")
    @patch("app.services.agent_runner.anthropic.AsyncAnthropic")
    async def test_assessment_captured(self, mock_cls, mock_exec, agent_settings, pipeline):
        """recommend_decision result is saved to pipeline.assessment."""
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client

        assessment_data = {
            "decision": "approve",
            "confidence": 0.92,
        }

        mock_client.messages.create.side_effect = [
            _make_response(
                [
                    _make_tool_use_block(
                        "recommend_decision",
                        {"decision": "approve"},
                        block_id="tu_decision",
                    ),
                ],
                stop_reason="tool_use",
            ),
            _make_response(
                [_make_text_block("Determination complete.")],
                stop_reason="end_turn",
            ),
        ]

        mock_exec.return_value = {
            "result": assessment_data,
            "source": "live",
        }

        await run_agent(pipeline, agent_settings)

        assert pipeline.status == "completed"
        assert pipeline.assessment == assessment_data


@pytest.mark.integration
class TestAgentRunnerIntegration:
    """Full agentic loop integration test — requires ANTHROPIC_API_KEY."""

    @pytest.fixture
    def integration_settings(self, tmp_path):
        import os

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set")

        sample = Path(__file__).resolve().parent.parent.parent / "sample-data"
        if not (sample / "lumbar_mri" / "request.json").exists():
            pytest.skip("Sample data not present")

        return Settings(
            anthropic_api_key=api_key,
            sample_data_dir=sample,
            processed_dir=tmp_path / "processed",
            upload_dir=tmp_path / "uploads",
            fallback_dir=tmp_path / "fallbacks",
            fallback_enabled=False,
            pipeline_timeout_seconds=300,
        )

    @pytest.fixture
    def integration_pipeline(self):
        sample = Path(__file__).resolve().parent.parent.parent / "sample-data"
        return PipelineState(
            id="integration-test",
            status="pending",
            file_paths=[str(sample / "lumbar_mri")],
            metadata={
                "request_id": "PA-2026-0413",
                "cpt_code": "72148",
                "plan_type": "PPO",
            },
        )

    async def test_full_agentic_loop(self, integration_settings, integration_pipeline):
        """Run complete pipeline with Claude — verifies the core tools are called."""
        import time

        start = time.monotonic()
        await run_agent(integration_pipeline, integration_settings)
        duration = time.monotonic() - start

        assert integration_pipeline.status == "completed", (
            f"Pipeline failed: {integration_pipeline.error}"
        )

        tool_results = [
            e for e in integration_pipeline.events if e.get("type") == "tool_result"
        ]
        tool_names = {e["tool"] for e in tool_results}
        expected_tools = {
            "parse_pa_request",
            "validate_clinical_criteria",
            "check_payer_policy",
            "recommend_decision",
        }
        assert expected_tools.issubset(tool_names), (
            f"Missing tools: {expected_tools - tool_names}"
        )

        assert any(e["type"] == "complete" for e in integration_pipeline.events)
        assert integration_pipeline.assessment is not None
        assert duration < 300, f"Pipeline took {duration:.0f}s (max 300s)"
