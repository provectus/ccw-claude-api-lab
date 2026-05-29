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
    """Read profile.json + financials.csv and assemble a LoanApplication dict."""
    folder = Path(input_data["folder_path"])
    if not folder.exists() or not folder.is_dir():
        return {"error": f"Loan package folder not found: {folder}"}

    profile_path = folder / "profile.json"
    financials_path = folder / "financials.csv"
    warnings: list[str] = []

    if not profile_path.exists():
        return {"error": f"Missing profile.json in {folder}"}
    if not financials_path.exists():
        return {"error": f"Missing financials.csv in {folder}"}

    profile = json.loads(profile_path.read_text())

    df = pd.read_csv(financials_path)
    if "fiscal_year" in df.columns:
        df = df.sort_values("fiscal_year")

    financials: list[dict] = []
    for _, row in df.iterrows():
        year: dict = {"fiscal_year": int(row["fiscal_year"]) if "fiscal_year" in row else None}
        for field in _FINANCIAL_FIELDS:
            if field in row and pd.notna(row[field]):
                year[field] = float(row[field])
            else:
                year[field] = None
                warnings.append(
                    f"Missing {field} for fiscal_year {year['fiscal_year']}"
                )
        financials.append(year)

    application = {
        "borrower_id": profile.get("borrower_id"),
        "business_name": profile.get("business_name"),
        "industry_naics": str(profile.get("industry_naics", "")),
        "requested_amount": profile.get("requested_amount"),
        "requested_term_months": profile.get("requested_term_months"),
        "purpose": profile.get("purpose"),
        "financials": financials,
    }
    if profile.get("collateral"):
        application["collateral"] = profile["collateral"]

    return safe_json_serialize({
        "application": application,
        "parse_warnings": warnings,
        "years_parsed": len(financials),
        "source_folder": folder.name,
    })
