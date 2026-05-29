"""Tool 3: Evaluate the request's clinical facts against the payer's CPT policy."""

from app.config import Settings
from app.tools._common import (
    eval_criterion,
    get_path,
    load_payer_policies,
    safe_json_serialize,
)

NAME = "check_payer_policy"

DEFINITION = {
    "name": NAME,
    "description": (
        "Look up the procedure's CPT code in the payer medical-necessity policies and evaluate "
        "each policy criterion against the request's documented clinical facts. Returns the "
        "per-criterion breakdown (required, met, actual value) plus an overall meets_policy "
        "flag (true only when every criterion is met). If no policy exists for the CPT, returns "
        "policy_found=false. Run after validate_clinical_criteria passes."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "request": {
                "type": "object",
                "description": "Validated canonical PARequest",
            },
        },
        "required": ["request"],
    },
}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Deterministically evaluate the CPT policy criteria against the request."""
    req = input_data.get("request") or {}
    cpt = str((req.get("procedure") or {}).get("cpt_code", ""))
    policies = load_payer_policies()["policies"]

    policy = policies.get(cpt)
    if policy is None:
        return safe_json_serialize({
            "policy_found": False,
            "cpt_code": cpt,
            "meets_policy": False,
            "note": f"No medical-necessity policy on file for CPT {cpt}; route to manual clinical review.",
        })

    results = []
    for crit in policy["criteria"]:
        actual = get_path(req, crit["path"])
        met = eval_criterion(actual, crit["op"], crit["value"])
        results.append({
            "id": crit["id"],
            "name": crit["name"],
            "requirement": f"{crit['path']} {crit['op']} {crit['value']}",
            "actual": actual,
            "met": met,
        })

    met_count = sum(1 for r in results if r["met"])
    total = len(results)

    return safe_json_serialize({
        "policy_found": True,
        "cpt_code": cpt,
        "procedure": policy["description"],
        "criteria": results,
        "criteria_met": met_count,
        "criteria_total": total,
        "meets_policy": met_count == total,
        "unmet_criteria": [r["name"] for r in results if not r["met"]],
    })
