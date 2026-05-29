"""Tool 2: Validate a canonical PA request against the structural/eligibility rules."""

import re

from app.config import Settings
from app.tools._common import load_criteria_rules, safe_json_serialize

NAME = "validate_clinical_criteria"

DEFINITION = {
    "name": NAME,
    "description": (
        "Validate a canonical PARequest against the structural and eligibility rules: valid "
        "5-digit CPT, valid ICD-10 codes, a 10-digit ordering-provider NPI, exactly one primary "
        "diagnosis, an in-range patient age and covered plan type, a valid place of service, and "
        "all required clinical fields present. Returns {valid, errors, warnings}. Run before "
        "checking payer policy — an incomplete request cannot be adjudicated."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "request": {
                "type": "object",
                "description": "Canonical PARequest produced by parse_pa_request",
            },
        },
        "required": ["request"],
    },
}


async def execute(input_data: dict, settings: Settings) -> dict:
    """Apply criteria_rules.json to the request."""
    req = input_data.get("request") or {}
    rules = load_criteria_rules()
    errors: list[str] = []
    warnings: list[str] = []

    patient = req.get("patient") or {}
    procedure = req.get("procedure") or {}
    diagnoses = req.get("diagnoses") or []
    provider = req.get("ordering_provider") or {}
    clinical = req.get("clinical") or {}

    # CPT format
    cpt = str(procedure.get("cpt_code", ""))
    if not re.match(rules["cpt_code"]["pattern"], cpt):
        errors.append(f"procedure.cpt_code '{cpt}' is not a valid 5-digit CPT code")

    # ICD-10 codes + primary diagnosis
    if not diagnoses:
        errors.append("no diagnoses provided")
    icd_pattern = rules["icd10_code"]["pattern"]
    for dx in diagnoses:
        code = str(dx.get("icd10_code", ""))
        if not re.match(icd_pattern, code):
            errors.append(f"diagnosis '{code}' is not a valid ICD-10 code")
    if rules["diagnoses"]["require_primary"]:
        primary_count = sum(1 for dx in diagnoses if dx.get("primary"))
        if primary_count != 1:
            errors.append(f"expected exactly one primary diagnosis, found {primary_count}")

    # NPI
    npi = str(provider.get("npi", ""))
    if not re.match(rules["npi"]["pattern"], npi):
        errors.append(f"ordering_provider.npi '{npi}' is not a valid 10-digit NPI")

    # Patient age + plan type
    age = patient.get("age")
    p_rule = rules["patient"]
    if age is None or not (p_rule["min_age"] <= age <= p_rule["max_age"]):
        errors.append(f"patient.age {age} is missing or out of range [{p_rule['min_age']}, {p_rule['max_age']}]")
    if patient.get("plan_type") not in p_rule["allowed_plan_types"]:
        errors.append(f"patient.plan_type '{patient.get('plan_type')}' is not a covered plan type")

    # Place of service
    pos = procedure.get("place_of_service")
    if pos not in rules["procedure"]["allowed_place_of_service"]:
        errors.append(f"procedure.place_of_service '{pos}' is not an allowed outpatient setting")

    # Required clinical fields
    for field in rules["clinical"]["required_fields"]:
        if clinical.get(field) is None:
            errors.append(f"clinical.{field} is missing")

    if not (req.get("clinical") or {}).get("notes"):
        warnings.append("no free-text clinical notes attached")

    return safe_json_serialize({
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checks_run": 6 + len(diagnoses),
    })
