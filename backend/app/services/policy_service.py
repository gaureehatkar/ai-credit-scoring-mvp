"""
Policy Rule Engine
------------------
Evaluates government scheme eligibility (JanSamarth / PMMY style) using
three-valued (Kleene) logic:

    SATISFIED   — all known conditions are met
    UNSATISFIED — at least one condition is known to be false
    UNRESOLVED  — a required attribute is missing and nothing is known false

This is the ENGINE FRAMEWORK (Task 10a).
All rule criteria below are PROVISIONAL / ILLUSTRATIVE — they are placeholder
values for the research demo and have NOT been verified against official
JanSamarth or PMMY documents.

In production these rules must be replaced with rules transcribed from
authoritative official sources with clause/page/version provenance.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Core types
# ---------------------------------------------------------------------------

class PolicyState(str, Enum):
    SATISFIED   = "SATISFIED"
    UNSATISFIED = "UNSATISFIED"
    UNRESOLVED  = "UNRESOLVED"


@dataclass
class RuleResult:
    rule_id: str
    condition: str
    state: PolicyState
    attribute_value: Optional[str] = None
    note: str = ""


@dataclass
class PolicyEvaluation:
    scheme: str                        # e.g. "JanSamarth" | "PMMY"
    state: PolicyState                 # combined Kleene result
    rule_results: list = field(default_factory=list)
    reason: str = ""
    provenance_note: str = (
        "PROVISIONAL — rules not verified against official documents. "
        "Task 10b required before freezing policy-rule dataset."
    )

    def to_dict(self) -> dict:
        return {
            "scheme": self.scheme,
            "state": self.state.value,
            "reason": self.reason,
            "rule_results": [
                {
                    "rule_id": r.rule_id,
                    "condition": r.condition,
                    "state": r.state.value,
                    "attribute_value": r.attribute_value,
                    "note": r.note,
                }
                for r in self.rule_results
            ],
            "provenance_note": self.provenance_note,
        }


# ---------------------------------------------------------------------------
# Kleene three-valued logic helpers
# ---------------------------------------------------------------------------

def kleene_and(states: list) -> PolicyState:
    """
    Kleene AND over a list of PolicyState values.
    Any UNSATISFIED → UNSATISFIED
    Any UNRESOLVED (and none UNSATISFIED) → UNRESOLVED
    All SATISFIED → SATISFIED
    """
    if PolicyState.UNSATISFIED in states:
        return PolicyState.UNSATISFIED
    if PolicyState.UNRESOLVED in states:
        return PolicyState.UNRESOLVED
    return PolicyState.SATISFIED


def kleene_or(states: list) -> PolicyState:
    """
    Kleene OR.
    Any SATISFIED → SATISFIED
    Any UNRESOLVED (and none SATISFIED) → UNRESOLVED
    All UNSATISFIED → UNSATISFIED
    """
    if PolicyState.SATISFIED in states:
        return PolicyState.SATISFIED
    if PolicyState.UNRESOLVED in states:
        return PolicyState.UNRESOLVED
    return PolicyState.UNSATISFIED


# ---------------------------------------------------------------------------
# Individual rule evaluators (PROVISIONAL criteria)
# ---------------------------------------------------------------------------

def _eval_age(age: Optional[float]) -> RuleResult:
    """
    PROVISIONAL: age between 18 and 60.
    UNVERIFIED — must be replaced with verified official source (Task 10b).
    """
    if age is None:
        return RuleResult(
            rule_id="AGE_CHECK",
            condition="18 <= age <= 60 [PROVISIONAL/UNVERIFIED]",
            state=PolicyState.UNRESOLVED,
            note="Age not provided — attribute missing",
        )
    val = float(age)
    if 18 <= val <= 60:
        return RuleResult(
            rule_id="AGE_CHECK",
            condition="18 <= age <= 60 [PROVISIONAL/UNVERIFIED]",
            state=PolicyState.SATISFIED,
            attribute_value=str(val),
        )
    return RuleResult(
        rule_id="AGE_CHECK",
        condition="18 <= age <= 60 [PROVISIONAL/UNVERIFIED]",
        state=PolicyState.UNSATISFIED,
        attribute_value=str(val),
        note="Age outside eligible range",
    )


def _eval_income(annual_income: Optional[float]) -> RuleResult:
    """
    PROVISIONAL: annual income <= ₹10,00,000 (₹10 lakh).
    UNVERIFIED — must be replaced with verified official source (Task 10b).
    """
    INCOME_CAP = 1_000_000  # ₹10 lakh — UNVERIFIED
    if annual_income is None:
        return RuleResult(
            rule_id="INCOME_CAP",
            condition=f"annual_income <= ₹{INCOME_CAP:,} [PROVISIONAL/UNVERIFIED]",
            state=PolicyState.UNRESOLVED,
            note="Income not provided",
        )
    if annual_income <= INCOME_CAP:
        return RuleResult(
            rule_id="INCOME_CAP",
            condition=f"annual_income <= ₹{INCOME_CAP:,} [PROVISIONAL/UNVERIFIED]",
            state=PolicyState.SATISFIED,
            attribute_value=f"₹{annual_income:,.0f}",
        )
    return RuleResult(
        rule_id="INCOME_CAP",
        condition=f"annual_income <= ₹{INCOME_CAP:,} [PROVISIONAL/UNVERIFIED]",
        state=PolicyState.UNSATISFIED,
        attribute_value=f"₹{annual_income:,.0f}",
        note="Income exceeds cap",
    )


def _eval_occupation(occupation: Optional[str]) -> RuleResult:
    """
    PROVISIONAL: occupation must be a non-farm gig/micro-enterprise category.
    UNVERIFIED — must be replaced with verified official source (Task 10b).
    """
    ELIGIBLE_OCCUPATIONS = {
        "delivery", "ride_hailing", "freelance_services",
        "retail_micro", "gig_worker", "self_employed",
        # applicant_type mappings
        "underbanked", "unbanked",
    }
    if occupation is None:
        return RuleResult(
            rule_id="OCCUPATION_CHECK",
            condition="occupation in eligible categories [PROVISIONAL/UNVERIFIED]",
            state=PolicyState.UNRESOLVED,
            note="Occupation not provided",
        )
    occ_lower = occupation.lower().strip()
    if occ_lower in ELIGIBLE_OCCUPATIONS:
        return RuleResult(
            rule_id="OCCUPATION_CHECK",
            condition="occupation in eligible categories [PROVISIONAL/UNVERIFIED]",
            state=PolicyState.SATISFIED,
            attribute_value=occupation,
        )
    return RuleResult(
        rule_id="OCCUPATION_CHECK",
        condition="occupation in eligible categories [PROVISIONAL/UNVERIFIED]",
        state=PolicyState.UNSATISFIED,
        attribute_value=occupation,
        note="Occupation not in eligible list",
    )


# ---------------------------------------------------------------------------
# Scheme evaluators
# ---------------------------------------------------------------------------

def evaluate_jan_samarth(
    age: Optional[float],
    annual_income: Optional[float],
    occupation: Optional[str],
) -> PolicyEvaluation:
    """
    Evaluate JanSamarth scheme eligibility.
    All criteria are PROVISIONAL/UNVERIFIED until Task 10b is complete.
    """
    age_result  = _eval_age(age)
    inc_result  = _eval_income(annual_income)
    occ_result  = _eval_occupation(occupation)

    rules = [age_result, inc_result, occ_result]
    combined = kleene_and([r.state for r in rules])

    reason_map = {
        PolicyState.SATISFIED:   "All known JanSamarth eligibility criteria met",
        PolicyState.UNSATISFIED: next(
            (r.note for r in rules if r.state == PolicyState.UNSATISFIED), "Ineligible"
        ),
        PolicyState.UNRESOLVED:  "One or more required attributes missing — cannot determine eligibility",
    }

    return PolicyEvaluation(
        scheme="JanSamarth",
        state=combined,
        rule_results=rules,
        reason=reason_map[combined],
    )


def evaluate_pmmy(
    age: Optional[float],
    annual_income: Optional[float],
    occupation: Optional[str],
) -> PolicyEvaluation:
    """
    Evaluate PMMY (Pradhan Mantri Mudra Yojana) eligibility.
    All criteria are PROVISIONAL/UNVERIFIED until Task 10b is complete.
    """
    age_result = _eval_age(age)
    inc_result = _eval_income(annual_income)
    occ_result = _eval_occupation(occupation)

    rules = [age_result, inc_result, occ_result]
    combined = kleene_and([r.state for r in rules])

    reason_map = {
        PolicyState.SATISFIED:   "All known PMMY eligibility criteria met",
        PolicyState.UNSATISFIED: next(
            (r.note for r in rules if r.state == PolicyState.UNSATISFIED), "Ineligible"
        ),
        PolicyState.UNRESOLVED:  "One or more required attributes missing",
    }

    return PolicyEvaluation(
        scheme="PMMY",
        state=combined,
        rule_results=rules,
        reason=reason_map[combined],
    )


def evaluate_policy(
    age: Optional[float],
    annual_income: Optional[float],
    occupation: Optional[str],
    scheme_mode: str = "any",
) -> PolicyEvaluation:
    """
    Evaluate scheme eligibility and combine results.

    scheme_mode:
        "any"          — Kleene OR over JanSamarth and PMMY (default)
        "jan_samarth"  — JanSamarth only
        "pmmy"         — PMMY only
    """
    js = evaluate_jan_samarth(age, annual_income, occupation)
    pm = evaluate_pmmy(age, annual_income, occupation)

    if scheme_mode == "jan_samarth":
        return js
    if scheme_mode == "pmmy":
        return pm

    # Default: "any" — Kleene OR (eligible under either scheme)
    combined_state = kleene_or([js.state, pm.state])

    # Pick the more informative reason
    if combined_state == PolicyState.SATISFIED:
        winning = js if js.state == PolicyState.SATISFIED else pm
        reason = f"Eligible under {winning.scheme}: {winning.reason}"
    elif combined_state == PolicyState.UNSATISFIED:
        reason = f"Ineligible under both schemes. JanSamarth: {js.reason} | PMMY: {pm.reason}"
    else:
        reason = "Eligibility unresolved — missing attributes"

    return PolicyEvaluation(
        scheme="JanSamarth OR PMMY",
        state=combined_state,
        rule_results=js.rule_results + pm.rule_results,
        reason=reason,
    )


def derive_policy_inputs(
    age: int,
    alternative_data: dict,
    applicant_type: str,
    monthly_income: Optional[float] = None,
) -> dict:
    """
    Extract the policy engine's input attributes from the application form data.

    Returns dict with: age, annual_income, occupation
    """
    # Annual income: 12 × mean monthly income
    income = monthly_income or float(alternative_data.get("monthly_income") or 0)
    annual_income = income * 12 if income > 0 else None

    # Occupation: derive from applicant type + employment_type field
    employment_type = alternative_data.get("employment_type")
    if employment_type:
        occupation = employment_type.lower().strip()
    else:
        # Fall back to applicant_type as a broad category
        occupation = applicant_type

    return {
        "age": float(age),
        "annual_income": annual_income,
        "occupation": occupation,
    }
