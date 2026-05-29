"""Tool 2: Validate a canonical LoanApplication against the validation rules."""

import re

from app.config import Settings
from app.tools._common import load_validation_rules, safe_json_serialize

NAME = "validate_loan_application"

DEFINITION = {
    "name": NAME,
    "description": (
        "Validate a canonical LoanApplication against the loan validation rules: requested "
        "amount within policy bounds, standard term length, valid 6-digit NAICS code, three "
        "complete years of non-null financials, and the balance-sheet identity "
        "(total_assets ~= total_liabilities + equity) within tolerance. Returns a structured "
        "result with `valid`, hard `errors`, and soft `warnings`. Run this before computing ratios."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "application": {
                "type": "object",
                "description": "Canonical LoanApplication produced by parse_loan_package",
            },
        },
        "required": ["application"],
    },
}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Apply validation_rules.json to the application.

    TODO (Step 7 — Build Tool 2):
      1. Load the rules with `load_validation_rules()`.
      2. Check `requested_amount` against min/max, `requested_term_months` against
         the allowed set, and `industry_naics` against the regex pattern.
      3. Check the financials: exactly `required_years` entries, every
         `non_null_fields` value present, and the balance-sheet identity
         (total_assets ~= total_liabilities + equity) within tolerance.
      4. Treat negative equity / questionable collateral as soft `warnings`.
      5. Return safe_json_serialize({valid, errors, warnings, checks_run}).

    See tests/test_loan_tools.py::TestValidateLoanApplication for the contract.
    """
    raise NotImplementedError("TODO (Step 7): implement validate_loan_application")
