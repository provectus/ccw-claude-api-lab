"""Tool 3: Compute credit ratios from a validated LoanApplication."""

from app.config import Settings
from app.tools._common import (
    amortized_annual_debt_service,
    safe_div,
    safe_json_serialize,
)

NAME = "compute_credit_ratios"

# Assumed pricing used to size debt service for the DSCR estimate. The agent may
# override via `assumed_annual_rate` once it has set indicative terms.
_DEFAULT_ANNUAL_RATE = 0.085

DEFINITION = {
    "name": NAME,
    "description": (
        "Compute the core commercial-credit ratios from a validated LoanApplication: DSCR "
        "(debt-service coverage on the most recent year's EBITDA against the amortized debt "
        "service for the requested loan), current ratio, debt-to-equity, gross margin per year "
        "and its trend, 3-year revenue CAGR, and LTV when collateral is present. Returns the "
        "ratios plus the intermediate values used. Run after validate_loan_application passes."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "application": {
                "type": "object",
                "description": "Validated canonical LoanApplication",
            },
            "assumed_annual_rate": {
                "type": "number",
                "description": "Optional annual interest rate (decimal, e.g. 0.085) used to size debt service. Defaults to 0.085.",
            },
        },
        "required": ["application"],
    },
}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Compute credit ratios. Pure arithmetic over the canonical financials.

    TODO (Step 8 — Build Tool 3):
      Compute, from the latest (and across all) financial years:
        - dscr            = latest EBITDA / amortized_annual_debt_service(
                              requested_amount, assumed_annual_rate, term_months)
        - current_ratio   = current_assets / current_liabilities (latest)
        - debt_to_equity  = total_liabilities / equity (latest)
        - gross margin per year + trend (latest minus earliest, in pp)
        - revenue_cagr_3y = (rev_latest / rev_earliest) ** (1/(n-1)) - 1
        - ltv             = requested_amount / collateral.appraised_value (if any)
      Use `safe_div` and `amortized_annual_debt_service` from _common. Return
      safe_json_serialize({dscr, current_ratio, debt_to_equity,
      gross_margin_by_year, gross_margin_trend_pp, revenue_cagr_3y_pct, ltv_pct,
      inputs_used}). Return {"error": ...} if no financials are present.

    See tests/test_loan_tools.py::TestComputeCreditRatios for the contract.
    """
    raise NotImplementedError("TODO (Step 8): implement compute_credit_ratios")
