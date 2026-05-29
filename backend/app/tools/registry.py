"""Tool registry — collects all contract-review tool modules and provides dispatch.

To add a tool: implement a module exporting NAME, DEFINITION, and async execute(),
then import it and append it to _TOOL_MODULES below. Order here is the order the
tools are advertised to Claude.
"""

from app.config import Settings
from app.tools import (
    parse_contract_pdf,
    extract_clauses,
    evaluate_clause_risk,
    generate_review_memo,
)

_TOOL_MODULES = [
    parse_contract_pdf,
    extract_clauses,
    evaluate_clause_risk,
    generate_review_memo,
]

_TOOL_MAP = {mod.NAME: mod for mod in _TOOL_MODULES}


def get_tool_definitions() -> list[dict]:
    """Return Anthropic tool-use definitions for all tools (for the `tools` API param)."""
    return [mod.DEFINITION for mod in _TOOL_MODULES]


def get_tool_names() -> list[str]:
    """Return ordered list of tool names."""
    return [mod.NAME for mod in _TOOL_MODULES]


async def execute_tool(name: str, input_data: dict, settings: Settings) -> dict:
    """Dispatch a tool call by name."""
    module = _TOOL_MAP.get(name)
    if module is None:
        return {"error": f"Unknown tool: {name}"}
    return await module.execute(input_data, settings)
