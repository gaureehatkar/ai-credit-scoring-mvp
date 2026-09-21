"""
Decision Engine — D1 through D4
--------------------------------
Combines the ML risk model output, evidence quality score, and policy
eligibility state into a single credit decision.

Decision modes:
    D1 — ML Risk Model only
    D2 — ML + Policy Eligibility
    D3 — ML + Evidence Quality
    D4 — ML + Policy + Evidence  (full system)

Gating logic (precedence top → bottom):
    1. PD >= τ                              → DECLINE  (PD_HIGH)
    2. mode in {D2,D4} and policy UNSAT     → DECLINE  (POLICY_INELIGIBLE)
    3. mode in {D2,D4} and policy UNRES     → REVIEW   (POLICY_UNRESOLVED)
    4. mode in {D3,D4} and evidence INSUFF  → REVIEW   (EVIDENCE_INSUFFICIENT)
    5. otherwise                            → APPROVE

τ (default probability threshold): set so that D1 approves ~70% of applicants.
We use 0.35 as a reasonable default that can be tuned.
"""

from dataclasses import dataclass
from typing import Optional
from app.services.evidence_service import EvidenceResult
from app.services.policy_service import PolicyEvaluation, PolicyState

# Default PD threshold — can be overridden per request
DEFAULT_TAU = 0.35

# Decision outcomes
APPROVE = "APPROVE"
REVIEW  = "REVIEW"
DECLINE = "DECLINE"

# Reason codes
PD_HIGH               = "PD_HIGH"
POLICY_INELIGIBLE     = "POLICY_INELIGIBLE"
POLICY_UNRESOLVED     = "POLICY_UNRESOLVED"
EVIDENCE_INSUFFICIENT = "EVIDENCE_INSUFFICIENT"


@dataclass
class DecisionResult:
    mode: str           # "D1" | "D2" | "D3" | "D4"
    decision: str       # APPROVE | REVIEW | DECLINE
    reason_code: Optional[str]
    pd: float           # calibrated default probability
    tau: float          # threshold used
    evidence: Optional[EvidenceResult]
    policy: Optional[PolicyEvaluation]

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "decision": self.decision,
            "reason_code": self.reason_code,
            "pd": round(self.pd, 4),
            "tau": self.tau,
            "evidence": self.evidence.to_dict() if self.evidence else None,
            "policy": self.policy.to_dict() if self.policy else None,
        }


def make_decision(
    pd: float,
    mode: str,
    evidence: Optional[EvidenceResult] = None,
    policy: Optional[PolicyEvaluation] = None,
    tau: float = DEFAULT_TAU,
) -> DecisionResult:
    """
    Apply the gating function and return a DecisionResult.

    Parameters
    ----------
    pd       : float          — calibrated probability of default ∈ [0,1]
    mode     : str            — "D1" | "D2" | "D3" | "D4"
    evidence : EvidenceResult — required for D3 / D4
    policy   : PolicyEvaluation — required for D2 / D4
    tau      : float          — PD threshold (default 0.35)
    """
    mode = mode.upper()
    if mode not in {"D1", "D2", "D3", "D4"}:
        raise ValueError(f"Unknown decision mode: {mode}. Must be D1, D2, D3 or D4.")

    # Gate 1 — PD too high
    if pd >= tau:
        return DecisionResult(
            mode=mode, decision=DECLINE, reason_code=PD_HIGH,
            pd=pd, tau=tau, evidence=evidence, policy=policy,
        )

    # Gate 2 — Policy hard block (D2 / D4)
    if mode in {"D2", "D4"} and policy is not None:
        if policy.state == PolicyState.UNSATISFIED:
            return DecisionResult(
                mode=mode, decision=DECLINE, reason_code=POLICY_INELIGIBLE,
                pd=pd, tau=tau, evidence=evidence, policy=policy,
            )

    # Gate 3 — Policy unresolved → review (D2 / D4)
    if mode in {"D2", "D4"} and policy is not None:
        if policy.state == PolicyState.UNRESOLVED:
            return DecisionResult(
                mode=mode, decision=REVIEW, reason_code=POLICY_UNRESOLVED,
                pd=pd, tau=tau, evidence=evidence, policy=policy,
            )

    # Gate 4 — Evidence insufficient → review (D3 / D4)
    if mode in {"D3", "D4"} and evidence is not None:
        if evidence.status == "INSUFFICIENT":
            return DecisionResult(
                mode=mode, decision=REVIEW, reason_code=EVIDENCE_INSUFFICIENT,
                pd=pd, tau=tau, evidence=evidence, policy=policy,
            )

    # All gates passed → APPROVE
    return DecisionResult(
        mode=mode, decision=APPROVE, reason_code=None,
        pd=pd, tau=tau, evidence=evidence, policy=policy,
    )


def run_all_modes(
    pd: float,
    evidence: Optional[EvidenceResult] = None,
    policy: Optional[PolicyEvaluation] = None,
    tau: float = DEFAULT_TAU,
) -> dict:
    """
    Run all four decision modes for the same applicant.
    Useful for the research comparison endpoint.

    Returns a dict keyed by mode name.
    """
    results = {}
    for mode in ["D1", "D2", "D3", "D4"]:
        results[mode] = make_decision(
            pd=pd, mode=mode, evidence=evidence, policy=policy, tau=tau
        ).to_dict()
    return results
