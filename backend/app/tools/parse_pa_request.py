"""Tool 1: Parse a prior-authorization request folder into a canonical PARequest."""

import json
from pathlib import Path

from app.config import Settings
from app.tools._common import safe_json_serialize

NAME = "parse_pa_request"

DEFINITION = {
    "name": NAME,
    "description": (
        "Parse a prior-authorization request folder into a canonical PARequest. The folder "
        "contains `request.json` (patient, procedure CPT, diagnoses, ordering provider, and "
        "structured clinical facts) and an optional `clinical_notes.txt` (free-text notes that "
        "are merged into clinical.notes). Returns the assembled request plus a list of parse "
        "warnings. Use this as the first step."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "folder_path": {
                "type": "string",
                "description": "Path to the PA request folder containing request.json (and optional clinical_notes.txt)",
            },
        },
        "required": ["folder_path"],
    },
}

_REQUIRED_TOP = ["request_id", "patient", "procedure", "diagnoses", "ordering_provider", "clinical"]


async def execute(input_data: dict, settings: Settings) -> dict:
    """Read request.json (+ clinical_notes.txt) and assemble a canonical PARequest."""
    folder = Path(input_data["folder_path"])
    if not folder.exists() or not folder.is_dir():
        return {"error": f"PA request folder not found: {folder}"}

    request_path = folder / "request.json"
    if not request_path.exists():
        return {"error": f"Missing request.json in {folder}"}

    request = json.loads(request_path.read_text())
    warnings: list[str] = []

    for key in _REQUIRED_TOP:
        if key not in request:
            warnings.append(f"Missing top-level section: {key}")

    # Merge free-text clinical notes if present.
    notes_path = folder / "clinical_notes.txt"
    if notes_path.exists():
        notes = notes_path.read_text().strip()
        request.setdefault("clinical", {})
        existing = request["clinical"].get("notes", "")
        request["clinical"]["notes"] = (existing + "\n" + notes).strip() if existing else notes
    else:
        warnings.append("No clinical_notes.txt found; proceeding with structured fields only")

    cpt = request.get("procedure", {}).get("cpt_code")

    return safe_json_serialize({
        "request": request,
        "parse_warnings": warnings,
        "cpt_code": cpt,
        "diagnosis_count": len(request.get("diagnoses", [])),
        "source_folder": folder.name,
    })
