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
    """Apply validation_rules.json to the application."""
    app_data = input_data.get("application") or {}
    rules = load_validation_rules()
    errors: list[str] = []
    warnings: list[str] = []

    # requested_amount bounds
    amount = app_data.get("requested_amount")
    amt_rule = rules["requested_amount"]
    if amount is None:
        errors.append("requested_amount is missing")
    elif amount < amt_rule["min"] or amount > amt_rule["max"]:
        errors.append(
            f"requested_amount {amount} outside allowed range "
            f"[{amt_rule['min']}, {amt_rule['max']}]"
        )

    # term in allowed set
    term = app_data.get("requested_term_months")
    if term not in rules["requested_term_months"]["allowed"]:
        errors.append(
            f"requested_term_months {term} not in allowed set "
            f"{rules['requested_term_months']['allowed']}"
        )

    # NAICS pattern
    naics = str(app_data.get("industry_naics", ""))
    if not re.match(rules["industry_naics"]["pattern"], naics):
        errors.append(f"industry_naics '{naics}' is not a valid 6-digit NAICS code")

    # financials completeness + balance-sheet identity
    fin_rule = rules["financials"]
    financials = app_data.get("financials") or []
    if len(financials) != fin_rule["required_years"]:
        errors.append(
            f"Expected {fin_rule['required_years']} years of financials, "
            f"got {len(financials)}"
        )

    tolerance = fin_rule["balance_sheet_tolerance_pct"] / 100.0
    for year in financials:
        fy = year.get("fiscal_year", "unknown")
        for field in fin_rule["non_null_fields"]:
            if year.get(field) is None:
                errors.append(f"FY{fy}: {field} is null or missing")

        ta = year.get("total_assets")
        tl = year.get("total_liabilities")
        eq = year.get("equity")
        if None not in (ta, tl, eq) and ta != 0:
            implied = tl + eq
            drift = abs(ta - implied) / abs(ta)
            if drift > tolerance:
                errors.append(
                    f"FY{fy}: balance sheet does not balance — "
                    f"assets {ta:.0f} vs liabilities+equity {implied:.0f} "
                    f"({drift * 100:.2f}% drift > {fin_rule['balance_sheet_tolerance_pct']}% tolerance)"
                )

        # soft warning: negative equity is a going-concern flag, not a hard stop
        if eq is not None and eq < 0:
            warnings.append(f"FY{fy}: negative equity ({eq:.0f}) — going-concern risk")

    # collateral sanity
    collateral = app_data.get("collateral")
    if collateral is not None:
        appraised = collateral.get("appraised_value")
        if appraised is None or appraised <= rules["collateral"]["min_appraised_value"]:
            warnings.append("collateral present but appraised_value is missing or non-positive")

    return safe_json_serialize({
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checks_run": 4 + len(financials),
    })
