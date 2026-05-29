"""Tool 3: Flag contract risk from the customer's perspective (deterministic)."""

from app.config import Settings
from app.tools._common import load_risk_rules, safe_json_serialize

NAME = "evaluate_clause_risk"

DEFINITION = {
    "name": NAME,
    "description": (
        "Evaluate a canonical contract for risk from the CUSTOMER's perspective and return a "
        "list of flags with severities (low / medium / high): the auto-renewal trap (auto-renews "
        "with a long notice window), a missing or weak liability cap, one-sided indemnification, "
        "no customer right to terminate for convenience, and any missing required clauses. "
        "Returns the flags plus an overall risk rating. Run after extract_clauses."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "contract": {"type": "object", "description": "Canonical contract from extract_clauses"},
        },
        "required": ["contract"],
    },
}

_RANK = {"low": 1, "medium": 2, "high": 3}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Apply the deterministic risk rules to the canonical contract."""
    contract = input_data.get("contract") or {}
    rules = load_risk_rules()
    flags: list[dict] = []

    def flag(clause: str, severity: str, message: str) -> None:
        flags.append({"clause": clause, "severity": severity, "message": message})

    # Auto-renewal trap
    ar = contract.get("auto_renewal") or {}
    if ar.get("present"):
        notice = ar.get("notice_days")
        threshold = rules["auto_renewal_notice_days_threshold"]
        if notice is not None and notice >= threshold:
            flag("auto_renewal", "high",
                 f"Auto-renews unless cancelled with {notice} days' notice (≥ {threshold}-day trap).")
        else:
            flag("auto_renewal", "medium", "Contract auto-renews; track the cancellation window.")

    # Liability cap
    liab = contract.get("liability_cap") or {}
    if not liab.get("present"):
        flag("liability_cap", "high", "No limitation-of-liability clause found.")
    elif liab.get("excludes_consequential"):
        flag("liability_cap", "low",
             "Liability cap excludes consequential damages — confirm carve-outs for IP/confidentiality.")

    # Indemnification
    ind = contract.get("indemnification") or {}
    if ind.get("present") and not ind.get("mutual"):
        flag("indemnification", "medium", "Indemnification is one-sided (not mutual) — favors the vendor.")
    elif not ind.get("present"):
        flag("indemnification", "medium", "No indemnification clause found.")

    # Termination
    term = contract.get("termination") or {}
    if not term.get("customer_for_convenience"):
        flag("termination", "medium", "Customer cannot terminate for convenience.")

    # Required clauses present?
    raw = contract.get("raw_clauses") or {}
    for clause in rules["required_clauses"]:
        present = clause in raw or (contract.get(clause) or {}).get("present")
        if not present:
            flag(clause, "medium", f"Required clause '{clause}' not found in the contract.")

    counts = {s: sum(1 for f in flags if f["severity"] == s) for s in ("low", "medium", "high")}
    overall = "none"
    if flags:
        overall = max((f["severity"] for f in flags), key=lambda s: _RANK[s])

    return safe_json_serialize({
        "flags": flags,
        "high_count": counts["high"],
        "medium_count": counts["medium"],
        "low_count": counts["low"],
        "overall_risk": overall,
    })
