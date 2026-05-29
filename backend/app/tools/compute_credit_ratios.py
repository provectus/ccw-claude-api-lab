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
    """Compute credit ratios. Pure arithmetic over the canonical financials."""
    app_data = input_data.get("application") or {}
    annual_rate = input_data.get("assumed_annual_rate", _DEFAULT_ANNUAL_RATE)

    financials = app_data.get("financials") or []
    if not financials:
        return {"error": "No financials present; cannot compute ratios"}

    # financials are oldest -> newest
    earliest = financials[0]
    latest = financials[-1]
    n_years = len(financials)

    requested_amount = app_data.get("requested_amount") or 0
    term_months = app_data.get("requested_term_months") or 0

    # DSCR — most recent EBITDA over annual debt service for the requested loan
    annual_debt_service = amortized_annual_debt_service(
        requested_amount, annual_rate, term_months
    )
    dscr = safe_div(latest.get("ebitda"), annual_debt_service)

    # Current ratio — current assets over current liabilities (latest year)
    current_ratio = safe_div(
        latest.get("current_assets"), latest.get("current_liabilities")
    )

    # Debt-to-equity (latest year)
    debt_to_equity = safe_div(
        latest.get("total_liabilities"), latest.get("equity")
    )

    # Gross margin per year + trend (percentage points, latest - earliest)
    gross_margins = []
    for year in financials:
        rev = year.get("revenue")
        cogs = year.get("cogs")
        gm = safe_div((rev - cogs) if None not in (rev, cogs) else None, rev)
        gross_margins.append({
            "fiscal_year": year.get("fiscal_year"),
            "gross_margin_pct": round(gm * 100, 2) if gm is not None else None,
        })
    gm_latest = gross_margins[-1]["gross_margin_pct"]
    gm_earliest = gross_margins[0]["gross_margin_pct"]
    gross_margin_trend_pp = (
        round(gm_latest - gm_earliest, 2)
        if None not in (gm_latest, gm_earliest)
        else None
    )

    # 3-year revenue CAGR
    rev_latest = latest.get("revenue")
    rev_earliest = earliest.get("revenue")
    revenue_cagr_3y = None
    if (
        rev_earliest not in (None, 0)
        and rev_latest is not None
        and rev_latest > 0
        and n_years > 1
    ):
        revenue_cagr_3y = round(
            ((rev_latest / rev_earliest) ** (1 / (n_years - 1)) - 1) * 100, 2
        )

    # LTV (if collateral)
    ltv = None
    collateral = app_data.get("collateral")
    if collateral and collateral.get("appraised_value"):
        ltv_ratio = safe_div(requested_amount, collateral["appraised_value"])
        ltv = round(ltv_ratio * 100, 2) if ltv_ratio is not None else None

    return safe_json_serialize({
        "dscr": round(dscr, 2) if dscr is not None else None,
        "current_ratio": round(current_ratio, 2) if current_ratio is not None else None,
        "debt_to_equity": round(debt_to_equity, 2) if debt_to_equity is not None else None,
        "gross_margin_by_year": gross_margins,
        "gross_margin_trend_pp": gross_margin_trend_pp,
        "revenue_cagr_3y_pct": revenue_cagr_3y,
        "ltv_pct": ltv,
        "inputs_used": {
            "assumed_annual_rate": annual_rate,
            "annual_debt_service": round(annual_debt_service, 2),
            "latest_fiscal_year": latest.get("fiscal_year"),
            "years_analyzed": n_years,
        },
    })
