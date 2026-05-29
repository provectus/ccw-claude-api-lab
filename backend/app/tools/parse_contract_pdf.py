"""Tool 1: Extract the full text of a contract PDF.

Primary method uses Claude's native PDF support (a `document` content block on the
Messages API — text + per-page vision, ZDR-eligible when your org has a ZDR
arrangement). Two optional local/cloud fallbacks (Docling, LlamaParse) are available
via the `method` argument and are imported lazily so they aren't required to install.
"""

from pathlib import Path

import anthropic

from app.config import Settings
from app.tools._common import pdf_to_base64, safe_json_serialize

NAME = "parse_contract_pdf"

_TRANSCRIBE_PROMPT = (
    "Transcribe the full text of this contract verbatim. Preserve section headings, "
    "numbering, and paragraph breaks. Do not summarize, comment, or omit anything — "
    "output only the contract text."
)

DEFINITION = {
    "name": NAME,
    "description": (
        "Extract the full text of a contract PDF. By default uses Claude's native PDF "
        "support (the Messages API `document` block — understands text, tables, and layout). "
        "Optional `method` values 'docling' or 'llamaparse' use local/cloud parsers instead. "
        "Returns the extracted text plus the method used. Use this as the first step."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Path to the contract PDF."},
            "method": {
                "type": "string",
                "enum": ["claude", "docling", "llamaparse"],
                "description": "Extraction backend. Default 'claude' (native PDF support).",
            },
        },
        "required": ["file_path"],
    },
}


async def _extract_with_claude(path: Path, settings: Settings) -> str:
    """Use Claude's native PDF support to transcribe the document."""
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_to_base64(path),
                        },
                    },
                    {"type": "text", "text": _TRANSCRIBE_PROMPT},
                ],
            }
        ],
    )
    return "".join(b.text for b in response.content if getattr(b, "type", None) == "text")


def _extract_with_docling(path: Path) -> str:
    """Local extraction via Docling (optional: `pip install docling`)."""
    try:
        from docling.document_converter import DocumentConverter
    except ImportError as exc:
        raise RuntimeError(
            "Docling is not installed. Install the optional parser with "
            "`uv pip install docling` to use method='docling'."
        ) from exc
    result = DocumentConverter().convert(str(path))
    return result.document.export_to_markdown()


def _extract_with_llamaparse(path: Path) -> str:
    """Cloud extraction via LlamaParse (optional: `pip install llama-parse`, needs LLAMA_CLOUD_API_KEY)."""
    try:
        from llama_parse import LlamaParse
    except ImportError as exc:
        raise RuntimeError(
            "LlamaParse is not installed. Install the optional parser with "
            "`uv pip install llama-parse` and set LLAMA_CLOUD_API_KEY to use method='llamaparse'."
        ) from exc
    docs = LlamaParse(result_type="markdown").load_data(str(path))
    return "\n\n".join(d.text for d in docs)


async def execute(input_data: dict, settings: Settings) -> dict:
    """Extract contract text via the chosen method (default: Claude native PDF)."""
    path = Path(input_data["file_path"])
    if not path.exists():
        return {"error": f"Contract PDF not found: {path}"}
    method = input_data.get("method", "claude")

    try:
        if method == "claude":
            text = await _extract_with_claude(path, settings)
        elif method == "docling":
            text = _extract_with_docling(path)
        elif method == "llamaparse":
            text = _extract_with_llamaparse(path)
        else:
            return {"error": f"Unknown method: {method}"}
    except Exception as exc:  # surface a clean tool error to the agent
        return {"error": f"{method} extraction failed: {exc}"}

    return safe_json_serialize({
        "text": text,
        "method": method,
        "char_count": len(text),
        "source_file": path.name,
    })
