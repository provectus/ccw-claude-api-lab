"""Tool 1: Parse a borrower loan package folder into a canonical LoanApplication."""

import json
from pathlib import Path

import pandas as pd

from app.config import Settings
from app.tools._common import safe_json_serialize

NAME = "parse_loan_package"

DEFINITION = {
    "name": NAME,
    "description": (
        "Parse a borrower loan-package folder into a canonical LoanApplication. The folder "
        "contains `profile.json` (borrower identity, requested amount/term, purpose, optional "
        "collateral) and `financials.csv` (one row per fiscal year with revenue, cogs, opex, "
        "ebitda, net_income, balance-sheet and working-capital fields). Returns the assembled "
        "application plus a list of parse warnings. Use this as the first step."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "folder_path": {
                "type": "string",
                "description": "Path to the loan-package folder containing profile.json and financials.csv",
            },
        },
        "required": ["folder_path"],
    },
}

_FINANCIAL_FIELDS = [
    "revenue",
    "cogs",
    "opex",
    "ebitda",
    "net_income",
    "total_assets",
    "total_liabilities",
    "equity",
    "cash",
    "accounts_receivable",
    "inventory",
    "current_assets",
    "current_liabilities",
]


async def execute(input_data: dict, settings: Settings) -> dict:
    """Read profile.json + financials.csv and assemble a LoanApplication dict.

    TODO (Step 6 — Build Tool 1):
      1. Resolve `input_data["folder_path"]` and confirm it exists.
      2. Read `profile.json` (json.loads) and `financials.csv` (pd.read_csv).
      3. Sort financials by `fiscal_year` and coerce each `_FINANCIAL_FIELDS`
         value to float, recording a warning for any missing field.
      4. Assemble the canonical LoanApplication dict (borrower_id, business_name,
         industry_naics, requested_amount, requested_term_months, purpose,
         financials[], optional collateral).
      5. Return safe_json_serialize({application, parse_warnings, years_parsed,
         source_folder}).

    See the `main` branch for the reference implementation, and the unit tests in
    tests/test_loan_tools.py::TestParseLoanPackage for the exact contract.
    """
    raise NotImplementedError("TODO (Step 6): implement parse_loan_package")
