"""Tool executor with live-then-fallback execution pattern."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.config import Settings
from app.tools.registry import execute_tool

logger = logging.getLogger(__name__)


async def execute_tool_with_fallback(
    tool_name: str,
    tool_input: dict,
    settings: Settings,
) -> dict:
    """Execute a tool live; fall back to pre-computed result on failure.

    Returns dict with keys:
        result  – tool output (dict)
        source  – "live" | "fallback" | "error"
    """
    try:
        result = await execute_tool(tool_name, tool_input, settings)
        if "error" in result:
            raise RuntimeError(result["error"])
        logger.info("Tool %s: live execution succeeded", tool_name)
        return {"result": result, "source": "live"}
    except Exception as exc:
        if not settings.fallback_enabled:
            logger.error("Tool %s: live failed, fallback disabled: %s", tool_name, exc)
            return {
                "result": {"error": str(exc)},
                "source": "error",
            }

        fallback_path = Path(settings.fallback_dir) / f"{tool_name}.json"
        if fallback_path.exists():
            logger.warning(
                "Tool %s: live failed (%s), using fallback", tool_name, exc
            )
            data = json.loads(fallback_path.read_text())
            return {"result": data, "source": "fallback"}

        logger.error(
            "Tool %s: live failed (%s), no fallback file at %s",
            tool_name, exc, fallback_path,
        )
        return {
            "result": {"error": str(exc)},
            "source": "error",
        }
