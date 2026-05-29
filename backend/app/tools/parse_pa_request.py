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
    """Read request.json (+ clinical_notes.txt) and assemble a canonical PARequest.

    TODO (Step 6 — Build Tool 1):
      1. Resolve `input_data["folder_path"]`; confirm it exists and has request.json.
      2. Load request.json (json.loads). Warn for any missing `_REQUIRED_TOP` section.
      3. If `clinical_notes.txt` exists, merge its text into `request["clinical"]["notes"]`.
      4. Return safe_json_serialize({request, parse_warnings, cpt_code,
         diagnosis_count, source_folder}).

    See tests/test_pa_tools.py::TestParsePARequest for the exact contract; the
    reference implementation is on the `healthcare-solution` branch.
    """
    raise NotImplementedError("TODO (Step 6): implement parse_pa_request")
