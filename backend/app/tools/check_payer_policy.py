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
    """Deterministically evaluate the CPT policy criteria against the request.

    TODO (Step 8 — Build Tool 3):
      1. Read the procedure's CPT and look it up in `load_payer_policies()["policies"]`.
      2. If no policy exists, return {policy_found: False, meets_policy: False, ...}
         (route to manual review — do NOT auto-deny).
      3. For each criterion, resolve the value with `get_path(req, crit["path"])` and
         test it with `eval_criterion(actual, crit["op"], crit["value"])`.
      4. Return safe_json_serialize({policy_found, cpt_code, procedure, criteria[],
         criteria_met, criteria_total, meets_policy (= all met), unmet_criteria}).

    See tests/test_pa_tools.py::TestCheckPayerPolicy for the contract.
    """
    raise NotImplementedError("TODO (Step 8): implement check_payer_policy")
