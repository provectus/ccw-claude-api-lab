"""Tool 2: Extract canonical clauses from contract text (deterministic)."""

import re

from app.config import Settings
from app.tools._common import (
    extract_section,
    load_clause_patterns,
    safe_json_serialize,
)

NAME = "extract_clauses"

DEFINITION = {
    "name": NAME,
    "description": (
        "Extract the key clauses from contract text into the canonical contract structure: "
        "parties, term, auto-renewal (and its notice window), payment terms, limitation of "
        "liability, indemnification, IP assignment, termination, and governing law. Returns the "
        "structured contract plus which clauses were found vs. missing. Run after parse_contract_pdf."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Full contract text from parse_contract_pdf"},
        },
        "required": ["text"],
    },
}


def _contains(text: str | None, pattern: str) -> bool:
    return bool(text) and re.search(pattern, text, re.IGNORECASE) is not None


async def execute(input_data: dict, settings: Settings) -> dict:
    """Heuristically extract canonical clauses from the contract text."""
    text = input_data.get("text") or ""
    if not text.strip():
        return {"error": "No contract text provided"}

    patterns = load_clause_patterns()["clauses"]
    raw = {name: extract_section(text, kws) for name, kws in patterns.items()}

    # Parties: "by and between X and Y"
    parties: list[str] = []
    m = re.search(r"between\s+(.+?)\s+(?:and|&)\s+(.+?)(?:[\.,\n]|\s+\()", text, re.IGNORECASE)
    if m:
        parties = [m.group(1).strip(), m.group(2).strip()]

    # Term length
    term_text = raw.get("term") or ""
    term_months = None
    ty = re.search(r"(\d+)\s*year", term_text, re.IGNORECASE)
    tm = re.search(r"(\d+)\s*month", term_text, re.IGNORECASE)
    if ty:
        term_months = int(ty.group(1)) * 12
    elif tm:
        term_months = int(tm.group(1))

    # Auto-renewal
    ar_text = raw.get("auto_renewal") or raw.get("term") or ""
    ar_present = _contains(ar_text, r"automatically renew|auto.?renew")
    ar_notice = None
    if ar_present:
        nm = re.search(r"(\d+)\s*days", ar_text, re.IGNORECASE)
        ar_notice = int(nm.group(1)) if nm else None

    # Payment terms
    pay_text = raw.get("payment_terms") or ""
    net = re.search(r"net\s+(\d+)", pay_text, re.IGNORECASE)

    # Liability cap
    liab_text = raw.get("liability_cap") or ""
    liab_present = bool(liab_text)
    basis = None
    bm = re.search(r"(exceed|limited to|not exceed)[^.\n]{0,80}", liab_text, re.IGNORECASE)
    if bm:
        basis = bm.group(0).strip()

    # Indemnification
    ind_text = raw.get("indemnification") or ""
    ind_present = bool(ind_text)
    ind_mutual = _contains(ind_text, r"each party|mutually|both parties")

    # IP assignment
    ip_text = raw.get("ip_assignment") or ""
    assigns_to = None
    if ip_text:
        if _contains(ip_text, r"customer (?:shall own|owns|retains)"):
            assigns_to = "customer"
        elif _contains(ip_text, r"(?:vendor|provider|company) (?:shall own|owns|retains)"):
            assigns_to = "vendor"
        elif _contains(ip_text, r"each party"):
            assigns_to = "each_party"

    # Termination
    term2 = raw.get("termination") or ""
    cust_conv = _contains(term2, r"customer\s+may\s+terminate[^.]{0,80}for convenience")
    tn = re.search(r"(\d+)\s*days", term2, re.IGNORECASE)
    term_notice = int(tn.group(1)) if tn else None

    # Governing law
    gl_text = raw.get("governing_law") or ""
    glm = re.search(r"laws of (?:the )?(?:State of )?([A-Z][A-Za-z ]+?)[\.,\n]", gl_text)
    governing_law = glm.group(1).strip() if glm else None

    contract = {
        "parties": parties,
        "term_months": term_months,
        "governing_law": governing_law,
        "auto_renewal": {"present": ar_present, "notice_days": ar_notice},
        "payment_terms": {"net_days": int(net.group(1)) if net else None, "raw": pay_text[:200] or None},
        "liability_cap": {
            "present": liab_present,
            "basis": basis,
            "excludes_consequential": _contains(liab_text, r"consequential"),
        },
        "indemnification": {"present": ind_present, "mutual": ind_mutual},
        "ip_assignment": {"present": bool(ip_text), "assigns_to": assigns_to},
        "termination": {"customer_for_convenience": cust_conv, "notice_days": term_notice},
        "raw_clauses": {k: v for k, v in raw.items() if v},
    }

    found = [k for k, v in raw.items() if v]
    missing = [k for k, v in raw.items() if not v]
    return safe_json_serialize({
        "contract": contract,
        "clauses_found": found,
        "missing_clauses": missing,
    })
