"""Tool 2: Validate a canonical PA request against the structural/eligibility rules."""

import re

from app.config import Settings
from app.tools._common import load_criteria_rules, safe_json_serialize

NAME = "validate_clinical_criteria"

DEFINITION = {
    "name": NAME,
    "description": (
        "Validate a canonical PARequest against the structural and eligibility rules: valid "
        "5-digit CPT, valid ICD-10 codes, a 10-digit ordering-provider NPI, exactly one primary "
        "diagnosis, an in-range patient age and covered plan type, a valid place of service, and "
        "all required clinical fields present. Returns {valid, errors, warnings}. Run before "
        "checking payer policy — an incomplete request cannot be adjudicated."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "request": {
                "type": "object",
                "description": "Canonical PARequest produced by parse_pa_request",
            },
        },
        "required": ["request"],
    },
}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Apply criteria_rules.json to the request.

    TODO (Step 7 — Build Tool 2):
      1. Load the rules: `rules = load_criteria_rules()`.
      2. Hard errors: invalid CPT (5-digit regex), invalid ICD-10 code(s), not exactly
         one primary diagnosis, invalid 10-digit NPI, out-of-range age, uncovered
         plan_type, disallowed place_of_service, and any missing required clinical field.
      3. Soft warning: no free-text clinical notes attached.
      4. Return safe_json_serialize({valid, errors, warnings, checks_run}).

    See tests/test_pa_tools.py::TestValidateClinicalCriteria for the contract.
    """
    raise NotImplementedError("TODO (Step 7): implement validate_clinical_criteria")
