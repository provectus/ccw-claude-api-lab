"""Tests for tool_executor with fallback."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.config import Settings
from app.services.tool_executor import execute_tool_with_fallback


@pytest.fixture
def fb_settings(tmp_path):
    """Settings with fallback enabled and a fallback dir."""
    fb_dir = tmp_path / "fallbacks"
    fb_dir.mkdir()
    return Settings(
        anthropic_api_key="test-key",
        fallback_dir=fb_dir,
        fallback_enabled=True,
        synthetic_dir=tmp_path / "synthetic",
        processed_dir=tmp_path / "processed",
        upload_dir=tmp_path / "uploads",
    )


class TestToolExecutor:
    @patch("app.services.tool_executor.execute_tool")
    async def test_live_success(self, mock_exec, fb_settings):
        mock_exec.return_value = {"total_records": 100}
        result = await execute_tool_with_fallback("parse_supplier_feed", {"file_path": "x"}, fb_settings)
        assert result["source"] == "live"
        assert result["result"]["total_records"] == 100

    @patch("app.services.tool_executor.execute_tool")
    async def test_live_error_triggers_fallback(self, mock_exec, fb_settings):
        mock_exec.side_effect = RuntimeError("boom")
        # Write a fallback file
        fb_file = fb_settings.fallback_dir / "parse_supplier_feed.json"
        fb_file.write_text(json.dumps({"total_records": 42, "fallback": True}))

        result = await execute_tool_with_fallback("parse_supplier_feed", {"file_path": "x"}, fb_settings)
        assert result["source"] == "fallback"
        assert result["result"]["total_records"] == 42

    @patch("app.services.tool_executor.execute_tool")
    async def test_tool_returns_error_key_triggers_fallback(self, mock_exec, fb_settings):
        mock_exec.return_value = {"error": "File not found"}
        fb_file = fb_settings.fallback_dir / "parse_supplier_feed.json"
        fb_file.write_text(json.dumps({"total_records": 42}))

        result = await execute_tool_with_fallback("parse_supplier_feed", {"file_path": "x"}, fb_settings)
        assert result["source"] == "fallback"

    @patch("app.services.tool_executor.execute_tool")
    async def test_fallback_disabled(self, mock_exec, fb_settings):
        fb_settings_no_fb = fb_settings.model_copy(update={"fallback_enabled": False})
        mock_exec.side_effect = RuntimeError("boom")

        result = await execute_tool_with_fallback("parse_supplier_feed", {"file_path": "x"}, fb_settings_no_fb)
        assert result["source"] == "error"

    @patch("app.services.tool_executor.execute_tool")
    async def test_no_fallback_file(self, mock_exec, fb_settings):
        mock_exec.side_effect = RuntimeError("boom")
        # No fallback file written
        result = await execute_tool_with_fallback("parse_supplier_feed", {"file_path": "x"}, fb_settings)
        assert result["source"] == "error"
