"""
Research API endpoints
----------------------
Exposes the three-layer decision pipeline for the research paper demo.

GET  /api/v1/research/compare   — run all 4 decision modes on a sample applicant
POST /api/v1/research/decide    — run D1–D4 on a custom applicant profile
GET  /api/v1/research/info      — describe the decision modes and architecture
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.services.evidence_service import compute_evidence
from app.services.policy_service import evaluate_policy
from app.services.decision_service import make_decision, run_all_modes, DEFAULT_TAU

router = APIRouter(prefix="/research", tags=["research"])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ResearchApplicant(BaseModel):
    """Applicant profile for research comparison endpoint."""
    age: int = Field(28, ge=18, le=100, description="Applicant age")
    monthly_income: float = Field(18000.0, gt=0, description="Monthly income in ₹")
    history_months: int = Field(6, ge=1, le=12, description="Months of financial history available")
    aa_completeness: float = Field(0.3, ge=0.0, le=1.0, description="Account Aggregator data completeness (0–1)")
    uli_completeness: float = Field(0.5, ge=0.0, le=1.0, description="ULI data completeness (0–1)")
    default_probability: float = Field(0.12, ge=0.0, le=1.0, description="ML model default probability")
    occupation: Optional[str] = Field("delivery", description="Occupation type")
    decision_mode: Optional[str] = Field(None, description="Single mode to evaluate (default: all four)")


class ModeComparison(BaseModel):
    mode: str
    description: str
    decision: str
    reason_code: Optional[str]
    key_insight: str


class ComparisonResponse(BaseModel):
    applicant_summary: dict
    evidence: dict
    policy: dict
    modes: list
    research_note: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/info", summary="Describe the research architecture")
def get_research_info():
    """
    Returns a description of the four decision modes and the three-layer
    architecture used in the research paper.
    """
    return {
        "title": "Policy-Constrained Credit Decisioning with Evidence-Quality Gating",
        "layers": {
            "Layer 1 — Risk Model": (
                "XGBoost ML model outputs a calibrated probability of default (PD). "
                "Trained on Give Me Some Credit dataset. "
                "Threshold τ = 0.35 (approves ~70% of applicants in D1)."
            ),
            "Layer 2 — Evidence Quality": (
                "E = 0.5 × (history_months/12) + 0.25 × AA_completeness + 0.25 × ULI_completeness. "
                "E < 0.5 → INSUFFICIENT — routes to human review in D3/D4. "
                "Measures confidence in the PD estimate, NOT creditworthiness."
            ),
            "Layer 3 — Policy Rule Engine": (
                "Three-valued (Kleene) logic evaluation of JanSamarth/PMMY eligibility. "
                "States: SATISFIED | UNSATISFIED | UNRESOLVED. "
                "UNSATISFIED = hard decline in D2/D4. "
                "UNRESOLVED = route to review in D2/D4. "
                "NOTE: Rule criteria are PROVISIONAL (Task 10b required for verified rules)."
            ),
        },
        "decision_modes": {
            "D1": "ML Risk Model only — baseline",
            "D2": "ML + Policy Eligibility",
            "D3": "ML + Evidence Quality",
            "D4": "ML + Policy + Evidence (full system)",
        },
        "gating_logic": [
            "1. PD >= τ           → DECLINE  (PD_HIGH)",
            "2. D2/D4 + UNSAT     → DECLINE  (POLICY_INELIGIBLE)",
            "3. D2/D4 + UNRES     → REVIEW   (POLICY_UNRESOLVED)",
            "4. D3/D4 + INSUFF.   → REVIEW   (EVIDENCE_INSUFFICIENT)",
            "5. otherwise         → APPROVE",
        ],
        "tau": DEFAULT_TAU,
        "tau_e": 0.5,
    }


@router.get("/compare", response_model=ComparisonResponse, summary="Compare all 4 modes on a sample applicant")
def compare_modes_sample():
    """
    Runs all four decision modes on a fixed demo applicant and returns a
    side-by-side comparison. Useful for the research review presentation.
    """
    # Fixed demo applicant (matches the research paper example)
    applicant = ResearchApplicant()
    return _run_comparison(applicant)


@router.post("/compare", response_model=ComparisonResponse, summary="Compare all 4 modes on a custom applicant")
def compare_modes_custom(applicant: ResearchApplicant):
    """
    Runs all four decision modes on a custom applicant profile.
    Submit your own values to explore how the decision changes.
    """
    return _run_comparison(applicant)


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

MODE_DESCRIPTIONS = {
    "D1": "ML Risk Model only",
    "D2": "ML + Policy Eligibility",
    "D3": "ML + Evidence Quality",
    "D4": "ML + Policy + Evidence (full system)",
}

MODE_INSIGHTS = {
    "D1": "Baseline: ignores data quality and scheme eligibility",
    "D2": "Adds compliance check — flags scheme-ineligible applicants regardless of PD",
    "D3": "Flags thin-file applicants — short history means less reliable PD estimate",
    "D4": "Full system — most cautious; combines all three layers before auto-approving",
}


def _run_comparison(applicant: ResearchApplicant) -> ComparisonResponse:
    # Layer 2 — Evidence
    evidence = compute_evidence(
        history_months=applicant.history_months,
        aa_completeness=applicant.aa_completeness,
        uli_completeness=applicant.uli_completeness,
    )

    # Layer 3 — Policy
    annual_income = applicant.monthly_income * 12
    policy = evaluate_policy(
        age=float(applicant.age),
        annual_income=annual_income,
        occupation=applicant.occupation,
    )

    # Layer 4 — All decision modes
    all_results = run_all_modes(
        pd=applicant.default_probability,
        evidence=evidence,
        policy=policy,
        tau=DEFAULT_TAU,
    )

    modes = []
    for mode, result in all_results.items():
        modes.append({
            "mode": mode,
            "description": MODE_DESCRIPTIONS[mode],
            "decision": result["decision"],
            "reason_code": result["reason_code"],
            "key_insight": MODE_INSIGHTS[mode],
        })

    return ComparisonResponse(
        applicant_summary={
            "age": applicant.age,
            "monthly_income": f"₹{applicant.monthly_income:,.0f}",
            "annual_income": f"₹{annual_income:,.0f}",
            "history_months": applicant.history_months,
            "aa_completeness": applicant.aa_completeness,
            "uli_completeness": applicant.uli_completeness,
            "default_probability": applicant.default_probability,
            "occupation": applicant.occupation,
        },
        evidence=evidence.to_dict(),
        policy=policy.to_dict(),
        modes=modes,
        research_note=(
            "D4 shows the value of the full system: even when the ML model says low risk, "
            "the evidence gate flags insufficient data and routes to human review rather than "
            "auto-approving on thin evidence. Policy adds the compliance dimension independently."
        ),
    )
