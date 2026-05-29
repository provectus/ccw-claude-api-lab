"""Agentic loop: Claude drives the loan-underwriting pipeline via tool use."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import anthropic

from app.config import Settings
from app.services.pipeline_store import PipelineState
from app.services.tool_executor import execute_tool_with_fallback
from app.tools.registry import get_tool_definitions

logger = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
_MAX_ITERATIONS = 25


def _load_system_prompt() -> str:
    """Load the credit analyst system prompt."""
    prompt_path = _PROMPTS_DIR / "credit_analyst.md"
    return prompt_path.read_text()


def _build_initial_message(file_paths: list[str], metadata: dict) -> str:
    """Build the initial user message from loan-package paths and borrower metadata."""
    parts = ["I have the following loan-package files to underwrite:\n"]
    for fp in file_paths:
        parts.append(f"- `{fp}`")

    if metadata:
        parts.append("\n**Borrower Metadata:**")
        for key, value in metadata.items():
            parts.append(f"- **{key}**: {value}")

    parts.append(
        "\nPlease underwrite this loan application through the complete pipeline "
        "and produce a creditworthiness assessment with a recommendation."
    )
    return "\n".join(parts)


async def run_agent(pipeline: PipelineState, settings: Settings) -> None:
    """Run the agentic loop for a pipeline. Appends events to pipeline.events.

    This function is designed to be run as an asyncio.Task. It catches all
    exceptions and records them as error events on the pipeline.
    """
    try:
        pipeline.status = "running"
        await pipeline.append_event({"type": "status", "status": "running"})

        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        system_prompt = _load_system_prompt()
        tools = get_tool_definitions()

        messages = [
            {
                "role": "user",
                "content": _build_initial_message(
                    pipeline.file_paths, pipeline.metadata
                ),
            }
        ]

        step_index = 0

        for iteration in range(_MAX_ITERATIONS):
            try:
                response = await asyncio.wait_for(
                    client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=4096,
                        system=[
                            {
                                "type": "text",
                                "text": system_prompt,
                                "cache_control": {"type": "ephemeral"},
                            }
                        ],
                        tools=tools,
                        messages=messages,
                    ),
                    timeout=settings.pipeline_timeout_seconds,
                )
            except asyncio.TimeoutError:
                pipeline.status = "failed"
                pipeline.error = "Pipeline timed out"
                await pipeline.append_event({
                    "type": "error",
                    "message": "Pipeline timed out",
                    "recoverable": False,
                })
                return

            # Process response content blocks
            tool_results = []
            for block in response.content:
                if block.type == "text":
                    await pipeline.append_event({
                        "type": "reasoning",
                        "text": block.text,
                    })

                elif block.type == "tool_use":
                    await pipeline.append_event({
                        "type": "tool_start",
                        "tool": block.name,
                        "input": block.input,
                        "tool_use_id": block.id,
                        "step_index": step_index,
                    })

                    result = await execute_tool_with_fallback(
                        block.name, block.input, settings
                    )

                    await pipeline.append_event({
                        "type": "tool_result",
                        "tool": block.name,
                        "output": result["result"],
                        "source": result["source"],
                        "tool_use_id": block.id,
                        "step_index": step_index,
                    })

                    # Extract the final assessment from assess_creditworthiness
                    if block.name == "assess_creditworthiness" and result["source"] != "error":
                        pipeline.assessment = result["result"]

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result["result"]),
                    })

                    step_index += 1

            # Check if agent is done (end_turn or no more tool calls to process)
            if response.stop_reason == "end_turn" or not tool_results:
                pipeline.status = "completed"
                pipeline.completed_at = datetime.now(timezone.utc).isoformat()
                await pipeline.append_event({
                    "type": "complete",
                    "assessment": pipeline.assessment,
                })
                return

            # Append assistant response and tool results, continue loop
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        # Exhausted max iterations
        pipeline.status = "failed"
        pipeline.error = f"Exceeded maximum iterations ({_MAX_ITERATIONS})"
        await pipeline.append_event({
            "type": "error",
            "message": f"Exceeded maximum iterations ({_MAX_ITERATIONS})",
            "recoverable": False,
        })

    except Exception as exc:
        logger.exception("Agent runner failed for pipeline %s", pipeline.id)
        pipeline.status = "failed"
        pipeline.error = str(exc)
        await pipeline.append_event({
            "type": "error",
            "message": str(exc),
            "recoverable": False,
        })
